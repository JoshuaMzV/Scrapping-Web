@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo ========================================================
echo  🚀 INICIANDO GENERADOR DE CATÁLOGOS
echo ========================================================
echo.

if not exist "venv" (
    echo ⚠️  Creando entorno virtual...
    python -m venv venv
    echo ✓ Entorno virtual creado
)

echo 📦 Activando entorno virtual...
call venv\Scripts\activate.bat

echo 🔧 Verificando dependencias...
pip install -q -r requirements.txt

echo 📱 Iniciando aplicación...
echo 🌐 Abriendo en: http://127.0.0.1:5000
echo 💡 Presiona Ctrl+C para detener
echo.

python run.py

pause
