@echo off
setlocal

set REPO_URL=https://github.com/Linxurs/minecito-app.git
set DEST_DIR=C:\Users\Estudiantes\AppData\Local\Linxurs\minecito-app

if exist "%DEST_DIR%" (
    if exist "%DEST_DIR%\.git" (
        echo El repositorio existe. Limpiando y actualizando...
        cd /d "%DEST_DIR%"
        git reset --hard
        git clean -fd
        git fetch origin
        git pull --rebase origin main
    ) else (
        echo El directorio existe pero no es un repositorio git. Borrando y clonando de nuevo...
        rmdir /s /q "%DEST_DIR%"
        git clone "%REPO_URL%" "%DEST_DIR%"
    )
) else (
    echo El directorio no existe. Clonando repositorio...
    git clone "%REPO_URL%" "%DEST_DIR%"
)

endlocal
pause
