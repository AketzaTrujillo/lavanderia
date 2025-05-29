"""
Script de empaquetado para Sistema de Lavandería
Convierte la aplicación Python en un ejecutable de escritorio
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def crear_spec_file():
    """Crea el archivo .spec personalizado para PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Img', 'Img'),
        ('config.json', '.'),
        ('lavanderia_estructura.sql', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        'mysql.connector',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'datetime',
        'json',
        'os',
        'sys',
        'threading',
        'subprocess',
        'smtplib',
        'email.mime.text',
        'email.mime.multipart',
        'webbrowser',
        'random',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaLavanderia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Img/lavadora.ico' if os.path.exists('Img/lavadora.ico') else None,
)
'''

    with open('SistemaLavanderia.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ Archivo .spec creado correctamente")


def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias = [
        'pyinstaller',
        'mysql-connector-python',
        'Pillow',
        'tkinter'
    ]

    print("🔍 Verificando dependencias...")
    faltantes = []

    for dep in dependencias:
        try:
            if dep == 'tkinter':
                import tkinter
            elif dep == 'mysql-connector-python':
                import mysql.connector
            elif dep == 'Pillow':
                import PIL
            elif dep == 'pyinstaller':
                import PyInstaller
        except ImportError:
            faltantes.append(dep)

    if faltantes:
        print(f"❌ Faltan las siguientes dependencias: {', '.join(faltantes)}")
        print("💡 Instálalas con: pip install " + " ".join(faltantes))
        return False

    print("✅ Todas las dependencias están instaladas")
    return True


def limpiar_build():
    """Limpia directorios de build anteriores"""
    directorios = ['build', 'dist', '__pycache__']

    for directorio in directorios:
        if os.path.exists(directorio):
            shutil.rmtree(directorio)
            print(f"🧹 Eliminado: {directorio}")


def crear_ejecutable():
    """Crea el ejecutable usando PyInstaller"""
    print("🔨 Creando ejecutable...")

    try:
        # Comando PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name=SistemaLavanderia',
            '--add-data=Img;Img',
            '--add-data=config.json;.',
            '--add-data=lavanderia_estructura.sql;.',
            '--hidden-import=tkinter',
            '--hidden-import=mysql.connector',
            '--hidden-import=PIL',
        ]

        # Agregar ícono si existe
        if os.path.exists('Img/lavadora.ico'):
            cmd.extend(['--icon=Img/lavadora.ico'])

        cmd.append('main.py')

        # Ejecutar PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Ejecutable creado exitosamente")
            return True
        else:
            print(f"❌ Error al crear ejecutable: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_necesarios = [
        'main.py',
        'loginP.py',
        'conexion.py',
        'utileria.py',
        'config.json',
        'lavanderia_estructura.sql'
    ]

    print("📋 Verificando archivos necesarios...")
    faltantes = []

    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            faltantes.append(archivo)

    if faltantes:
        print(f"❌ Faltan los siguientes archivos: {', '.join(faltantes)}")
        return False

    print("✅ Todos los archivos necesarios están presentes")
    return True


def main():
    """Función principal del script de empaquetado"""
    print("🚀 INICIANDO EMPAQUETADO DEL SISTEMA DE LAVANDERÍA")
    print("=" * 60)

    # Verificaciones previas
    if not verificar_archivos():
        return False

    if not verificar_dependencias():
        return False

    # Limpiar builds anteriores
    limpiar_build()

    # Crear ejecutable
    if crear_ejecutable():
        print("\n" + "=" * 60)
        print("🎉 EMPAQUETADO COMPLETADO EXITOSAMENTE")
        print("📁 El ejecutable se encuentra en: dist/SistemaLavanderia.exe")
        print("💡 Puedes distribuir el archivo .exe junto con los archivos de configuración")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ ERROR EN EL EMPAQUETADO")
        return False


if __name__ == "__main__":
    main()