@echo off
REM ============================================================
REM  ACTUALIZAR - Descarga la ultima version del disenador.
REM  Doble clic sobre este archivo (necesita Git instalado).
REM ============================================================
cd /d "%~dp0"
echo Buscando actualizaciones...
echo.
git fetch origin
git switch main
git pull --ff-only origin main
echo.
echo Listo. Ya tenes la ultima version.
echo Podes cerrar esta ventana.
pause
