#!/usr/bin/env python3
"""Submission-audit reconstruction; not the missing historical interactive code."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1]/'tools/audit_screen.py'),run_name='__main__')
