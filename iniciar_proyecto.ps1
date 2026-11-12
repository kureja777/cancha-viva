$runtime = Get-AppxPackage -Name 'OpenAI.CodexPrimaryRuntime*' | Sort-Object Version -Descending | Select-Object -First 1
if (-not $runtime) { throw 'No se encontro el runtime de Codex. Consulta README.md.' }
& (Join-Path $runtime.InstallLocation 'dependencies\python\python.exe') -X utf8 (Join-Path $PSScriptRoot 'iniciar_todo.py')
