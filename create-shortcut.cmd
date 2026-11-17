@echo off
chcp 65001 >nul
setlocal
set "PROJECT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\OneDrive - Personal\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\OneDrive\Desktop"

powershell -NoProfile -Command "$w = New-Object -ComObject WScript.Shell; $p = Join-Path $env:DESKTOP 'Prompt Assistant.lnk'; $s = $w.CreateShortcut($p); $s.TargetPath = Join-Path $env:PROJECT_DIR 'run.cmd'; $s.WorkingDirectory = $env:PROJECT_DIR; $s.IconLocation = (Join-Path $env:PROJECT_DIR 'PromptAssistant.ico') + ',0'; $s.Description = 'Prompt Assistant - local prompt workspace'; $s.Save(); Write-Host ('Created desktop shortcut: ' + $p)"
pause
