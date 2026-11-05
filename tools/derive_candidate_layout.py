"""Compatibility entry point; implementation: tools/kernel-config/derive_candidate_layout.py."""
import runpy
import sys
from pathlib import Path

_target = Path(__file__).resolve().parent / "kernel-config" / "derive_candidate_layout.py"
sys.path.insert(0, str(_target.parent))
globals().update(runpy.run_path(str(_target), run_name=__name__))
