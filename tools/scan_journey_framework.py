"""Compatibility entry point; implementation: tools/journey/scan_journey_framework.py."""
import runpy
import sys
from pathlib import Path

_target = Path(__file__).resolve().parent / "journey" / "scan_journey_framework.py"
sys.path.insert(0, str(_target.parent))
globals().update(runpy.run_path(str(_target), run_name=__name__))
