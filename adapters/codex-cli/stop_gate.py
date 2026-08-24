#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from mero_precision.cli import run_hook  # noqa: E402

raise SystemExit(run_hook("codex"))
