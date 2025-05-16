import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Scrollbar
import subprocess
import os
import datetime
import json
import threading
import time
from resplado_automatico import RespaldoAutomatico
from utileria import respaldo_auto
 



class ModuloRespaldo:
    def __init__(self, ventana_padre=None, id_usuario=None):
        self.id_usuario = id_usuario
        self.directorio = "respaldos"
        self.respaldo_auto = respaldo_auto


        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Respaldos - Lavandería")
        self.ventana.geometry("800x650")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            from utileria import centrar_ventana  # Asegúrate de importar centrar_ventana
            centrar_ventana(self.ventana, 800, 650)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        self.construir_interfaz()
        self.actualizar_estado_botones_respaldo()


        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE RESPALDOS",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        ttk.Separator(self.frame_principal, orient="horizontal").pack(fill=tk.X, pady=(0, 20))

        # Botón para generar respaldo
        btn_respaldo = tk.Button(
            self.frame_principal,
            text="Generar respaldo completo",
            bg="#3a7ff6",
            fg="white",
            font=("Helvetica", 11, "bold"),
            command=self.generar_respaldo
        )
        btn_respaldo.pack(pady=10)


       # --- Frame de configuración de respaldo automático ---
        frame_auto = tk.LabelFrame(self.frame_principal, text="Respaldo automático", bg="#f5f5f5", font=("Helvetica", 10, "bold"))
        frame_auto.pack(pady=10, fill=tk.X)

        # Variable para almacenar el intervalo
        self.intervalo_respaldo = tk.StringVar()

        # Menú desplegable para elegir intervalo
        opciones = ["Cada hora", "Cada día", "Cada semana", "Cada mes"]
        self.combo_intervalo = ttk.Combobox(frame_auto, textvariable=self.intervalo_respaldo, values=opciones, state="readonly", width=20)
        self.combo_intervalo.pack(side=tk.LEFT, padx=10)

        # Leer configuración guardada
        try:
            with open("config_respaldo.json", "r") as f:
                config = json.load(f)
                self.combo_intervalo.set(config.get("intervalo", "Cada día"))
        except:
            self.combo_intervalo.set("Cada día")

       # Botón para activar respaldo automático
        self.btn_toggle_auto = tk.Button(
            frame_auto,
            text="Iniciar respaldo automático",
            bg="#3a7ff6",
            fg="white",
            font=("Helvetica", 10),
            command=self.iniciar_respaldo_automatico
        )
        self.btn_toggle_auto.pack(side=tk.LEFT, padx=10)

        # Botón para detener respaldo automático
        self.btn_detener_auto = tk.Button(
            frame_auto,
            text="Detener respaldo automático",
            bg="#e53935",
            fg="white",
            font=("Helvetica", 10),
            command=self.detener_respaldo_automatico
        )
        self.btn_detener_auto.pack(side=tk.LEFT, padx=10)


        # --- Etiqueta de estado dinámico del respaldo ---
        self.label_estado_respaldo = tk.Label(
            self.frame_principal,
            text="",  # Se actualizará dinámicamente
            bg="#f5f5f5",
            fg="#00796b",
            font=("Helvetica", 10, "italic")
        )
        self.label_estado_respaldo.pack(pady=(0, 10))
    

        # --- Frame para tabla con scrollbar ---
        frame_tabla_scroll = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_tabla_scroll.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tabla_scroll, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview con dos columnas
        self.tabla_respaldo = ttk.Treeview(
            frame_tabla_scroll,
            columns=("archivo", "fecha"),
            show="headings",
            height=10,
            yscrollcommand=scrollbar.set
        )

        # Configurar encabezados y columnas
        self.tabla_respaldo.heading("archivo", text="Nombre del Archivo")
        self.tabla_respaldo.heading("fecha", text="Fecha y Hora")
        self.tabla_respaldo.column("archivo", width=400, anchor=tk.W)
        self.tabla_respaldo.column("fecha", width=150, anchor=tk.CENTER)

        # Asociar scrollbar al Treeview
        scrollbar.config(command=self.tabla_respaldo.yview)

        self.tabla_respaldo.pack(fill=tk.BOTH, expand=True)

        # Separador visual entre tabla y botones
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 10))


        # ---- Frame Botones---
        frame_botones = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        btn_ver = tk.Button(
            frame_botones,
            text="Ver Carpeta",
            bg="#3a7ff6",
            fg="white",
            command=self.abrir_carpeta
        )
        btn_ver.pack(side=tk.LEFT, padx=5)

        btn_eliminar = tk.Button(
            frame_botones,
            text="Eliminar",
            bg="#e53935",
            fg="white",
            command=self.eliminar_respaldo
        )
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        btn_restaurar = tk.Button(
            frame_botones,
            text="Restaurar",
            bg="#3a7ff6",
            fg="white",
            command=self.restaurar_respaldo
        )
        btn_restaurar.pack(side=tk.LEFT, padx=5)



        self.actualizar_lista()

    def generar_respaldo(self):

        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"respaldo_bd_{fecha}.sql"
        carpeta_respaldos = "respaldos"
        ruta_archivo = os.path.join(carpeta_respaldos, nombre_archivo)

        try:
            # Leer configuración desde config.json
            with open("config.json", "r") as f:
                config = json.load(f)

            usuario = config["user"]
            password = config["password"]
            base_datos = config["database"]
            host = config.get("host", "localhost")

            # Crear carpeta si no existe
            os.makedirs(carpeta_respaldos, exist_ok=True)

            # Comando mysqldump
            comando = [
                "mysqldump",
                f"-h{host}",
                f"-u{usuario}",
                f"-p{password}",
                base_datos
            ]

            # Ejecutar respaldo
            with open(ruta_archivo, "w", encoding="utf-8") as salida:
                subprocess.run(comando, stdout=salida, check=True)

            messagebox.showinfo("Respaldo creado", f"Archivo guardado en:\n{ruta_archivo}")
            self.actualizar_lista()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el respaldo:\n{e}")


    def actualizar_lista(self):
        """Actualiza la lista de archivos de respaldo"""
        self.tabla_respaldo.delete(*self.tabla_respaldo.get_children())
        for archivo in os.listdir("respaldos"):
            if archivo.endswith(".sql"):
                ruta = os.path.join("respaldos", archivo)
                # Extraer fecha desde el nombre: respaldo_bd_YYYYMMDD_HHMMSS.sql
                try:
                    partes = archivo.replace("respaldo_bd_", "").replace(".sql", "").split("_")
                    fecha_formateada = datetime.datetime.strptime(partes[0] + partes[1], "%Y%m%d%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
                except:
                    fecha_formateada = "Fecha no válida"

                self.tabla_respaldo.insert("", tk.END, values=(archivo, fecha_formateada))



    def abrir_carpeta(self):
        ruta = os.path.join(os.getcwd(), "respaldos")

        if not os.path.exists(ruta):
            os.makedirs(ruta)  # Crear la carpeta si no existe

        try:
            os.startfile(ruta)  # Solo funciona en Windows
        except AttributeError:
            # Para sistemas como Linux o macOS
            import subprocess
            subprocess.run(["xdg-open", ruta])


    def eliminar_respaldo(self):
        seleccion = self.tabla_respaldo.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un respaldo para eliminar.")
            return

        archivo = self.tabla_respaldo.item(seleccion[0], "values")[0]

        confirmacion = messagebox.askyesno("Eliminar", f"¿Deseas eliminar el respaldo '{archivo}'?")
        if confirmacion:
            try:
                os.remove(os.path.join(self.directorio, archivo))
                self.actualizar_lista()
                messagebox.showinfo("Eliminado", f"Respaldo '{archivo}' eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el respaldo:\n{e}")


    def restaurar_respaldo(self):
        seleccion = self.tabla_respaldo.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un respaldo para restaurar.")
            return

        archivo = self.tabla_respaldo.item(seleccion[0], "values")[0]
        ruta_respaldo = os.path.join("respaldos", archivo)

        if not os.path.exists(ruta_respaldo):
            messagebox.showerror("Error", "El archivo de respaldo no existe.")
            return

        confirmacion = messagebox.askyesno("Confirmar restauración",
                                        "Esto sobrescribirá la base de datos actual.\n¿Deseas continuar?")
        if not confirmacion:
            return

        try:
            with open("config.json", "r") as f:
                config = json.load(f)

            usuario = config["user"]
            password = config["password"]
            base_datos = config["database"]

            comando = f'mysql -u {usuario} -p{password} {base_datos} < "{ruta_respaldo}"'
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

            if resultado.returncode == 0:
                messagebox.showinfo("Restauración completa", "La base de datos fue restaurada correctamente.")
            else:
                messagebox.showerror("Error al restaurar", f"Ocurrió un error:\n{resultado.stderr}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar el respaldo:\n{str(e)}")


    def toggle_respaldo_automatico(self):
        if not self.ejecutando_respaldo:
            self.ejecutando_respaldo = True
            self.hilo_respaldo = threading.Thread(target=self.respaldo_automatico, daemon=True)
            self.hilo_respaldo.start()
            messagebox.showinfo("Automático", "Respaldo automático iniciado.")
        else:
            self.ejecutando_respaldo = False
            messagebox.showinfo("Automático", "Respaldo automático detenido.")

    def respaldo_automatico(self):
        while self.ejecutando_respaldo:
            intervalo = self.obtener_segundos_intervalo()

            # Esperar ese intervalo
            for _ in range(intervalo):
                if not self.ejecutando_respaldo:
                    return
                time.sleep(1)

            # Ejecutar respaldo
            try:
                self.generar_respaldo()
            except Exception as e:
                print(f"Error durante respaldo automático: {e}")

    def obtener_segundos_intervalo(self):
        seleccion = self.intervalo_respaldo.get()
        if seleccion == "Cada hora":
            return 60
        elif seleccion == "Cada día":
            return 86400
        elif seleccion == "Cada semana":
            return 604800
        elif seleccion == "Cada mes":
            return 2592000  # 30 días aprox
        else:
            return 86400  # Por defecto: un día
        
    def actualizar_estado_botones_respaldo(self):
        try:
            with open("config_respaldo.json", "r") as f:
                config = json.load(f)
                intervalo = config.get("intervalo", "")
                if intervalo:
                    self.btn_toggle_auto.config(state=tk.DISABLED)
                    self.btn_detener_auto.config(state=tk.NORMAL)
                    self.combo_intervalo.set(intervalo)
                    self.label_estado_respaldo.config(
                        text=f"🟢 Respaldo automático activo ({intervalo.lower()})"
                    )
                else:
                    self.btn_toggle_auto.config(state=tk.NORMAL)
                    self.btn_detener_auto.config(state=tk.DISABLED)
                    self.label_estado_respaldo.config(
                        text="🔴 Respaldo automático desactivado"
                    )
        except Exception as e:
            self.label_estado_respaldo.config(text="⚠️ Estado desconocido del respaldo automático")
            print(f"[ERROR] No se pudo actualizar el estado del respaldo: {e}")


    def iniciar_respaldo_automatico(self):
        intervalo = self.combo_intervalo.get()
        self.respaldo_auto.configurar_intervalo(intervalo)
        self.respaldo_auto.iniciar()
        messagebox.showinfo("Respaldo automático", f"Respaldo automático iniciado ({intervalo}).")
        self.actualizar_estado_botones_respaldo()

    def detener_respaldo_automatico(self):
        self.respaldo_auto.detener()
        messagebox.showinfo("Respaldo automático", "Respaldo automático desactivado.")
        self.actualizar_estado_botones_respaldo()







