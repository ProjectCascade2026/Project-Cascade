# Backup Project Cascade v1
$BackupDir = "$env:USERPROFILE\cascade_backups"
$ProjectDir = "$env:USERPROFILE\cascade_app_package"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupPath = "$BackupDir\cascade_backup_$Timestamp"

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "Created backup directory: $BackupDir"
}

# Copy entire project
Write-Host "Backing up cascade_app_package to $BackupPath..."
Copy-Item -Path $ProjectDir -Destination $BackupPath -Recurse -Force

# Create backup manifest
$ManifestPath = "$BackupPath\BACKUP_MANIFEST.txt"
$ManifestContent = @"
Project Cascade v1 - Backup Manifest
Created: $(Get-Date)
Backup Location: $BackupPath

Project Statistics:
- Total commits: $(cd $BackupPath; git log --oneline | wc -l)
- Latest commit: $(cd $BackupPath; git log --oneline -1)
- Branch: $(cd $BackupPath; git branch --show-current)

Key Files:
- cascade_app.py (main dashboard)
- cascade_db.py (database functions)
- cascade_data.db (SQLite database)
- update_project_goals.py (goals initialization)
- add_email_monitoring_goal.py (new goal)
- fresh_gmail_analysis.py (email analysis routine)

Database Contents (at backup time):
"@

cd $BackupPath
$DbStats = python -c "
import sqlite3
db = sqlite3.connect('cascade_data.db')
c = db.cursor()
tables = ['signals', 'research_findings', 'cascade_sequences', 'project_goals', 'amplitude_watch', 'cascade_nodes']
for table in tables:
    c.execute(f'SELECT COUNT(*) FROM {table}')
    count = c.fetchone()[0]
    print(f'  {table}: {count} records')
db.close()
"

$ManifestContent += $DbStats

$ManifestContent | Out-File -FilePath $ManifestPath -Encoding UTF8

Write-Host ""
Write-Host "Backup complete!"
Write-Host "Backup location: $BackupPath"
Write-Host "Manifest: $ManifestPath"
Write-Host ""
Write-Host "All backups: $BackupDir"
ls $BackupDir | ForEach-Object { Write-Host "  - $($_.Name)" }
