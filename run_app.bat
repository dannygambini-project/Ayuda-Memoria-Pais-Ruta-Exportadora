@echo off
title PROMPERU - Ayuda Memoria Pais 2026
echo ========================================================
echo   PROMPERU - Sistema de Ayuda Memoria Pais 2026
echo   Direccion de Promocion de las Exportaciones
echo ========================================================
echo.
echo Iniciando servidor de aplicacion en http://127.0.0.1:8000 ...
echo Presione Ctrl + C para detener el servidor.
echo.
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
