@echo off
echo -------------------------------------------------------
echo Configurando remoto 'origin' para futuros push
echo -------------------------------------------------------

:: Verifica si estás en un repositorio Git
IF NOT EXIST ".git" (
    echo ERROR: Este directorio no es un repositorio Git.
    pause
    exit /b
)

:: Cambia el remoto origin a la URL deseada
set REMOTE_ORIGIN=https://github.com/Linxurs/minecito-app.git
git remote set-url origin %REMOTE_ORIGIN%

:: Verifica si existe el remoto upstream, si no, lo agrega
git remote | findstr /r /c:"^upstream$" >nul
if errorlevel 1 (
    echo Agregando remoto 'upstream'...
    git remote add upstream https://github.com/Linxurs/minecito-app.git
) else (
    echo Remoto 'upstream' ya existe.
)

echo.
echo Remotos configurados:
git remote -v

echo.
echo Listo! Los futuros 'git push' se enviarán a:
echo %REMOTE_ORIGIN%
pause
