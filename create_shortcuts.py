"""
Script para crear accesos directos del Sistema de Lavandería
Crea iconos en escritorio y menú inicio
"""

import os
import sys
import winshell
from win32com.client import Dispatch
import tkinter as tk
from tkinter import messagebox
import shutil
from pathlib import Path


class CreadorAccesosDirectos:
    def __init__(self):
        self.ruta_instalacion = os.path.abspath(os.getcwd())
        self.crear_interfaz()

    def crear_interfaz(self):
        """Crea la interfaz para el creador de accesos directos"""
        self.ventana = tk.Tk()
        self.ventana.title("Crear Accesos Directos - Sistema de Lavandería")
        self.ventana.geometry("500x400")
        self.ventana.resizable(False, False)
        self.ventana.config(bg="#f0f4f8")

        # Centrar ventana
        self.centrar_ventana()

        # Header
        header_frame = tk.Frame(self.ventana, bg="#2563eb", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="🔗 Crear Accesos Directos",
            font=("Segoe UI", 16, "bold"),
            bg="#2563eb",
            fg="white"
        ).pack(pady=25)

        # Contenido principal
        content_frame = tk.Frame(self.ventana, bg="#ffffff", relief=tk.RAISED, bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content_frame,
            text="Seleccione dónde crear los accesos directos:",
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#374151"
        ).pack(pady=20)

        # Opciones
        self.var_escritorio = tk.BooleanVar(value=True)
        tk.Checkbutton(
            content_frame,
            text="🖥️ Crear acceso directo en el Escritorio",
            variable=self.var_escritorio,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#374151"
        ).pack(anchor=tk.W, padx=40, pady=5)

        self.var_menu_inicio = tk.BooleanVar(value=True)
        tk.Checkbutton(
            content_frame,
            text="📂 Agregar al Menú de Inicio",
            variable=self.var_menu_inicio,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#374151"
        ).pack(anchor=tk.W, padx=40, pady=5)

        self.var_inicio_automatico = tk.BooleanVar(value=False)
        tk.Checkbutton(
            content_frame,
            text="🚀 Iniciar automáticamente con Windows",
            variable=self.var_inicio_automatico,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#374151"
        ).pack(anchor=tk.W, padx=40, pady=5)

        # Información de la instalación
        info_frame = tk.Frame(content_frame, bg="#f8f9fa", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            info_frame,
            text="📍 Información de la instalación:",
            font=("Segoe UI", 11, "bold"),
            bg="#f8f9fa",
            fg="#374151"
        ).pack(anchor=tk.W, padx=10, pady=5)

        tk.Label(
            info_frame,
            text=f"Carpeta: {self.ruta_instalacion}",
            font=("Segoe UI", 9),
            bg="#f8f9fa",
            fg="#6b7280",
            wraplength=450
        ).pack(anchor=tk.W, padx=20, pady=2)

        # Verificar archivos
        archivos_encontrados = self.verificar_archivos()
        if archivos_encontrados['sistema']:
            tk.Label(
                info_frame,
                text="✅ SistemaLavanderia.exe encontrado",
                font=("Segoe UI", 9),
                bg="#f8f9fa",
                fg="#059669"
            ).pack(anchor=tk.W, padx=20, pady=2)
        else:
            tk.Label(
                info_frame,
                text="❌ SistemaLavanderia.exe no encontrado",
                font=("Segoe UI", 9),
                bg="#f8f9fa",
                fg="#dc2626"
            ).pack(anchor=tk.W, padx=20, pady=2)

        if archivos_encontrados['icono']:
            tk.Label(
                info_frame,
                text="✅ Icono de aplicación encontrado",
                font=("Segoe UI", 9),
                bg="#f8f9fa",
                fg="#059669"
            ).pack(anchor=tk.W, padx=20, pady=2)

        # Botones
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(
            button_frame,
            text="🔗 Crear Accesos Directos",
            font=("Segoe UI", 12, "bold"),
            bg="#2563eb",
            fg="white",
            width=20,
            height=2,
            command=self.crear_accesos_directos
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="❌ Cancelar",
            font=("Segoe UI", 12),
            bg="#6b7280",
            fg="white",
            width=15,
            height=2,
            command=self.ventana.destroy
        ).pack(side=tk.RIGHT, padx=10)

        self.ventana.mainloop()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def verificar_archivos(self):
        """Verifica que los archivos necesarios existan"""
        archivos = {
            'sistema': os.path.exists(os.path.join(self.ruta_instalacion, "SistemaLavanderia.exe")),
            'icono': os.path.exists(os.path.join(self.ruta_instalacion, "Img", "lavadora.ico"))
        }
        return archivos

    def crear_accesos_directos(self):
        """Crea los accesos directos seleccionados"""
        try:
            archivos = self.verificar_archivos()

            if not archivos['sistema']:
                messagebox.showerror(
                    "Error",
                    "No se encontró SistemaLavanderia.exe en la carpeta actual.\n\n"
                    "Asegúrese de ejecutar este script desde la carpeta de instalación."
                )
                return

            ruta_ejecutable = os.path.join(self.ruta_instalacion, "SistemaLavanderia.exe")
            ruta_icono = os.path.join(self.ruta_instalacion, "Img", "lavadora.ico") if archivos['icono'] else ""

            accesos_creados = []

            # Crear acceso directo en escritorio
            if self.var_escritorio.get():
                try:
                    escritorio = winshell.desktop()
                    ruta_acceso = os.path.join(escritorio, "Sistema de Lavandería.lnk")

                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(ruta_acceso)
                    shortcut.Targetpath = ruta_ejecutable
                    shortcut.WorkingDirectory = self.ruta_instalacion
                    shortcut.Description = "Sistema de Gestión de Lavandería"
                    if ruta_icono and os.path.exists(ruta_icono):
                        shortcut.IconLocation = ruta_icono
                    shortcut.save()

                    accesos_creados.append("Escritorio")

                except Exception as e:
                    messagebox.showwarning(
                        "Advertencia",
                        f"No se pudo crear el acceso directo en el escritorio:\n{e}"
                    )

            # Agregar al menú de inicio
            if self.var_menu_inicio.get():
                try:
                    menu_inicio = winshell.start_menu()
                    carpeta_programa = os.path.join(menu_inicio, "Programas", "Sistema de Lavandería")

                    # Crear carpeta si no existe
                    os.makedirs(carpeta_programa, exist_ok=True)

                    ruta_acceso = os.path.join(carpeta_programa, "Sistema de Lavandería.lnk")

                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(ruta_acceso)
                    shortcut.Targetpath = ruta_ejecutable
                    shortcut.WorkingDirectory = self.ruta_instalacion
                    shortcut.Description = "Sistema de Gestión de Lavandería"
                    if ruta_icono and os.path.exists(ruta_icono):
                        shortcut.IconLocation = ruta_icono
                    shortcut.save()

                    # Crear también acceso directo al desinstalador si existe
                    ruta_desinstalador = os.path.join(self.ruta_instalacion, "uninstall.exe")
                    if os.path.exists(ruta_desinstalador):
                        ruta_acceso_desinst = os.path.join(carpeta_programa, "Desinstalar.lnk")
                        shortcut_desinst = shell.CreateShortCut(ruta_acceso_desinst)
                        shortcut_desinst.Targetpath = ruta_desinstalador
                        shortcut_desinst.WorkingDirectory = self.ruta_instalacion
                        shortcut_desinst.Description = "Desinstalar Sistema de Lavandería"
                        shortcut_desinst.save()

                    accesos_creados.append("Menú de Inicio")

                except Exception as e:
                    messagebox.showwarning(
                        "Advertencia",
                        f"No se pudo agregar al menú de inicio:\n{e}"
                    )

            # Agregar al inicio automático
            if self.var_inicio_automatico.get():
                try:
                    startup = winshell.startup()
                    ruta_acceso = os.path.join(startup, "Sistema de Lavandería.lnk")

                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(ruta_acceso)
                    shortcut.Targetpath = ruta_ejecutable
                    shortcut.WorkingDirectory = self.ruta_instalacion
                    shortcut.Description = "Sistema de Gestión de Lavandería - Inicio Automático"
                    if ruta_icono and os.path.exists(ruta_icono):
                        shortcut.IconLocation = ruta_icono
                    shortcut.save()

                    accesos_creados.append("Inicio Automático")

                except Exception as e:
                    messagebox.showwarning(
                        "Advertencia",
                        f"No se pudo configurar el inicio automático:\n{e}"
                    )

            # Mostrar resultado
            if accesos_creados:
                mensaje = "✅ Accesos directos creados exitosamente en:\n\n"
                mensaje += "\n".join([f"• {acceso}" for acceso in accesos_creados])
                mensaje += "\n\n¡Ya puede usar el Sistema de Lavandería desde estos accesos!"

                messagebox.showinfo("Éxito", mensaje)
                self.ventana.destroy()
            else:
                messagebox.showwarning(
                    "Sin cambios",
                    "No se seleccionó ninguna opción para crear accesos directos."
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al crear los accesos directos:\n{e}"
            )


