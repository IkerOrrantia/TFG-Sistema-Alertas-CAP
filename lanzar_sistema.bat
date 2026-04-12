@echo off
title Lanzador Maestro RETIMF
echo ========================================
echo   INICIANDO ECOSISTEMA TFG - RETIMF
echo ========================================

:: 1. Lanzar el Panel Visual (Astro) en una nueva ventana
echo [+] 1/3 Iniciando Frontend (Astro)...
start "RETIMF - Panel Visual" cmd /k "npm run dev"

:: 2. Lanzar el Vigilante (Node.js) en una nueva ventana
echo [+] 2/3 Iniciando Monitor de Telemetría...
start "RETIMF - Vigilante" cmd /k "node monitor.js"

:: 3. Lanzar el Generador de Alertas (Python) en una nueva ventana
echo [+] 3/3 Iniciando Generador Interactivo...
cd backend
start "RETIMF - Centro de Control" cmd /k "python generador_alertas.py"
cd ..

:: 4. Esperar a que el servidor esté listo y abrir navegador
echo.
echo Esperando a que Astro arranque...
timeout /t 5 /nobreak > nul

echo [+] Abriendo Dashboard en el navegador...
start http://localhost:4321

echo ========================================
echo   ¡Todo en marcha y listo para la demo!
echo ========================================
echo Puedes minimizar esta ventana.
pause