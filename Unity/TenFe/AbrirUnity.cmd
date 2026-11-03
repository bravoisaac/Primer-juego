@echo off
set "TENFE_EDITOR=C:\Program Files\Unity\Hub\Editor\6000.3.26f1\Editor\Unity.exe"
if not exist "%TENFE_EDITOR%" (
  echo Abre Unity Hub y agrega la carpeta que contiene este archivo.
  pause
  exit /b 1
)
start "" "%TENFE_EDITOR%" -projectPath "%~dp0."
