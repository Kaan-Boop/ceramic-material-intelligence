# Run from any directory after completing docs/PROTOTYPE.md setup.
# Keeps ownership of both child processes; Enter or Ctrl+C stops them.
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$webRoot = Join-Path $projectRoot 'apps/web'
$pythonExe = Join-Path $projectRoot 'storage/prototype/environment/Scripts/python.exe'
$nextCli = Join-Path $webRoot 'node_modules/next/dist/bin/next'
$logRoot = Join-Path $projectRoot 'storage/prototype/logs'
if (!(Test-Path -LiteralPath $pythonExe) -or !(Test-Path -LiteralPath $nextCli) -or !(Test-Path -LiteralPath (Join-Path $webRoot '.next/BUILD_ID'))) {
    throw 'Kurulum veya web derlemesi eksik. docs/PROTOTYPE.md adımlarını tamamlayın.'
}
foreach ($listenPort in @(8000, 3000)) {
    $probe = [System.Net.Sockets.TcpClient]::new()
    try { $probe.Connect('127.0.0.1', $listenPort); $occupied = $true }
    catch { $occupied = $false }
    finally { $probe.Dispose() }
    if ($occupied) { throw "Port $listenPort kullanımda. Mevcut sunucuyu kendi terminalinden kapatın; bu script onu sonlandırmaz." }
}
$nodeExe = (Get-Command node -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$runId = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
$env:NEXT_TELEMETRY_DISABLED = '1'
$apiProcess = $null
$webProcess = $null
try {
    $apiProcess = Start-Process -FilePath $pythonExe -ArgumentList @('-m', 'uvicorn', 'apps.api.app.main:app', '--host', '127.0.0.1', '--port', '8000', '--no-access-log') -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logRoot "$runId-api.log") -RedirectStandardError (Join-Path $logRoot "$runId-api-error.log")
    $webProcess = Start-Process -FilePath $nodeExe -ArgumentList @(('"' + $nextCli + '"'), 'start', '--hostname', '127.0.0.1', '--port', '3000') -WorkingDirectory $webRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logRoot "$runId-web.log") -RedirectStandardError (Join-Path $logRoot "$runId-web-error.log")
    $ready = $false
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if ($apiProcess.HasExited -or $webProcess.HasExited) { throw "Sunucu başlatılamadı. Log: $logRoot" }
        try {
            $health = Invoke-RestMethod 'http://127.0.0.1:3000/api/v1/health' -TimeoutSec 2
            if ($health.mode -eq 'LOCAL_RESEARCH_PROTOTYPE') { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (!$ready) { throw "Sunucu hazır olmadı. Log: $logRoot" }
    Write-Host 'Ceramic Glaze Lab hazır: http://127.0.0.1:3000'
    Write-Host 'Yalnızca bu bilgisayarda erişilebilir. Bu terminali açık bırakın.'
    Read-Host 'Sunucuları kapatmak için Enter' | Out-Null
} finally {
    foreach ($childProcess in @($webProcess, $apiProcess)) {
        if ($null -ne $childProcess -and !$childProcess.HasExited) { $childProcess.Kill(); $childProcess.WaitForExit() }
    }
}
