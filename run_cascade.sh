#!/bin/bash
# Project Cascade Launcher Script

set -e

cd "$(dirname "$0")"

echo "🚀 Project Cascade Startup"
echo "=========================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Check/install dependencies
echo ""
echo "📦 Checking dependencies..."

packages=(
    "streamlit"
    "pandas"
    "plotly"
    "watchdog"
)

for package in "${packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "  ✓ $package"
    else
        echo "  ⬇ Installing $package..."
        pip install "$package" --quiet
    fi
done

# Initialize database and import data
echo ""
echo "💾 Initializing database..."
python3 cascade_importer.py

# Start file watcher in background
echo ""
echo "👁️  Starting file watcher..."
python3 cascade_watcher.py &
WATCHER_PID=$!

# Give watcher a moment to start
sleep 2

# Launch Streamlit app
echo ""
echo "🎯 Launching Streamlit app..."
echo "   Opening at http://localhost:8501"
echo ""

streamlit run cascade_app.py

# Clean up watcher on exit
trap "kill $WATCHER_PID 2>/dev/null" EXIT
