@echo off
REM Push cascade_app.py fix to GitHub
cd /d "C:\Users\Dr. Strangelove\cascade_app_package"

REM Stage the fixed file
git add cascade_app.py

REM Commit with descriptive message
git commit -m "Fix: Safe category index handling in goal editing (ValueError fix)"

REM Push to remote
git push origin main

echo.
echo Push complete! Check Streamlit Cloud for automatic redeployment.
pause
