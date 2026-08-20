# PowerShell script to set up Windows Task Scheduler for institutional data imports
# Runs WEEKLY (complements daily Substack import)

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator!"
    Exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Institutional Data Scheduler" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$scriptPath = "C:\Users\Dr. Strangelove\cascade_app_package\import_institutional_data.py"
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

$taskName = "Import Institutional Research Data"
$taskDescription = "Weekly import of NASA, NOAA, World Bank, FAO, CGIAR data into Project Cascade"

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

# Create trigger (weekly on Monday at 10:00 AM)
$trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday `
    -At "10:00 AM"

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

    Write-Host "✅ Weekly institutional data import scheduled!" -ForegroundColor Green
    Write-Host "`n📋 Task Details:" -ForegroundColor Cyan
    Write-Host "   Name: $taskName" -ForegroundColor White
    Write-Host "   Schedule: Every Monday at 10:00 AM" -ForegroundColor White
    Write-Host "   Data Sources: NASA, NOAA, World Bank, FAO, CGIAR" -ForegroundColor White

    Write-Host "`n🧪 Running task now to verify..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName

    Start-Sleep -Seconds 3

    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "`n✅ Task executed successfully" -ForegroundColor Green

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Setup Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`n📅 Your automation schedule:" -ForegroundColor Green
    Write-Host "   • Daily: 08:00 AM - Substack email import" -ForegroundColor White
    Write-Host "   • Weekly: Monday 10:00 AM - Institutional data import" -ForegroundColor White
    Write-Host "`n🎯 Dashboard auto-updates with new cascade research`n" -ForegroundColor Green

} catch {
    Write-Error "Failed to create task: $_"
    Exit 1
}
