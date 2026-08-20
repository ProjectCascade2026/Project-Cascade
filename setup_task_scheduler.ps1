# PowerShell script to set up Windows Task Scheduler for automated Substack imports
# Run as Administrator

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator!"
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then try again."
    Exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Substack Import Task Scheduler" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Get the script path
$scriptPath = "C:\Users\Dr. Strangelove\cascade_app_package\import_substack_imap.py"
$pythonPath = "C:\Python39\python.exe"
$workingDir = "C:\Users\Dr. Strangelove\cascade_app_package"

# Verify files exist
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

# Task details
$taskName = "Import Substack Emails"
$taskDescription = "Daily import of Substack research into Project Cascade"
$taskTime = "08:00"  # 8:00 AM

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "⚠️  Task '$taskName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Replace existing task? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Cancelled." -ForegroundColor Yellow
        Exit 0
    }
    # Delete existing task
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ Deleted existing task`n" -ForegroundColor Green
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# Create trigger (daily at 8:00 AM)
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At $taskTime

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Create principal (run under current user)
$principal = New-ScheduledTaskPrincipal `
    -UserID "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description $taskDescription `
        -Force | Out-Null

    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    Write-Host "`n📋 Task Details:" -ForegroundColor Cyan
    Write-Host "   Name: $taskName" -ForegroundColor White
    Write-Host "   Schedule: Daily at $taskTime" -ForegroundColor White
    Write-Host "   Python: $pythonPath" -ForegroundColor White
    Write-Host "   Script: $scriptPath" -ForegroundColor White
    Write-Host "   Working Dir: $workingDir" -ForegroundColor White

    # Test run the task
    Write-Host "`n🧪 Running task now to verify..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName

    Start-Sleep -Seconds 3

    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "`n✅ Task executed at: $($taskInfo.LastRunTime)" -ForegroundColor Green
    Write-Host "✅ Task status: $($taskInfo.LastTaskResult)" -ForegroundColor Green

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ Setup Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`n📅 Your Substack emails will be imported daily at $taskTime" -ForegroundColor Green
    Write-Host "🎯 Check your dashboard to see new research appearing automatically`n" -ForegroundColor Green

} catch {
    Write-Error "Failed to create task: $_"
    Exit 1
}
