@echo off
echo ========================================
echo INSTALACIÓN SISTEMA FERRETERÍA
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado
    echo Por favor instale Python 3.12 desde: https://www.python.org/
    pause
    exit /b 1
)

echo Python detectado
echo.

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR al instalar dependencias
    pause
    exit /b 1
)

echo Dependencias instaladas correctamente
echo.

REM Crear base de datos
echo Creando base de datos...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR al crear base de datos
    pause
    exit /b 1
)

echo Base de datos creada correctamente
echo.

REM Configuración inicial
echo Configurando sistema inicial...
python manage.py auto_config
if %errorlevel% neq 0 (
    echo ERROR en configuración inicial
    pause
    exit /b 1
)

echo Sistema configurado correctamente
echo.

echo ========================================
echo INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo Para iniciar el sistema:
echo python manage.py runserver
echo.
echo Luego acceda a: http://localhost:8000
echo Usuario: admin
echo Contraseña: admin123
echo.
echo IMPORTANTE: Cambie la contraseña del admin
echo despues del primer inicio.
echo.
pause