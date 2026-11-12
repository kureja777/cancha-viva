@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -Command "$r = Get-AppxPackage -Name 'OpenAI.CodexPrimaryRuntime*' | Sort-Object Version -Descending | Select-Object -First 1; if ($r) { & (Join-Path $r.InstallLocation 'dependencies\python\python.exe') -X utf8 '.\iniciar_todo.py' --stop }"
