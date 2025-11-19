Write-Host ""
Write-Host "========================================================"
Write-Host "  🚀 INICIANDO GENERADOR DE CATÁLOGOS"
Write-Host "========================================================"
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptPath

# Crear venv si no existe
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  Creando entorno virtual..."
    python -m venv venv
    Write-Host "✓ Entorno virtual creado"
}

Write-Host "📦 Activando entorno virtual..."
& .\venv\Scripts\Activate.ps1

Write-Host "🔧 Verificando dependencias..."
pip install -q -r requirements.txt

Write-Host "📱 Iniciando aplicación..."
Write-Host "🌐 Abriendo en: http://127.0.0.1:5000"
Write-Host "💡 Presiona Ctrl+C para detener"
Write-Host ""

python run.py

Read-Host "Presiona Enter para salir"
