import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Scrollbar
import subprocess
import os
import datetime
import json
import threading
import time
from resplado_automatico import RespaldoAutomatico
from utileria import centrar_ventana


class ModuloRespaldo:
    def __init__(self, ventana_padre=None, id_usuario=None):
        self.id_usuario = id_usuario
        self.directorio = "respaldos"
        self.respaldo_auto = RespaldoAutomatico()

        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Respaldos - Lavandería")
        self.ventana.geometry("800x650")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            centrar_ventana(self.ventana, 800, 650)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Crear directorio de respaldos si no existe
        os.makedirs(self.directorio, exist_ok=True)

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
            text="💾 Generar respaldo completo",
            bg="#4caf50",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=25,
            height=2,
            cursor="hand2",
            command=self.generar_respaldo
        )
        btn_respaldo.pack(pady=10)

        # Frame de configuración de respaldo automático
        frame_auto = tk.LabelFrame(
            self.frame_principal,
            text="⚙️ Respaldo automático",
            bg="#f5f5f5",
            font=("Helvetica", 10, "bold"),
            padx=10,
            pady=10
        )
        frame_auto.pack(pady=15, fill=tk.X)

        # Frame interno para organizar los controles
        frame_controles = tk.Frame(frame_auto, bg="#f5f5f5")
        frame_controles.pack(fill=tk.X)

        # Variable para almacenar el intervalo
        self.intervalo_respaldo = tk.StringVar()

        # Etiqueta y menú desplegable para elegir intervalo
        tk.Label(
            frame_controles,
            text="Frecuencia:",
            bg="#f5f5f5",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        opciones = ["Cada hora", "Cada día", "Cada semana", "Cada mes"]
        self.combo_intervalo = ttk.Combobox(
            frame_controles,
            textvariable=self.intervalo_respaldo,
            values=opciones,
            state="readonly",
            width=15
        )
        self.combo_intervalo.pack(side=tk.LEFT, padx=5)

        # Leer configuración guardada
        self.cargar_configuracion_respaldo()

        # Frame para botones
        frame_botones_auto = tk.Frame(frame_controles, bg="#f5f5f5")
        frame_botones_auto.pack(side=tk.RIGHT, padx=10)

        # Botón para activar respaldo automático
        self.btn_toggle_auto = tk.Button(
            frame_botones_auto,
            text="▶️ Iniciar",
            bg="#4caf50",
            fg="white",
            font=("Helvetica", 10),
            width=10,
            cursor="hand2",
            command=self.iniciar_respaldo_automatico
        )
        self.btn_toggle_auto.pack(side=tk.LEFT, padx=2)

        # Botón para detener respaldo automático
        self.btn_detener_auto = tk.Button(
            frame_botones_auto,
            text="⏹️ Detener",
            bg="#f44336",
            fg="white",
            font=("Helvetica", 10),
            width=10,
            cursor="hand2",
            command=self.detener_respaldo_automatico
        )
        self.btn_detener_auto.pack(side=tk.LEFT, padx=2)

        # Etiqueta de estado dinámico del respaldo
        self.label_estado_respaldo = tk.Label(
            self.frame_principal,
            text="",
            bg="#f5f5f5",
            fg="#00796b",
            font=("Helvetica", 10, "italic")
        )
        self.label_estado_respaldo.pack(pady=(5, 15))

        # Etiqueta para la tabla (ANTES del frame)
        tk.Label(
            self.frame_principal,
            text="📋 Historial de Respaldos:",
            bg="#f5f5f5",
            font=("Helvetica", 12, "bold"),
            fg="#333"
        ).pack(anchor=tk.W, padx=10, pady=(0, 5))

        # Frame para tabla con scrollbar
        frame_tabla_scroll = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_tabla_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tabla_scroll, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview con columnas mejoradas
        self.tabla_respaldo = ttk.Treeview(
            frame_tabla_scroll,
            columns=("archivo", "fecha", "tamaño"),
            show="headings",
            height=12,
            yscrollcommand=scrollbar.set
        )

        # Configurar encabezados y columnas
        self.tabla_respaldo.heading("archivo", text="Nombre del Archivo")
        self.tabla_respaldo.heading("fecha", text="Fecha y Hora")
        self.tabla_respaldo.heading("tamaño", text="Tamaño")

        self.tabla_respaldo.column("archivo", width=350, anchor=tk.W)
        self.tabla_respaldo.column("fecha", width=150, anchor=tk.CENTER)
        self.tabla_respaldo.column("tamaño", width=100, anchor=tk.CENTER)

        # Asociar scrollbar al Treeview
        scrollbar.config(command=self.tabla_respaldo.yview)

        self.tabla_respaldo.pack(fill=tk.BOTH, expand=True)

        # Separador visual entre tabla y botones
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=15)

        # Frame Botones
        frame_botones = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        # Botones con mejor estilo
        botones = [
            ("📁 Ver Carpeta", "#2196f3", self.abrir_carpeta),
            ("🗑️ Eliminar", "#f44336", self.eliminar_respaldo),
            ("🔄 Restaurar", "#ff9800", self.restaurar_respaldo),
            ("🔄 Refrescar", "#4caf50", self.actualizar_lista)
        ]

        for texto, color, comando in botones:
            btn = tk.Button(
                frame_botones,
                text=texto,
                bg=color,
                fg="white",
                font=("Helvetica", 10),
                width=12,
                cursor="hand2",
                command=comando
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Cargar lista inicial
        self.actualizar_lista()

    def cargar_configuracion_respaldo(self):
        """Carga la configuración de respaldo desde el archivo"""
        try:
            with open("config_respaldo.json", "r") as f:
                config = json.load(f)
                intervalo = config.get("intervalo", "Cada día")
                if intervalo:
                    self.combo_intervalo.set(intervalo)
                else:
                    self.combo_intervalo.set("Cada día")
        except FileNotFoundError:
            self.combo_intervalo.set("Cada día")
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            self.combo_intervalo.set("Cada día")

    def generar_respaldo(self):
        """Genera un respaldo manual de la base de datos"""
        try:
            # Mostrar indicador de progreso
            self.label_estado_respaldo.config(text="⏳ Generando respaldo...")
            self.ventana.update()

            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"respaldo_bd_{fecha}.sql"
            carpeta_respaldos = self.directorio
            ruta_archivo = os.path.join(carpeta_respaldos, nombre_archivo)

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
                resultado = subprocess.run(
                    comando,
                    stdout=salida,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )

            # Verificar que el archivo se creó y tiene contenido
            if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 0:
                self.label_estado_respaldo.config(text="✅ Respaldo completado exitosamente")
                messagebox.showinfo(
                    "Respaldo creado",
                    f"Archivo guardado en:\n{ruta_archivo}\n\nTamaño: {self.formatear_tamanio(os.path.getsize(ruta_archivo))}"
                )
                self.actualizar_lista()
            else:
                raise Exception("El archivo de respaldo está vacío o no se creó correctamente")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else "Error desconocido"
            self.label_estado_respaldo.config(text="❌ Error al generar respaldo")
            messagebox.showerror(
                "Error",
                f"No se pudo generar el respaldo:\n{error_msg}\n\nVerifique:\n• Credenciales de MySQL\n• Permisos de escritura\n• Conexión a la base de datos"
            )
        except FileNotFoundError:
            self.label_estado_respaldo.config(text="❌ mysqldump no encontrado")
            messagebox.showerror(
                "Error",
                "No se encontró mysqldump.\n\nAsegúrese de que MySQL esté instalado y mysqldump esté en el PATH del sistema."
            )
        except Exception as e:
            self.label_estado_respaldo.config(text="❌ Error al generar respaldo")
            messagebox.showerror("Error", f"No se pudo generar el respaldo:\n{str(e)}")

    def formatear_tamanio(self, bytes_size):
        """Convierte bytes a formato legible"""
        if bytes_size == 0:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    def actualizar_lista(self):
        """Actualiza la lista de archivos de respaldo"""
        # Limpiar tabla
        for item in self.tabla_respaldo.get_children():
            self.tabla_respaldo.delete(item)

        try:
            if not os.path.exists(self.directorio):
                os.makedirs(self.directorio, exist_ok=True)
                return

            archivos = [f for f in os.listdir(self.directorio) if f.endswith(".sql")]
            archivos.sort(reverse=True)  # Más recientes primero

            if not archivos:
                self.tabla_respaldo.insert("", tk.END, values=("No hay respaldos disponibles", "", ""))
                return

            for archivo in archivos:
                ruta_completa = os.path.join(self.directorio, archivo)
                try:
                    # Obtener información del archivo
                    stat_info = os.stat(ruta_completa)
                    tamanio = self.formatear_tamanio(stat_info.st_size)

                    # Extraer fecha desde el nombre: respaldo_bd_YYYYMMDD_HHMMSS.sql
                    try:
                        if archivo.startswith("respaldo_bd_") and archivo.endswith(".sql"):
                            fecha_parte = archivo.replace("respaldo_bd_", "").replace(".sql", "")
                            if "_" in fecha_parte:
                                fecha_str, hora_str = fecha_parte.split("_")
                                fecha_obj = datetime.datetime.strptime(fecha_str + hora_str, "%Y%m%d%H%M%S")
                                fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
                            else:
                                fecha_formateada = "Formato de fecha no válido"
                        else:
                            # Para archivos con formato diferente, usar fecha de modificación
                            fecha_obj = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                            fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
                    except Exception:
                        fecha_formateada = "Fecha no disponible"

                    self.tabla_respaldo.insert("", tk.END, values=(archivo, fecha_formateada, tamanio))

                except OSError as e:
                    print(f"Error al leer archivo {archivo}: {e}")
                    continue

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la lista:\n{str(e)}")

    def abrir_carpeta(self):
        """Abre la carpeta de respaldos en el explorador"""
        ruta = os.path.abspath(self.directorio)

        if not os.path.exists(ruta):
            os.makedirs(ruta, exist_ok=True)

        try:
            # Windows
            if os.name == 'nt':
                os.startfile(ruta)
            # macOS
            elif os.name == 'posix' and os.uname().sysname == 'Darwin':
                subprocess.run(["open", ruta])
            # Linux y otros Unix
            else:
                subprocess.run(["xdg-open", ruta])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")

    def eliminar_respaldo(self):
        """Elimina el respaldo seleccionado"""
        seleccion = self.tabla_respaldo.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un respaldo para eliminar.")
            return

        archivo = self.tabla_respaldo.item(seleccion[0], "values")[0]

        # Verificar que no sea el mensaje de "no hay respaldos"
        if archivo == "No hay respaldos disponibles":
            return

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar el respaldo?\n\n'{archivo}'\n\nEsta acción no se puede deshacer."
        )

        if confirmacion:
            try:
                ruta_archivo = os.path.join(self.directorio, archivo)
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
                    self.actualizar_lista()
                    messagebox.showinfo("Eliminado", f"Respaldo '{archivo}' eliminado correctamente.")
                else:
                    messagebox.showerror("Error", "El archivo no existe.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el respaldo:\n{str(e)}")

    def restaurar_respaldo(self):
        """Restaura la base de datos desde el respaldo seleccionado"""
        seleccion = self.tabla_respaldo.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un respaldo para restaurar.")
            return

        archivo = self.tabla_respaldo.item(seleccion[0], "values")[0]

        # Verificar que no sea el mensaje de "no hay respaldos"
        if archivo == "No hay respaldos disponibles":
            return

        ruta_respaldo = os.path.join(self.directorio, archivo)

        if not os.path.exists(ruta_respaldo):
            messagebox.showerror("Error", "El archivo de respaldo no existe.")
            return

        # Advertencia de seguridad
        confirmacion = messagebox.askyesno(
            "⚠️ CONFIRMAR RESTAURACIÓN",
            f"ADVERTENCIA: Esta operación sobrescribirá COMPLETAMENTE la base de datos actual.\n\n"
            f"Archivo a restaurar: {archivo}\n\n"
            f"• Se perderán TODOS los datos actuales\n"
            f"• Esta acción NO se puede deshacer\n"
            f"• Se recomienda hacer un respaldo antes de continuar\n\n"
            f"¿Deseas continuar con la restauración?",
            icon='warning'
        )

        if not confirmacion:
            return

        try:
            # Mostrar progreso
            self.label_estado_respaldo.config(text="⏳ Restaurando base de datos...")
            self.ventana.update()

            # Leer configuración
            with open("config.json", "r") as f:
                config = json.load(f)

            usuario = config["user"]
            password = config["password"]
            base_datos = config["database"]
            host = config.get("host", "localhost")

            # Comando para restaurar
            comando = [
                "mysql",
                f"-h{host}",
                f"-u{usuario}",
                f"-p{password}",
                base_datos
            ]

            # Ejecutar restauración
            with open(ruta_respaldo, 'r', encoding='utf-8') as archivo_sql:
                resultado = subprocess.run(
                    comando,
                    stdin=archivo_sql,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            if resultado.returncode == 0:
                self.label_estado_respaldo.config(text="✅ Base de datos restaurada exitosamente")
                messagebox.showinfo(
                    "Restauración completa",
                    f"La base de datos fue restaurada correctamente desde:\n{archivo}\n\n"
                    f"Se recomienda reiniciar la aplicación para reflejar todos los cambios."
                )
            else:
                error_msg = resultado.stderr or "Error desconocido"
                self.label_estado_respaldo.config(text="❌ Error en la restauración")
                messagebox.showerror(
                    "Error al restaurar",
                    f"Ocurrió un error durante la restauración:\n\n{error_msg}\n\n"
                    f"Verifique:\n• Las credenciales de MySQL\n• Los permisos de la base de datos\n• La integridad del archivo de respaldo"
                )

        except FileNotFoundError:
            self.label_estado_respaldo.config(text="❌ mysql no encontrado")
            messagebox.showerror(
                "Error",
                "No se encontró el cliente MySQL.\n\nAsegúrese de que MySQL esté instalado y el cliente mysql esté en el PATH del sistema."
            )
        except Exception as e:
            self.label_estado_respaldo.config(text="❌ Error en la restauración")
            messagebox.showerror("Error", f"No se pudo restaurar el respaldo:\n{str(e)}")

    def actualizar_estado_botones_respaldo(self):
        """Actualiza el estado de los botones de respaldo automático"""
        try:
            with open("config_respaldo.json", "r") as f:
                config = json.load(f)
                intervalo = config.get("intervalo", "")
                if intervalo and intervalo.strip():
                    self.btn_toggle_auto.config(
                        state=tk.DISABLED,
                        text="✅ Activo",
                        bg="#66bb6a"
                    )
                    self.btn_detener_auto.config(
                        state=tk.NORMAL,
                        bg="#f44336"
                    )
                    self.combo_intervalo.set(intervalo)
                    self.label_estado_respaldo.config(
                        text=f"🟢 Respaldo automático activo ({intervalo.lower()})",
                        fg="#4caf50"
                    )
                else:
                    self.btn_toggle_auto.config(
                        state=tk.NORMAL,
                        text="▶️ Iniciar",
                        bg="#4caf50"
                    )
                    self.btn_detener_auto.config(
                        state=tk.DISABLED,
                        bg="#bdbdbd"
                    )
                    self.label_estado_respaldo.config(
                        text="🔴 Respaldo automático desactivado",
                        fg="#f44336"
                    )
        except FileNotFoundError:
            self.btn_toggle_auto.config(
                state=tk.NORMAL,
                text="▶️ Iniciar",
                bg="#4caf50"
            )
            self.btn_detener_auto.config(
                state=tk.DISABLED,
                bg="#bdbdbd"
            )
            self.label_estado_respaldo.config(
                text="🔴 Respaldo automático desactivado",
                fg="#f44336"
            )
        except Exception as e:
            self.label_estado_respaldo.config(
                text="⚠️ Estado desconocido del respaldo automático",
                fg="#ff9800"
            )
            print(f"[ERROR] No se pudo actualizar el estado del respaldo: {e}")

    def iniciar_respaldo_automatico(self):
        """Inicia el respaldo automático"""
        intervalo = self.combo_intervalo.get()

        if not intervalo:
            messagebox.showwarning("Selección requerida",
                                   "Por favor selecciona una frecuencia para el respaldo automático.")
            return

        try:
            self.respaldo_auto.configurar_intervalo(intervalo)
            self.respaldo_auto.iniciar()

            messagebox.showinfo(
                "Respaldo automático",
                f"Respaldo automático iniciado correctamente.\n\nFrecuencia: {intervalo}\n\nLos respaldos se ejecutarán en segundo plano."
            )
            self.actualizar_estado_botones_respaldo()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el respaldo automático:\n{str(e)}")

    def detener_respaldo_automatico(self):
        """Detiene el respaldo automático"""
        try:
            self.respaldo_auto.detener()
            messagebox.showinfo("Respaldo automático", "Respaldo automático desactivado correctamente.")
            self.actualizar_estado_botones_respaldo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo detener el respaldo automático:\n{str(e)}")


# Función de entrada principal
def abrir_respaldos(ventana_padre=None, id_usuario=None):
    """Función para abrir el módulo de respaldos desde otros módulos"""
    return ModuloRespaldo(ventana_padre, id_usuario)


# Para pruebas independientes
if __name__ == "__main__":
    id_usuario_prueba = 1
    ModuloRespaldo(id_usuario=id_usuario_prueba)