def crear_script_desinstalacion():
    """Crea un script de desinstalación básico"""
    script_desinstall = '''@echo off
title Desinstalar Sistema de Lavandería

echo.
echo ================================================================
echo          DESINSTALADOR - SISTEMA DE LAVANDERÍA
echo ================================================================
echo.
echo Este proceso eliminará los accesos directos del sistema.
echo Los archivos del programa y la base de datos NO se eliminarán.
echo.

set /p "confirmar=¿Desea continuar? (s/n): "
if /i not "%confirmar%"=="s" (
    echo Desinstalación cancelada.
    pause
    exit /b 0
)

echo.
echo Eliminando accesos directos...

REM Eliminar del escritorio
if exist "%USERPROFILE%\\Desktop\\Sistema de Lavandería.lnk" (
    del "%USERPROFILE%\\Desktop\\Sistema de Lavandería.lnk"
    echo ✅ Eliminado del escritorio
)

REM Eliminar del menú de inicio
if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Sistema de Lavandería" (
    rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Sistema de Lavandería"
    echo ✅ Eliminado del menú de inicio
)

REM Eliminar del inicio automático
if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Sistema de Lavandería.lnk" (
    del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Sistema de Lavandería.lnk"
    echo ✅ Eliminado del inicio automático
)

echo.
echo ================================================================
echo                    DESINSTALACIÓN COMPLETADA
echo ================================================================
echo.
echo • Los accesos directos han sido eliminados
echo • Los archivos del programa permanecen en esta carpeta
echo • La base de datos NO ha sido afectada
echo.
echo Para eliminar completamente el sistema:
echo 1. Elimine manualmente esta carpeta
echo 2. Elimine la base de datos 'lavanderiadb' desde MySQL
echo.

pause
'''

    try:
        with open("uninstall.bat", "w", encoding="utf-8") as f:
            f.write(script_desinstall)
        print("✅ Script de desinstalación creado: uninstall.bat")
    except Exception as e:
        print(f"❌ Error al crear script de desinstalación: {e}")


def main():
    """Función principal"""
    try:
        # Verificar que estamos en Windows
        if os.name != 'nt':
            print("❌ Este script solo funciona en Windows")
            return

        # Verificar dependencias
        try:
            import winshell
            from win32com.client import Dispatch
        except ImportError:
            messagebox.showerror(
                "Dependencias faltantes",
                "Faltan dependencias necesarias.\n\n"
                "Instale con:\n"
                "pip install pywin32 winshell"
            )
            return

        # Crear script de desinstalación
        crear_script_desinstalacion()

        # Iniciar creador de accesos directos
        CreadorAccesosDirectos()

    except Exception as e:
        print(f"❌ Error: {e}")
        if 'tkinter' in str(e):
            print("💡 Asegúrese de que tkinter esté disponible")
        else:
            messagebox.showerror("Error", f"Error al iniciar el creador de accesos directos:\n{e}")


if __name__ == "__main__":
    main()