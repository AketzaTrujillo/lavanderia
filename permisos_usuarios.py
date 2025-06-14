import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Asegurar que podemos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
except ImportError as e:
    print(f"Error al importar conexion: {e}")


class GestionPermisosUsuarios:
    """Clase para gestionar permisos específicos de cada cajero"""

    def __init__(self, ventana_padre=None):
        # Crear ventana
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Permisos de Usuarios")
        self.ventana.geometry("800x600")
        self.ventana.config(bg="#f0f9ff")
        self.ventana.resizable(False, False)

        # Variables
        self.usuario_seleccionado = None
        self.permisos_disponibles = {
            'registrar_pedido': 'Registrar Pedidos',
            'gestionar_clientes': 'Gestionar Clientes',
            'registrar_venta': 'Registrar Ventas',
            'gestionar_caja': 'Gestionar Caja',
            'seguimiento_pedidos': 'Seguimiento de Pedidos',
            'ver_reportes': 'Ver Reportes Básicos',
            'gestionar_inventario': 'Gestionar Inventario',
            'aplicar_descuentos': 'Aplicar Descuentos'
        }

        # Inicializar BD de permisos
        self.inicializar_tabla_permisos()

        # Crear interfaz
        self.crear_interfaz()

        # Cargar datos
        self.cargar_usuarios()

    def inicializar_tabla_permisos(self):
        """Crear tabla de permisos si no existe"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Crear tabla permisos_usuarios si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permisos_usuarios (
                    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    modulo VARCHAR(50) NOT NULL,
                    permitido BOOLEAN DEFAULT FALSE,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_module (id_usuario, modulo)
                )
            """)

            conexion.commit()
            conexion.close()

        except Exception as e:
            print(f"Error al inicializar tabla de permisos: {e}")

    def verificar_estructura_usuarios(self):
        """Verificar qué columnas tiene la tabla usuarios"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("DESCRIBE usuarios")
            columnas = cursor.fetchall()
            conexion.close()

            # Retornar lista de nombres de columnas
            return [col[0] for col in columnas]

        except Exception as e:
            print(f"Error al verificar estructura: {e}")
            return []

    def crear_interfaz(self):
        """Crear la interfaz gráfica"""
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg="#f0f9ff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(main_frame, text="🔒 Gestión de Permisos de Usuarios",
                          font=("Segoe UI", 18, "bold"), bg="#f0f9ff", fg="#1f2937")
        titulo.pack(pady=(0, 20))

        # Frame superior para selección de usuario
        frame_usuarios = tk.LabelFrame(main_frame, text="Seleccionar Cajero",
                                       font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#374151")
        frame_usuarios.pack(fill=tk.X, pady=(0, 20))

        # Combobox para usuarios
        tk.Label(frame_usuarios, text="Cajero:", font=("Segoe UI", 10),
                 bg="#ffffff").pack(side=tk.LEFT, padx=(10, 5), pady=10)

        self.combo_usuarios = ttk.Combobox(frame_usuarios, width=30, state="readonly",
                                           font=("Segoe UI", 10))
        self.combo_usuarios.pack(side=tk.LEFT, padx=(0, 10), pady=10)
        self.combo_usuarios.bind("<<ComboboxSelected>>", self.on_usuario_seleccionado)

        # Información del usuario seleccionado
        self.label_info_usuario = tk.Label(frame_usuarios, text="",
                                           font=("Segoe UI", 9), bg="#ffffff", fg="#6b7280")
        self.label_info_usuario.pack(side=tk.LEFT, padx=(20, 10), pady=10)

        # Frame para permisos
        frame_permisos = tk.LabelFrame(main_frame, text="Permisos Disponibles",
                                       font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#374151")
        frame_permisos.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Crear canvas y scrollbar para permisos
        canvas_frame = tk.Frame(frame_permisos, bg="#ffffff")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_permisos = tk.Canvas(canvas_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas_permisos.yview)
        self.frame_permisos_scroll = tk.Frame(self.canvas_permisos, bg="#ffffff")

        self.frame_permisos_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_permisos.configure(scrollregion=self.canvas_permisos.bbox("all"))
        )

        self.canvas_permisos.create_window((0, 0), window=self.frame_permisos_scroll, anchor="nw")
        self.canvas_permisos.configure(yscrollcommand=scrollbar.set)

        self.canvas_permisos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Checkboxes para permisos
        self.checkboxes_permisos = {}
        self.crear_checkboxes_permisos()

        # Frame de botones
        frame_botones = tk.Frame(main_frame, bg="#f0f9ff")
        frame_botones.pack(fill=tk.X, pady=(10, 0))

        # Botones de acción
        btn_guardar = tk.Button(frame_botones, text="💾 Guardar Cambios",
                                command=self.guardar_permisos, bg="#059669", fg="white",
                                font=("Segoe UI", 10, "bold"), padx=20, pady=8)
        btn_guardar.pack(side=tk.LEFT, padx=(0, 10))

        btn_todos = tk.Button(frame_botones, text="✅ Seleccionar Todos",
                              command=self.seleccionar_todos, bg="#0891b2", fg="white",
                              font=("Segoe UI", 10, "bold"), padx=20, pady=8)
        btn_todos.pack(side=tk.LEFT, padx=(0, 10))

        btn_ninguno = tk.Button(frame_botones, text="❌ Quitar Todos",
                                command=self.quitar_todos, bg="#dc2626", fg="white",
                                font=("Segoe UI", 10, "bold"), padx=20, pady=8)
        btn_ninguno.pack(side=tk.LEFT, padx=(0, 10))

        btn_cerrar = tk.Button(frame_botones, text="🚪 Cerrar",
                               command=self.ventana.destroy, bg="#6b7280", fg="white",
                               font=("Segoe UI", 10, "bold"), padx=20, pady=8)
        btn_cerrar.pack(side=tk.RIGHT)

    def crear_checkboxes_permisos(self):
        """Crear checkboxes para cada permiso"""
        row = 0
        for modulo, descripcion in self.permisos_disponibles.items():
            # Frame para cada permiso
            frame_permiso = tk.Frame(self.frame_permisos_scroll, bg="#f8fafc",
                                     relief=tk.RIDGE, bd=1)
            frame_permiso.pack(fill=tk.X, padx=5, pady=2)

            # Checkbox
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(frame_permiso, text="", variable=var,
                                      bg="#f8fafc", font=("Segoe UI", 10))
            checkbox.pack(side=tk.LEFT, padx=(10, 5), pady=8)

            # Descripción del permiso
            label_desc = tk.Label(frame_permiso, text=descripcion,
                                  font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#374151")
            label_desc.pack(side=tk.LEFT, padx=(0, 10), pady=8)

            # Código del módulo (más pequeño)
            label_codigo = tk.Label(frame_permiso, text=f"({modulo})",
                                    font=("Segoe UI", 8), bg="#f8fafc", fg="#6b7280")
            label_codigo.pack(side=tk.RIGHT, padx=(0, 10), pady=8)

            # Guardar referencia
            self.checkboxes_permisos[modulo] = var

            row += 1

    def cargar_usuarios(self):
        """Cargar lista de usuarios cajeros - CORREGIDO"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Primero verificar qué columnas existen
            columnas_disponibles = self.verificar_estructura_usuarios()
            print(f"Columnas disponibles en usuarios: {columnas_disponibles}")

            # Construir query dinámicamente según las columnas disponibles
            columnas_select = ["id_usuario", "nombre"]

            # Agregar correo si existe
            if 'correo' in columnas_disponibles:
                columnas_select.append("correo")
            elif 'email' in columnas_disponibles:
                columnas_select.append("email")

            # NO incluir fecha_creacion ya que causa error

            query = f"SELECT {', '.join(columnas_select)} FROM usuarios WHERE rol = 'cajero' ORDER BY nombre"
            cursor.execute(query)

            usuarios = cursor.fetchall()

            # Limpiar combobox
            self.combo_usuarios['values'] = []

            if usuarios:
                valores = []
                self.usuarios_data = {}

                for usuario in usuarios:
                    id_usuario = usuario[0]
                    nombre = usuario[1]

                    # Determinar si tenemos email
                    if len(usuario) > 2:
                        email = usuario[2]
                        display_text = f"{nombre} ({email})"
                    else:
                        email = "N/A"
                        display_text = nombre

                    valores.append(display_text)
                    self.usuarios_data[display_text] = {
                        'id': id_usuario,
                        'nombre': nombre,
                        'correo': email
                    }

                self.combo_usuarios['values'] = valores
            else:
                messagebox.showinfo("Información", "No se encontraron usuarios cajeros en el sistema.")

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
            print(f"Error detallado: {e}")

    def on_usuario_seleccionado(self, event=None):
        """Cuando se selecciona un usuario - CORREGIDO"""
        seleccion = self.combo_usuarios.get()
        if seleccion and seleccion in self.usuarios_data:
            self.usuario_seleccionado = self.usuarios_data[seleccion]

            # Mostrar información del usuario (sin fecha que no existe)
            info_text = f"ID: {self.usuario_seleccionado['id']} | Usuario: {self.usuario_seleccionado['nombre']}"
            self.label_info_usuario.config(text=info_text)

            # Cargar permisos del usuario
            self.cargar_permisos_usuario()

    def cargar_permisos_usuario(self):
        """Cargar permisos del usuario seleccionado"""
        if not self.usuario_seleccionado:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener permisos del usuario
            cursor.execute("""
                SELECT modulo, permitido 
                FROM permisos_usuarios 
                WHERE id_usuario = %s
            """, (self.usuario_seleccionado['id'],))

            permisos_usuario = cursor.fetchall()

            # Resetear todos los checkboxes
            for var in self.checkboxes_permisos.values():
                var.set(False)

            # Marcar permisos que tiene el usuario
            for modulo, permitido in permisos_usuario:
                if modulo in self.checkboxes_permisos:
                    self.checkboxes_permisos[modulo].set(bool(permitido))

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar permisos del usuario: {e}")

    def guardar_permisos(self):
        """Guardar permisos del usuario seleccionado"""
        if not self.usuario_seleccionado:
            messagebox.showwarning("Advertencia", "Debe seleccionar un cajero primero.")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener permisos marcados
            permisos_marcados = []
            for modulo, var in self.checkboxes_permisos.items():
                permitido = var.get()
                permisos_marcados.append((self.usuario_seleccionado['id'], modulo, permitido))

            # Eliminar permisos existentes del usuario
            cursor.execute("DELETE FROM permisos_usuarios WHERE id_usuario = %s",
                           (self.usuario_seleccionado['id'],))

            # Insertar nuevos permisos
            cursor.executemany("""
                INSERT INTO permisos_usuarios (id_usuario, modulo, permitido) 
                VALUES (%s, %s, %s)
            """, permisos_marcados)

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito",
                                f"Permisos actualizados correctamente para {self.usuario_seleccionado['nombre']}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar permisos: {e}")

    def seleccionar_todos(self):
        """Marcar todos los permisos"""
        for var in self.checkboxes_permisos.values():
            var.set(True)

    def quitar_todos(self):
        """Desmarcar todos los permisos"""
        for var in self.checkboxes_permisos.values():
            var.set(False)

    @staticmethod
    def obtener_permisos_usuario(id_usuario):
        """Método estático para obtener permisos de un usuario específico"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT modulo, permitido 
                FROM permisos_usuarios 
                WHERE id_usuario = %s AND permitido = TRUE
            """, (id_usuario,))

            permisos = cursor.fetchall()
            conexion.close()

            # Retornar lista de módulos permitidos
            return [permiso[0] for permiso in permisos]

        except Exception as e:
            print(f"Error al obtener permisos del usuario {id_usuario}: {e}")
            return []


# Función para abrir la ventana de gestión de permisos
def abrir_gestion_permisos(ventana_padre=None):
    GestionPermisosUsuarios(ventana_padre)


if __name__ == "__main__":
    # Para pruebas
    app = GestionPermisosUsuarios()
    app.ventana.mainloop()