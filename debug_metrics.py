#!/usr/bin/env python3
"""Debug what get_metrics_summary returns"""

import sys
import os

# Add cascade_app_package to path
sys.path.insert(0, r'C:\Users\Dr. Strangelove\cascade_app_package')

try:
    from cascade_db import get_metrics_summary

    print("Testing get_metrics_summary()...")
    print("=" * 60)

    metrics = get_metrics_summary()

    print(f"Type: {type(metrics)}")
    print(f"Value: {metrics}")
    print(f"Keys: {list(metrics.keys()) if isinstance(metrics, dict) else 'N/A'}")

    if isinstance(metrics, dict):
        print("\nIndividual values:")
        for key, val in metrics.items():
            print(f"  {key}: {val}")

    print("\n" + "=" * 60)
    print("✓ Function works correctly" if metrics else "✗ Function returned empty/None")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
