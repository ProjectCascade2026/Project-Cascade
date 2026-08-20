#!/usr/bin/env python3
"""
Backup Project Cascade v1 - Python version
Creates timestamped backup of entire cascade_app_package directory
Generates BACKUP_MANIFEST.txt with project statistics
"""

import os
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

def get_git_info(repo_path):
    """Get git statistics from repository"""
    try:
        # Get commit count
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        commit_count = len(result.stdout.strip().split('\n')) if result.stdout else 0

        # Get latest commit
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        latest_commit = result.stdout.strip() if result.stdout else "N/A"

        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        current_branch = result.stdout.strip() if result.stdout else "N/A"

        return {
            'commits': commit_count,
            'latest': latest_commit,
            'branch': current_branch
        }
    except Exception as e:
        return {
            'commits': 'N/A',
            'latest': 'N/A',
            'branch': 'N/A'
        }

def get_database_stats(db_path):
    """Get record counts from cascade database"""
    stats = {}
    try:
        db = sqlite3.connect(db_path)
        c = db.cursor()
        tables = ['signals', 'research_findings', 'cascade_sequences', 'project_goals', 'amplitude_watch', 'cascade_nodes']

        for table in tables:
            try:
                c.execute(f'SELECT COUNT(*) FROM {table}')
                count = c.fetchone()[0]
                stats[table] = count
            except:
                stats[table] = 0

        db.close()
    except Exception as e:
        print(f"Warning: Could not read database stats: {e}")

    return stats

def main():
    # Define paths
    home_dir = os.path.expanduser("~")
    backup_dir = os.path.join(home_dir, "cascade_backups")
    project_dir = os.path.join(home_dir, "cascade_app_package")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"cascade_backup_{timestamp}")

    print("\n" + "="*60)
    print("Project Cascade v1 - Backup")
    print("="*60 + "\n")

    # Create backup directory if needed
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")

    # Copy project
    print(f"Backing up cascade_app_package to {backup_path}...")
    try:
        shutil.copytree(project_dir, backup_path)
        print("Project copied successfully")
    except Exception as e:
        print(f"ERROR: Failed to copy project: {e}")
        return False

    # Create manifest
    print("Generating backup manifest...")
    manifest_path = os.path.join(backup_path, "BACKUP_MANIFEST.txt")

    git_info = get_git_info(backup_path)
    db_stats = get_database_stats(os.path.join(backup_path, "cascade_data.db"))

    manifest_content = f"""Project Cascade v1 - Backup Manifest
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup Location: {backup_path}

Project Statistics:
- Total commits: {git_info['commits']}
- Latest commit: {git_info['latest']}
- Branch: {git_info['branch']}

Key Files:
- cascade_app.py (main dashboard)
- cascade_db.py (database functions)
- cascade_data.db (SQLite database)
- update_project_goals.py (goals initialization)
- add_email_monitoring_goal.py (new goal)
- fresh_gmail_analysis.py (email analysis routine)

Database Contents (at backup time):
"""

    for table, count in db_stats.items():
        manifest_content += f"  {table}: {count} records\n"

    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        print(f"Manifest created: {manifest_path}")
    except Exception as e:
        print(f"WARNING: Could not create manifest: {e}")

    # List all backups
    print("\n" + "="*60)
    print("Backup Complete!")
    print("="*60)
    print(f"\nBackup location: {backup_path}")
    print(f"Manifest: {manifest_path}")
    print(f"\nAll backups in {backup_dir}:")

    try:
        backups = sorted(os.listdir(backup_dir))
        for backup in backups:
            print(f"  - {backup}")
    except:
        pass

    print()
    return True

if __name__ == '__main__':
    main()
