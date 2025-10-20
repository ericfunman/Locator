@echo off
REM Script de lancement de Locator
REM Application de gestion locative

echo ========================================
echo    Demarrage de Locator
echo ========================================
echo.

REM Se placer dans le répertoire du script
cd /d "%~dp0"

echo Repertoire: %CD%
echo.

REM Définir le chemin vers conda
set CONDA_PATH=C:\Users\lapin\miniconda3\Scripts\conda.exe

REM Vérifier que conda existe
if not exist "%CONDA_PATH%" (
    echo ERREUR: Conda n'est pas trouve a l'emplacement : %CONDA_PATH%
    echo Veuillez verifier le chemin d'installation de Miniconda
    pause
    exit /b 1
)

echo Lancement de l'application Streamlit...
echo.
echo L'application sera disponible sur : http://localhost:8501
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo ========================================
echo.

REM Lancer Streamlit avec conda
"%CONDA_PATH%" run -p C:\Users\lapin\miniconda3 --no-capture-output streamlit run app.py

REM Si l'application s'arrête
echo.
echo ========================================
echo Application arretee
echo ========================================
pause
