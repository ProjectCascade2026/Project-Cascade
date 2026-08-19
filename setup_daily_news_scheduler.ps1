# PowerShell script to set up Windows Task Scheduler for daily news headline scan
# Runs DAILY at 07:00 AM (first in the daily sequence)

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator!"
    Exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Daily News Headline Scan Scheduler" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$scriptPath = "C:\Users\Dr. Strangelove\cascade_app_package\import_daily_news_headlines.py"
$pythonPath = "C:\Python39\python.exe"
$workingDir = "C:\Users\Dr. Strangelove\cascade_app_package"

if (!(Test-Path $pythonPath)) {
    Write-Error "Python not found at $pythonPath"
    Exit 1
}

if (!(Test-Path $scriptPath)) {
    Write-Error "Script not found at $scriptPath"
    Exit 1
}

Write-Host "✅ Python found: $pythonPath" -ForegroundColor Green
Write-Host "✅ Script found: $scriptPath`n" -ForegroundColor Green

$taskName = "Daily News Headline Scan"
$taskDescription = "Daily scan of news headlines for infrastructure incidents, supply chain disruptions, and geopolitical events with cascade implications"

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "⚠️  Task '$taskName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Replace existing task? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Cancelled." -ForegroundColor Yellow
        Exit 0
    }
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ Deleted existing task`n" -ForegroundColor Green
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# Create trigger (daily at 07:00 AM)
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "07:00 AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Create principal
$principal = New-ScheduledTaskPrincipal `
    -UserID "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description $taskDescription `
        -Force | Out-Null

    Write-Host "✅ Daily news headline scan scheduled!" -ForegroundColor Green
    Write-Host "`n📋 Task Details:" -ForegroundColor Cyan
    Write-Host "   Name: $taskName" -ForegroundColor White
    Write-Host "   Schedule: Every day at 07:00 AM" -ForegroundColor White
    Write-Host "   Data Sources: News headlines (infrastructure, geopolitical, supply chain)" -ForegroundColor White

    Write-Host "`n🧪 Running task now to verify..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName

    Start-Sleep -Seconds 3

    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "`n✅ Task executed successfully" -ForegroundColor Green

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Setup Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`n📅 Your complete daily automation schedule:" -ForegroundColor Green
    Write-Host "   • Daily: 07:00 AM - News headline scan (early warning)" -ForegroundColor White
    Write-Host "   • Daily: 08:00 AM - Substack email import" -ForegroundColor White
    Write-Host "   • Daily: 09:00 AM - Critical infrastructure monitoring" -ForegroundColor White
    Write-Host "   • Weekly: Monday 10:00 AM - Institutional data import" -ForegroundColor White
    Write-Host "`n🎯 Dashboard auto-updates with new cascade signals and findings`n" -ForegroundColor Green

} catch {
    Write-Error "Failed to create task: $_"
    Exit 1
}
