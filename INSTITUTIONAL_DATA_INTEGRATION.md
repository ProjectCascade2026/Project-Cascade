# Institutional Data Integration Guide

Automated weekly imports from NASA, NOAA, World Bank, FAO, and CGIAR via direct APIs (no webpage fetching).

## What Gets Imported

### 📡 NASA Earthdata
- Global temperature anomalies (MERRA-2)
- Precipitation patterns (IMERG)
- Vegetation stress indices (NDVI)
- Sea level rise tracking
- Arctic ice extent

### 📊 NOAA Climate Data
- Global monthly temperature anomalies
- Extreme weather event tracking
- Precipitation deviations
- Ocean heat content
- Sea level monitoring

### 🏦 World Bank Indicators
- Agricultural production indices
- Energy infrastructure access
- Food import dependency ratios
- Water stress by region
- Economic resilience indicators

### 🌾 FAO Food Systems
- Food Price Index (real-time)
- Agricultural production by commodity
- Food supply/demand balances
- Crop failure regions
- Fertilizer availability and prices

### 💧 CGIAR Water-Energy-Food Nexus
- Basin-scale water-energy-food analyses
- Institutional interplay assessments
- Cascade impact modeling
- Regional vulnerability indices

## Setup (5 minutes)

### Step 1: Test the script manually

```bash
cd C:\Users\Dr. Strangelove\cascade_app_package
python import_institutional_data.py
```

You should see:
```
✅ NASA Earthdata connection ready
✅ NOAA Climate Data connection ready
✅ World Bank API connection ready
✅ FAO API connection ready
✅ CGIAR Data Portal connection ready

✅ Institutional Data Import Complete!
   • Signals added: 5
   • Findings added: 5
```

### Step 2: Schedule weekly execution

**Right-click PowerShell** → **"Run as Administrator"** → Paste:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force; & "C:\Users\Dr. Strangelove\cascade_app_package\setup_institutional_scheduler.ps1"
```

This creates a weekly task: **Every Monday at 10:00 AM**

### Step 3: Verify in Task Scheduler

1. Open `taskschd.msc`
2. Look for **"Import Institutional Research Data"**
3. Should run successfully

## Your Complete Automation Schedule

| Time | Task | Frequency | Source |
|------|------|-----------|--------|
| **08:00 AM** | Import Substack Emails | **Daily** | Your subscribed researchers |
| **10:00 AM Monday** | Import Institutional Data | **Weekly** | NASA, NOAA, World Bank, FAO, CGIAR |

**Result:** Your dashboard updates automatically with:
- ✅ New cascade research from leading scientists (daily)
- ✅ Real-time climate/infrastructure monitoring data (weekly)
- ✅ Global food/water/energy indicators (weekly)

## What Appears in Dashboard

### Research Findings Page
- New findings from institutional sources with full citations
- Organized by cascade mechanism
- Confidence levels and supporting evidence

### System Dynamics Page
- Signal distribution across cascade nodes
- Real-time tracking of which systems are stressed

### Amplitude Page
- Node activation frequency over time
- Trends in cascading impacts

### Routines Page
- Shows both automated imports running
- Status and next execution times

## No Webpage Fetching

✅ **Advantages of API-based approach:**
- No permission prompts
- More reliable (APIs designed for automation)
- Structured data (JSON/CSV not HTML parsing)
- Respects institutional terms of service
- Runs unattended 100% of the time

## Technical Details

### How It Works

1. **Direct API calls** to institutional endpoints
2. **Parse structured data** (JSON, CSV)
3. **Extract cascade-relevant signals:**
   - Temperature anomalies → water stress node
   - Food price spikes → feedback amplification
   - Energy access gaps → infrastructure brittleness
   - Regional economic indicators → geopolitical risk
4. **Map to cascade mechanisms**
5. **Add to database** with source attribution

### Data Flow

```
NASA/NOAA/World Bank/FAO
        ↓
API Endpoints (no webpage)
        ↓
import_institutional_data.py
        ↓
Parse → Extract signals → Map to cascade model
        ↓
cascade_db.py
        ↓
Dashboard auto-updates
```

## Future Expansions

Once this is running smoothly, we can add:

1. **Real-time supply chain monitoring**
   - Semiconductor fab utilization (Intel, TSMC APIs)
   - Shipping data (port congestion, AIS tracking)
   - Commodity prices (real-time futures data)

2. **Climate tipping point indicators**
   - Arctic methane release monitoring
   - Greenland ice sheet velocity
   - Atlantic Meridional Overturning Circulation (AMOC)

3. **Geopolitical risk feeds**
   - Conflict event databases
   - Sanctions tracking
   - Migration flow data

4. **Infrastructure sensor data**
   - Grid frequency monitoring
   - Water system pressures
   - Agricultural soil moisture networks

All via APIs, all automated, all no-prompt.

## Troubleshooting

### Script runs but no data appears

**Check:** Task Scheduler logs in Windows Event Viewer
- Search for "Import Institutional Research Data"
- Look for errors in Application logs

### Task doesn't run at scheduled time

1. Verify Task Scheduler has the correct Python path
2. Confirm working directory is set correctly
3. Check network connectivity (required)

### Want to run immediately (don't wait for Monday)

In Task Scheduler, right-click "Import Institutional Research Data" → **Run**

## Files

| File | Purpose |
|------|---------|
| `import_institutional_data.py` | Main import script (API connections) |
| `setup_institutional_scheduler.ps1` | Creates weekly scheduled task |
| `config.ini` | Gmail credentials (for Substack) |

---

**Status:** ✅ Ready to deploy

**Your cascade research is now fully autonomous.**
