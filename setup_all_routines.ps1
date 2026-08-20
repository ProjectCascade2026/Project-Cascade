# Master scheduler setup - activates all 4 cascade automation routines
# Run as Administrator

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator!"
    Exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project Cascade - Full Automation Setup" -ForegroundColor Cyan
Write-Host "Activating all 4 daily/weekly routines" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$scriptDir = "C:\Users\Dr. Strangelove\cascade_app_package"
$routines = @(
    @{name="News Headline Scan"; script="setup_daily_news_scheduler.ps1"; time="07:00 AM"},
    @{name="Substack Email Import"; script="setup_task_scheduler.ps1"; time="08:00 AM"},
    @{name="Infrastructure Monitoring"; script="setup_daily_infrastructure_scheduler.ps1"; time="09:00 AM"},
    @{name="Institutional Data Import"; script="setup_institutional_scheduler.ps1"; time="Monday 10:00 AM"}
)

$completed = 0
$failed = 0

foreach ($routine in $routines) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Setting up: $($routine.name)" -ForegroundColor Yellow
    Write-Host "Schedule: $($routine.time)" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow

    $scriptPath = Join-Path $scriptDir $routine.script

    if (!(Test-Path $scriptPath)) {
        Write-Host "ERROR: Script not found - $scriptPath" -ForegroundColor Red
        $failed++
        continue
    }

    try {
        & $scriptPath
        $completed++
    } catch {
        Write-Host "ERROR: Failed to run $($routine.name)" -ForegroundColor Red
        Write-Host $_ -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Completed: $completed / 4" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed: $failed / 4" -ForegroundColor Red
}

Write-Host ""
Write-Host "Your Complete Automation Schedule:" -ForegroundColor Green
Write-Host "   * Daily 07:00 AM - News Headline Scan" -ForegroundColor White
Write-Host "   * Daily 08:00 AM - Substack Email Import" -ForegroundColor White
Write-Host "   * Daily 09:00 AM - Infrastructure Monitoring" -ForegroundColor White
Write-Host "   * Weekly Monday 10:00 AM - Institutional Data" -ForegroundColor White

Write-Host ""
Write-Host "Starting tomorrow at 07:00 AM, your dashboard will update with:" -ForegroundColor Green
Write-Host "   - Breaking infrastructure incidents and early warnings" -ForegroundColor White
Write-Host "   - Research findings from leading cascade scientists" -ForegroundColor White
Write-Host "   - Real-time food/commodity/infrastructure monitoring" -ForegroundColor White
Write-Host "   - Weekly authoritative institutional research" -ForegroundColor White

Write-Host ""
Write-Host "Dashboard: https://project-cascade-strangelove.streamlit.app/" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
if ($failed -eq 0) {
    Write-Host "SUCCESS: ALL ROUTINES ACTIVATED" -ForegroundColor Green
} else {
    Write-Host "WARNING: Check errors above" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
