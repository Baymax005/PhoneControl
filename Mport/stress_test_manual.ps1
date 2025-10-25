# MANUAL STRESS TEST SETUP
# Run this AFTER you've started server and client manually

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "         MPORT STRESS TEST - MANUAL MODE" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "BEFORE running this script, make sure:" -ForegroundColor Yellow
Write-Host "  [1] Server is running: python Mport/server/tunnel_server.py" -ForegroundColor White
Write-Host "  [2] Client is running: python Mport/client/quick_start.py" -ForegroundColor White
Write-Host "  [3] Wait ~5 seconds for client to register`n" -ForegroundColor White

$confirm = Read-Host "Are server and client running? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "`nPlease start them first:" -ForegroundColor Yellow
    Write-Host "  Terminal 1: python Mport/server/tunnel_server.py" -ForegroundColor Cyan
    Write-Host "  Terminal 2: python Mport/client/quick_start.py" -ForegroundColor Cyan
    Write-Host "  Then run this script again.`n" -ForegroundColor Cyan
    exit
}

# Connect ADB through tunnel
Write-Host "`n[SETUP] Connecting ADB through tunnel..." -ForegroundColor Cyan
adb disconnect localhost:8080 2>&1 | Out-Null
Start-Sleep -Seconds 1

$adbResult = adb connect localhost:8080
Write-Host "  $adbResult" -ForegroundColor Green

# Verify it worked
Write-Host "`n[VERIFY] Testing tunnel connection..." -ForegroundColor Cyan
$model = adb -s localhost:8080 shell getprop ro.product.model 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  SUCCESS! Phone model: $model" -ForegroundColor Green
    Write-Host "  Tunnel is working!`n" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Tunnel connection failed!" -ForegroundColor Red
    Write-Host "  Make sure server and client are running.`n" -ForegroundColor Red
    exit
}

# Choose test type
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Choose stress test:" -ForegroundColor Yellow
Write-Host "  1 - Quick Test (~30 seconds, basic load)" -ForegroundColor White
Write-Host "  2 - Full Test (~5 minutes, comprehensive)" -ForegroundColor White
$choice = Read-Host "Enter choice (1 or 2)"

Write-Host "`nStarting stress test...`n" -ForegroundColor Yellow
Start-Sleep -Seconds 1

if ($choice -eq "2") {
    python Mport/tests/stress_test.py
} else {
    python Mport/tests/quick_stress.py
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "         STRESS TEST COMPLETE!" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "The server and client are still running." -ForegroundColor Yellow
Write-Host "Check their terminals for statistics and performance data.`n" -ForegroundColor Yellow
