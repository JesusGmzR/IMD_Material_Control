@echo off
REM Script de compilación para IMD Material Control Desktop App
echo ==========================================
echo    IMD MATERIAL CONTROL - COMPILACION
echo ==========================================
echo.

echo [1/5] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo [2/5] Verificando dependencias...
python -c "import flask, webview, mysql.connector; print('✓ Dependencias OK')"
if errorlevel 1 (
    echo Error: Faltan dependencias. Ejecute: pip install flask flask-cors pywebview mysql-connector-python
    pause
    exit /b 1
)

echo [3/5] Limpiando compilaciones anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo [4/5] Compilando aplicación con PyInstaller...
pyinstaller --clean imd_app.spec
if errorlevel 1 (
    echo Error en la compilación
    pause
    exit /b 1
)

echo [5/5] Verificando compilación...
if exist "dist\IMD_MaterialControl.exe" (
    echo.
    echo ==========================================
    echo    ✓ COMPILACION EXITOSA
    echo ==========================================
    echo.
    echo Archivo generado: dist\IMD_MaterialControl.exe
    echo Tamaño: 
    for %%I in ("dist\IMD_MaterialControl.exe") do echo %%~zI bytes
    echo.
    echo Para probar: cd dist && IMD_MaterialControl.exe
    echo.
) else (
    echo ❌ Error: No se generó el ejecutable
    pause
    exit /b 1
)

echo ¿Desea abrir la carpeta de distribución? (Y/N)
set /p respuesta=
if /i "%respuesta%"=="Y" (
    explorer dist
)

pause