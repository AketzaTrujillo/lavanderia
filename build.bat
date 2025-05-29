@echo off
chcp 65001 >nul
title Sistema de Lavandería - Builder

echo.
echo ================================================================
echo         🏢 SISTEMA DE LAVANDERÍA - CONSTRUCTOR AUTOMÁTICO
echo ================================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en el PATH
    echo 💡 Instale Python desde: https://python.org
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
python --version

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo.
    echo 📦 Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Error al crear entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)

REM Activar entorno virtual
echo.
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo.
echo 📈 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo.
echo 📚 Instalando dependencias...
pip install pyinstaller mysql-connector-python Pillow pandas numpy matplotlib seaborn reportlab XlsxWriter tkcalendar flask requests pyautogui

if %errorlevel% neq 0 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

REM Limpiar builds anteriores
echo.
echo 🧹 Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.spec" del "*.spec"

echo ✅ Directorio limpio

REM Verificar archivos necesarios
echo.
echo 📋 Verificando archivos necesarios...

set "archivos_requeridos=main.py loginP.py conexion.py utileria.py config.json lavanderia_estructura.sql"
for %%f in (%archivos_requeridos%) do (
    if not exist "%%f" (
        echo ❌ Archivo faltante: %%f
        pause
        exit /b 1
    )
)

echo ✅ Todos los archivos necesarios están presentes

REM Crear el ejecutable principal
echo.
echo 🔨 Creando ejecutable principal del sistema...
pyinstaller --onefile ^
    --windowed ^
    --name=SistemaLavanderia ^
    --add-data="Img;Img" ^
    --add-data="config.json;." ^
    --add-data="lavanderia_estructura.sql;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=mysql.connector ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageTk ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.pyplot ^
    --hidden-import=seaborn ^
    --hidden-import=reportlab ^
    --hidden-import=reportlab.pdfgen ^
    --hidden-import=reportlab.pdfgen.canvas ^
    --hidden-import=XlsxWriter ^
    --hidden-import=tkcalendar ^
    --hidden-import=flask ^
    --hidden-import=requests ^
    --hidden-import=PyAutoGUI ^
    --hidden-import=admin_view ^
    --hidden-import=cajero_view ^
    --hidden-import=gestionar_clientes ^
    --hidden-import=gestionar_usuarios ^
    --hidden-import=gestionar_productos_servicios ^
    --hidden-import=ventas ^
    --hidden-import=pedidos ^
    --hidden-import=caja ^
    --hidden-import=seguimiento_pedidos ^
    --hidden-import=reportes ^
    --hidden-import=respaldos2 ^
    --hidden-import=historial_cliente ^
    --hidden-import=email_sender ^
    --hidden-import=email_sender_mejorado ^
    --hidden-import=auto_updater ^
    --hidden-import=resplado_automatico ^
    main.py

if %errorlevel% neq 0 (
    echo ❌ Error al crear ejecutable principal
    pause
    exit /b 1
)

echo ✅ Ejecutable principal creado

REM Crear el instalador
echo.
echo 🔧 Creando instalador...
pyinstaller --onefile ^
    --windowed ^
    --name=InstaladorLavanderia ^
    --add-data="lavanderia_estructura.sql;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=mysql.connector ^
    installer.py

if %errorlevel% neq 0 (
    echo ❌ Error al crear instalador
    pause
    exit /b 1
)

echo ✅ Instalador creado

REM Crear carpeta de distribución final
echo.
echo 📦 Preparando distribución final...
if not exist "distribucion" mkdir "distribucion"

REM Copiar archivos necesarios
copy "dist\SistemaLavanderia.exe" "distribucion\"
copy "dist\InstaladorLavanderia.exe" "distribucion\"
copy "config.json" "distribucion\"
copy "lavanderia_estructura.sql" "distribucion\"
copy "README.md" "distribucion\" 2>nul

REM Copiar carpeta de imágenes si existe
if exist "Img" xcopy "Img" "distribucion\Img\" /E /I /Q

