"""Basic smoke tests for Explain model definitions.

This script verifies that model definitions can be loaded and stepped without
raising runtime errors. By default, it tests all JSON definitions found in the
`definitions/` folder.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_engine import ModelEngine


def _find_definitions() -> list[Path]:
    """Return sorted definition files from the repository definitions folder."""
    return sorted((REPO_ROOT / "definitions").glob("*.json"))


def _run_one(definition_path: Path, steps: int) -> tuple[bool, str]:
    """Load and run one definition for a fixed number of steps."""
    engine = ModelEngine().load_json_file(str(definition_path))

    for _ in range(steps):
        engine.step_model()

    if not engine.is_initialized:
        return False, f"{definition_path.name}: engine is not initialized"

    if not engine.models:
        return False, f"{definition_path.name}: no models were instantiated"

    monitor = engine.models.get("Monitor") or engine.models.get("MON")
    if monitor is not None and hasattr(monitor, "heart_rate"):
        heart_rate = float(getattr(monitor, "heart_rate") or 0.0)
        if not math.isfinite(heart_rate):
            return False, f"{definition_path.name}: non-finite Monitor heart_rate"

    return True, (
        f"{definition_path.name}: initialized={engine.is_initialized}, "
        f"models={len(engine.models)}, steps={steps}"
    )


def main() -> int:
    """Run smoke tests and return process exit code."""
    parser = argparse.ArgumentParser(description="Run Explain smoke tests")
    parser.add_argument(
        "--steps",
        type=int,
        default=25,
        help="Number of step_model() iterations per definition (default: 25)",
    )
    parser.add_argument(
        "--definition",
        type=str,
        default=None,
        help="Optional single definition file name from definitions/ (e.g. baseline_neonate.json)",
    )
    args = parser.parse_args()

    if args.steps < 1:
        print("[FAIL] --steps must be >= 1")
        return 2

    if args.definition:
        definition_paths = [REPO_ROOT / "definitions" / args.definition]
    else:
        definition_paths = _find_definitions()

    if not definition_paths:
        print("[FAIL] No definition files found in definitions/")
        return 2

    failed = False
    for definition_path in definition_paths:
        if not definition_path.exists():
            print(f"[FAIL] {definition_path.name}: file not found")
            failed = True
            continue

        try:
            ok, message = _run_one(definition_path, steps=args.steps)
        except Exception as exc:
            ok, message = False, f"{definition_path.name}: exception={exc}"

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {message}")
        if not ok:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
