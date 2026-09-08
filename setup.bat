@echo off
echo ========================================
echo INSTALANDO AGENTE ESTUDIOSO
echo ========================================
echo.

echo 📦 Instalando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado!
    echo Por favor, baixe em python.org
    pause
    exit
)
echo ✅ Python encontrado!

echo.
echo 📦 Instalando bibliotecas...
echo (pode demorar alguns minutos)

pip install pandas numpy requests websocket-client scikit-learn gTTS playsound colorama schedule python-dotenv ta

if errorlevel 1 (
    echo ❌ Erro na instalacao!
    pause
    exit
)

echo.
echo ✅ INSTALACAO CONCLUIDA!
echo.
echo 🚀 Para rodar o agente, digite:
echo    python main.py
echo.
pause