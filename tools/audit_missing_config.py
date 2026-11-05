"""Compatibility entry point; implementation: tools/kernel-config/audit_missing_config.py."""
import runpy
import sys
from pathlib import Path

_target = Path(__file__).resolve().parent / "kernel-config" / "audit_missing_config.py"
sys.path.insert(0, str(_target.parent))
globals().update(runpy.run_path(str(_target), run_name=__name__))
