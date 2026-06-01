# Ejecutar desde cualquier sitio: clic derecho -> Ejecutar con PowerShell
# Requiere: DBeaver conectado a master_db (127.0.0.1:5441) y POSTGRES_PASSWORD en .env

$Proyecto = Split-Path $PSScriptRoot -Parent
Set-Location $Proyecto

Write-Host "Carpeta del proyecto: $Proyecto" -ForegroundColor Gray
Write-Host "Comprueba DBeaver: master_db conectado (enchufe verde)." -ForegroundColor Yellow
Write-Host ""

$env:ADMIN_PASSWORD = '123456789A!'

& "$Proyecto\.venv\Scripts\python.exe" "$Proyecto\scripts\asegurar_admin_linda.py" --production

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Fallo. Si ves 'connection timeout':" -ForegroundColor Red
    Write-Host "  1. Conecta master_db en DBeaver y espera 5 segundos."
    Write-Host "  2. Vuelve a ejecutar este script."
    Write-Host ""
}

Write-Host ""
Write-Host "Pulsa Enter para cerrar."
Read-Host
