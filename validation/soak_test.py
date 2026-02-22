"""Long-run soak tests for Explain model definitions.

This script performs a high-step simulation run to detect numerical drift or
non-finite values over time. It is intended for runtime stability validation.
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


TRACK_FIELDS = [
    ("Monitor", "heart_rate"),
    ("Monitor", "abp_mean"),
    ("Monitor", "pap_mean"),
    ("Monitor", "cvp"),
    ("Monitor", "spo2"),
    ("Monitor", "resp_rate"),
    ("Heart", "heart_rate"),
    ("Heart", "ecg_signal"),
]


def _resolve_definition(definition_name: str) -> Path:
    path = REPO_ROOT / "definitions" / definition_name
    if not path.exists():
        raise FileNotFoundError(f"definition not found: {path}")
    return path


def _resolve_owner(engine: ModelEngine, owner_name: str):
    if owner_name == "Monitor":
        return engine.models.get("Monitor") or engine.models.get("MON")
    return engine.models.get(owner_name)


def _run_soak(definition_name: str, steps: int, report_every: int) -> tuple[bool, str]:
    definition_path = _resolve_definition(definition_name)
    engine = ModelEngine().load_json_file(str(definition_path))

    if not engine.is_initialized:
        return False, f"{definition_name}: engine is not initialized"

    stats: dict[tuple[str, str], dict[str, float | int | None]] = {
        key: {"min": float("inf"), "max": float("-inf"), "last": None, "count": 0}
        for key in TRACK_FIELDS
    }

    for i in range(1, steps + 1):
        engine.step_model()

        for owner, field in TRACK_FIELDS:
            obj = _resolve_owner(engine, owner)
            if obj is None or not hasattr(obj, field):
                continue

            value = getattr(obj, field)
            if not isinstance(value, (int, float)):
                continue

            fv = float(value)
            if not math.isfinite(fv):
                return False, f"{definition_name}: non-finite value at step {i}: {owner}.{field}={fv}"

            item = stats[(owner, field)]
            item["min"] = min(float(item["min"]), fv)
            item["max"] = max(float(item["max"]), fv)
            item["last"] = fv
            item["count"] = int(item["count"]) + 1

        if report_every > 0 and i % report_every == 0:
            print(f"[INFO] {definition_name}: progress {i}/{steps}")

    monitored = sum(1 for item in stats.values() if int(item["count"]) > 0)
    summary = (
        f"{definition_name}: completed {steps} steps, initialized={engine.is_initialized}, "
        f"models={len(engine.models)}, monitored_fields={monitored}/{len(TRACK_FIELDS)}"
    )

    print(f"[PASS] {summary}")
    for owner, field in TRACK_FIELDS:
        item = stats[(owner, field)]
        if int(item["count"]) == 0:
            print(f"  - {owner}.{field}: n/a")
            continue
        print(
            f"  - {owner}.{field}: last={float(item['last']):.6g}, "
            f"min={float(item['min']):.6g}, max={float(item['max']):.6g}"
        )

    return True, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Explain soak test")
    parser.add_argument(
        "--definition",
        type=str,
        default="baseline_neonate.json",
        help="Definition file in definitions/ (default: baseline_neonate.json)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=10000,
        help="Number of simulation steps to run (default: 10000)",
    )
    parser.add_argument(
        "--report-every",
        type=int,
        default=2000,
        help="Print progress every N steps; use 0 to disable (default: 2000)",
    )
    args = parser.parse_args()

    if args.steps < 1:
        print("[FAIL] --steps must be >= 1")
        return 2

    if args.report_every < 0:
        print("[FAIL] --report-every must be >= 0")
        return 2

    try:
        ok, message = _run_soak(args.definition, args.steps, args.report_every)
    except Exception as exc:
        ok, message = False, f"{args.definition}: exception={exc}"

    if not ok:
        print(f"[FAIL] {message}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
