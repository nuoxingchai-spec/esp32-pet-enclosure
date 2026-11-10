@echo off
setlocal
set "BLENDER=C:\Users\admin\Downloads\blender-5.4.0-alpha+main.4f97ee24309d-windows.amd64-release\blender-5.4.0-alpha+main.4f97ee24309d-windows.amd64-release\blender.exe"
set "HERE=%~dp0"

if not exist "%BLENDER%" (
    echo Blender not found:
    echo %BLENDER%
    pause
    exit /b 1
)

if "%~1"=="" (
    start "" "%BLENDER%" --python "%HERE%start_mcp.py"
) else (
    start "" "%BLENDER%" "%~1" --python "%HERE%start_mcp.py"
)

endlocal
