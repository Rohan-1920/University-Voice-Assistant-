$serviceName = "GIFTUniversityBot"
$botDir      = "D:\Calling Agent for Uni Students\university-ai-agent"
$nssmExe     = "$botDir\nssm.exe"
$uvicorn     = "C:\Users\Dr_Com\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\uvicorn.exe"

Write-Host "GIFT University Bot - Service Setup" -ForegroundColor Cyan

# 1. Check uvicorn exists
if (-not (Test-Path $uvicorn)) {
    Write-Host "uvicorn.exe nahi mila: $uvicorn" -ForegroundColor Red
    Write-Host "pip install uvicorn chala kar dobara try karein" -ForegroundColor Yellow
    exit 1
}
Write-Host "uvicorn found: $uvicorn" -ForegroundColor Green

# 2. Remove old service
Write-Host "Purani service hata raha hai..." -ForegroundColor Yellow
& $nssmExe stop   $serviceName 2>$null
& $nssmExe remove $serviceName confirm 2>$null
Start-Sleep -Seconds 1

# 3. Install service — uvicorn directly
Write-Host "Service install ho rahi hai..." -ForegroundColor Yellow
& $nssmExe install $serviceName $uvicorn "app.main:app --host 0.0.0.0 --port 8000"
& $nssmExe set $serviceName AppDirectory    $botDir
& $nssmExe set $serviceName DisplayName     "GIFT University AI Bot"
& $nssmExe set $serviceName Description     "GIFT University AI Admission Assistant 24/7"
& $nssmExe set $serviceName Start           SERVICE_AUTO_START
& $nssmExe set $serviceName AppStdout       "$botDir\bot.log"
& $nssmExe set $serviceName AppStderr       "$botDir\bot_error.log"
& $nssmExe set $serviceName AppRestartDelay 3000

# 4. Start
Write-Host "Service start ho rahi hai..." -ForegroundColor Yellow
& $nssmExe start $serviceName
Start-Sleep -Seconds 4

# 5. Check
$svc = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq "Running") {
    Write-Host ""
    Write-Host "Service chal rahi hai!" -ForegroundColor Green
    Write-Host "http://localhost:8000/demo" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Service start nahi hui. Error log:" -ForegroundColor Red
    Get-Content "$botDir\bot_error.log" -ErrorAction SilentlyContinue | Select-Object -Last 15
}

Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  Stop:  .\nssm.exe stop $serviceName"
Write-Host "  Start: .\nssm.exe start $serviceName"
Write-Host "  Logs:  Get-Content bot.log -Wait"