REM Crear archivo README para la distribución
echo.
echo 📄 Creando documentación...
(
echo # Sistema de Lavandería - Distribución
echo.
echo ## Archivos incluidos:
echo - `InstaladorLavanderia.exe` - Ejecutar PRIMERO para instalar el sistema PRIMERO para instalar el sistema
echo - `SistemaLavanderia.exe` - Aplicación principal del sistema
echo - `config.json` - Archivo de configuración
echo - `lavanderia_estructura.sql` - Script de base de datos
echo - `Img/` - Carpeta de imágenes e iconos
echo.
echo ## Instrucciones de instalación:
echo 1. Asegúrese de tener MySQL Server instalado
echo 2. Ejecute `InstaladorLavanderia.exe`
echo 3. Siga las instrucciones del asistente
echo 4. Una vez instalado, ejecute `SistemaLavanderia.exe`
echo.
echo ## Credenciales iniciales:
echo - Usuario: admin@lavanderia.com
echo - Contraseña: 1234
echo.
echo ## Soporte:
echo Para soporte técnico, contacte al desarrollador.
) > "distribucion\LEEME.txt"

echo ✅ Documentación creada

REM Mostrar resumen final
echo.
echo ================================================================
echo                    🎉 CONSTRUCCIÓN COMPLETADA
echo ================================================================
echo.
echo 📁 Archivos generados en la carpeta 'distribucion':
echo    • InstaladorLavanderia.exe (Ejecutar primero)
echo    • SistemaLavanderia.exe (Aplicación principal)
echo    • Archivos de configuración y recursos
echo.
echo 💡 Para distribuir el sistema:
echo    1. Comprima la carpeta 'distribucion' en un ZIP
echo    2. Distribuya el ZIP a los usuarios finales
echo    3. Los usuarios deben ejecutar InstaladorLavanderia.exe primero
echo.
echo ✅ El sistema está listo para distribuir
echo.

REM Preguntar si abrir la carpeta de distribución
set /p "abrir=¿Desea abrir la carpeta de distribución? (s/n): "
if /i "%abrir%"=="s" (
    start explorer "distribucion"
)

echo.
echo Presione cualquier tecla para continuar...
pause >nul PRIMERO para instalar el sistema
echo - `SistemaLavanderia.exe` - Aplicación principal del sistema
echo - `config.json` - Archivo de configuración
echo - `lavanderia_estructura.sql` - Script de base de datos
echo - `Img/` - Carpeta de imágenes e iconos
echo.
echo ## Instrucciones de instalación:
echo 1. Asegúrese de tener MySQL Server instalado
echo 2. Ejecute `InstaladorLavanderia.exe`
echo 3. Siga las instrucciones del asistente
echo 4. Una vez instalado, ejecute `SistemaLavanderia.exe`
echo.
echo ## Credenciales iniciales:
echo - Usuario: admin@lavanderia.com
echo - Contraseña: 1234
echo.
echo ## Soporte:
echo Para soporte técnico, contacte al desarrollador.
) > "distribucion\LEEME.txt"

echo ✅ Documentación creada

REM Mostrar resumen final
echo.
echo ================================================================
echo                    🎉 CONSTRUCCIÓN COMPLETADA
echo ================================================================
echo.
echo 📁 Archivos generados en la carpeta 'distribucion':
echo    • InstaladorLavanderia.exe (Ejecutar primero)
echo    • SistemaLavanderia.exe (Aplicación principal)
echo    • Archivos de configuración y recursos
echo.
echo 💡 Para distribuir el sistema:
echo    1. Comprima la carpeta 'distribucion' en un ZIP
echo    2. Distribuya el ZIP a los usuarios finales
echo    3. Los usuarios deben ejecutar InstaladorLavanderia.exe primero
echo.
echo ✅ El sistema está listo para distribuir
echo.

REM Preguntar si abrir la carpeta de distribución
set /p "abrir=¿Desea abrir la carpeta de distribución? (s/n): "
if /i "%abrir%"=="s" (
    start explorer "distribucion"
)

echo.
echo Presione cualquier tecla para continuar...
pause >nul