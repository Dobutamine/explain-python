"""Long-run stability smoke test for `baseline_mongo.json`.

This script loads the model, advances a fixed number of simulation steps,
and prints simple min/max/last statistics for selected monitor and heart
signals to detect numerical instability.
"""

import math
from model_engine import ModelEngine


def main():
    """Run a 10k-step soak test and print tracked signal statistics.

    Raises:
        RuntimeError: If any tracked numeric value becomes non-finite.
    """
    steps = 10000
    engine = ModelEngine()
    engine.load_json_file("definitions/baseline_mongo.json")

    monitor = engine.models.get("Monitor")
    heart = engine.models.get("Heart")

    track_fields = [
        ("Monitor", "heart_rate"),
        ("Monitor", "abp_mean"),
        ("Monitor", "pap_mean"),
        ("Monitor", "cvp"),
        ("Monitor", "spo2"),
        ("Monitor", "resp_rate"),
        ("Heart", "heart_rate"),
        ("Heart", "ecg_signal"),
    ]

    stats = {
        key: {"min": float("inf"), "max": float("-inf"), "last": None}
        for key in track_fields
    }

    for i in range(1, steps + 1):
        engine.step_model()

        objs = {"Monitor": monitor, "Heart": heart}
        for owner, field in track_fields:
            obj = objs.get(owner)
            if obj is None or not hasattr(obj, field):
                continue

            value = getattr(obj, field)
            if isinstance(value, (int, float)):
                fv = float(value)
                if not math.isfinite(fv):
                    raise RuntimeError(
                        f"Non-finite value at step {i}: {owner}.{field}={fv}"
                    )

                stat = stats[(owner, field)]
                stat["min"] = min(stat["min"], fv)
                stat["max"] = max(stat["max"], fv)
                stat["last"] = fv

    print(
        f"PASS: completed {steps} steps; initialized={engine.is_initialized}; models={len(engine.models)}"
    )
    for owner, field in track_fields:
        stat = stats[(owner, field)]
        if stat["last"] is None:
            print(f"{owner}.{field}: n/a")
        else:
            print(
                f"{owner}.{field}: last={stat['last']:.6g}, min={stat['min']:.6g}, max={stat['max']:.6g}"
            )


if __name__ == "__main__":
    main()
