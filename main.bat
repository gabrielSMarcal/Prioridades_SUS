@echo off

if /i "%~1" neq "RUN" (
    start "Hosp - Main" cmd /k ""%~f0" RUN"
    exit /b
)

setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Criando ambiente virtual em .venv...
    py -m venv .venv
    if errorlevel 1 (
        python -m venv .venv
        if errorlevel 1 (
            echo Falha ao criar ambiente virtual.
            pause
            exit /b 1
        )
    )
)

call ".venv\Scripts\activate.bat"
python main.py

set "EXIT_CODE=%ERRORLEVEL%"
deactivate >nul 2>&1
echo.
echo Execucao finalizada com codigo %EXIT_CODE%.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul
exit /b %EXIT_CODE%