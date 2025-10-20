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

REM Vérifier que conda est installé
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ERREUR: Conda n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Miniconda ou Anaconda
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
C:\Users\lapin\miniconda3\Scripts\conda.exe run -p C:\Users\lapin\miniconda3 --no-capture-output streamlit run app.py

REM Si l'application s'arrête
echo.
echo ========================================
echo Application arretee
echo ========================================
pause
