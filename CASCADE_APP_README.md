# Project Cascade — Standalone Application

**Status**: ✅ Built and ready to launch

## What's Been Built

A **Python-based standalone application** with:

- **SQLite Database** (`cascade_data.db`) - Persistent, file-based storage
- **Streamlit Dashboard** - Interactive web interface with 8 primary sections
- **Auto-update Watcher** - Monitors markdown files and re-imports on change
- **Data Importer** - Parses existing markdown files into database on first run

## Architecture

```
cascade_db.py              → Database schema & operations
cascade_importer.py        → Data import from markdown files
cascade_watcher.py         → File change monitoring (auto-update)
cascade_app.py             → Streamlit dashboard (8 sections)
launcher.py                → Single entry point to start everything
cascade_data.db            → SQLite database (created on first run)
```

## 8 Primary Sections

1. **Summary** — Key metrics, active nodes, recent signals
2. **Today's Progress** — Daily signal counts, severity distribution, node trends
3. **Mission and Goals** — Framework overview, reference points, strategic goals
4. **Amplitude** — Node escalation visualization and trends
5. **Cascading Nodes Visualizing** — CASCADE sequence details, node activation matrix
6. **Systematic Underestimation** — Underestimation metrics and trends
7. **Granularity** — Detailed signal breakdown by domain, severity, source
8. **Appendix** — Baseline return failures, data schema reference

## How to Run

### Quick Start (Recommended)

```bash
cd /home/claude/confluence
python3 launcher.py
```

This will:
1. Check/install dependencies (streamlit, pandas, plotly, watchdog)
2. Initialize database and import data from existing markdown files
3. Launch Streamlit dashboard at `http://localhost:8501`

### Manual Start

```bash
cd /home/claude/confluence

# Initialize database and import data
python3 cascade_importer.py

# In one terminal: start the file watcher
python3 cascade_watcher.py

# In another terminal: launch Streamlit
streamlit run cascade_app.py
```

## Data Import

On first run, the importer will parse:
- `confluence_state.md` → Reference points (Amplitude, Frequency, etc.)
- `CASCADING_NODES_WATCH_LOG.md` → CASCADE sequences (10 documented)
- `BASELINE_RETURN_FAILURE_RESEARCH_20260818.md` → Geographic baseline shifts

Current import status:
- ✅ 13 Cascade Nodes
- ✅ 10 CASCADE Sequences
- ✅ 3+ Baseline Failures
- ✅ Reference point framework

## Auto-Update

The file watcher monitors these files for changes:
- `confluence_state.md`
- `CASCADING_NODES_WATCH_LOG.md`
- `BASELINE_RETURN_FAILURE_RESEARCH_20260818.md`

When any are modified, the database re-imports automatically (no manual refresh needed).

## Database Files

- **`cascade_data.db`** - Main database (SQLite)
  - Location: `/home/claude/confluence/`
  - Size: ~50-100KB (grows as you add data)
  - Portable: Can be backed up or moved easily

## Stability Advantages

✅ **Separation of Concerns** - Data (database) is separate from UI (Streamlit)
✅ **Modular** - Each section is independent; changes don't break others
✅ **Persistent** - Data survives app restarts
✅ **Extensible** - Easy to add new metrics, visualizations, or analysis
✅ **Queryable** - Direct SQL access to database for custom analysis

## Next Steps

1. **Run the app**: `python3 launcher.py`
2. **Review the initial state** with imported data
3. **Request enhancements** - Sections to modify, visualizations to add, metrics to track
4. **Add data** - New signals, cascade observations, or baseline failures

The architecture is stable and built to handle incremental refinement without degradation.

## Files Location

All application files are in `/home/claude/confluence/`:
```
/home/claude/confluence/
├── cascade_db.py                          # Database
├── cascade_importer.py                    # Data import
├── cascade_watcher.py                     # Auto-update watcher
├── cascade_app.py                         # Streamlit dashboard
├── launcher.py                            # Entry point ← Run this
├── cascade_data.db                        # Data (created on first run)
└── CASCADE_APP_README.md                  # This file
```

---

**Built on 2026-08-18**  
**Architecture**: Standalone Python + SQLite + Streamlit  
**Status**: Ready for deployment
