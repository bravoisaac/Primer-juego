$ErrorActionPreference = 'Stop'
$tenFeEditor = 'C:\Program Files\Unity\Hub\Editor\6000.3.26f1\Editor\Unity.exe'
if (-not (Test-Path -LiteralPath $tenFeEditor)) { throw 'Instala o selecciona Unity 6000.3.26f1.' }
New-Item -ItemType Directory -Force -Path (Join-Path $PSScriptRoot 'Logs') | Out-Null
$buildArguments = '-batchmode -nographics -quit -projectPath . -executeMethod TenFe.Editor.ProjectTools.ValidateExistingAndBuild -logFile Logs/build.log'
$editorProcess = Start-Process -FilePath $tenFeEditor -WorkingDirectory $PSScriptRoot -ArgumentList $buildArguments -WindowStyle Hidden -Wait -PassThru
if ($editorProcess.ExitCode -ne 0) { throw 'La compilación falló. Revisa Logs/build.log.' }
$playerPath = Join-Path $PSScriptRoot 'Builds\Windows\TenFe.exe'
$smokeProcess = Start-Process -FilePath $playerPath -WorkingDirectory $PSScriptRoot -ArgumentList '--smoke-test -screen-width 1280 -screen-height 720 -logFile Logs/runtime.log' -WindowStyle Hidden -Wait -PassThru
if ($smokeProcess.ExitCode -ne 0) { throw 'La validación falló. Revisa Docs/Validation/runtime.txt y Logs/runtime.log.' }
Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Docs\Validation\core.txt')
Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Docs\Validation\runtime.txt')
