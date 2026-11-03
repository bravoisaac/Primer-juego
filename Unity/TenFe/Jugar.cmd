@echo off
if not exist "%~dp0Builds\Windows\TenFe.exe" (
  echo Falta la compilacion. Abre Unity y usa Ten Fe - Compilar Windows.
  pause
  exit /b 1
)
start "" "%~dp0Builds\Windows\TenFe.exe"
