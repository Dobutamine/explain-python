from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_engine import ModelEngine


def _load_engine(definition_name: str) -> ModelEngine:
    definition_path = REPO_ROOT / "definitions" / definition_name
    return ModelEngine().load_json_file(str(definition_path))


def check_baseline() -> tuple[bool, str]:
    engine = _load_engine("baseline.json")
    engine.step_model()
    required = ["PDA", "MOB", "SHUNTS", "MVU", "MVU_ART"]
    ok = engine.is_initialized and all(name in engine.models for name in required)
    return ok, f"baseline: initialized={engine.is_initialized}, required_present={ok}"


def check_pda() -> tuple[bool, str]:
    engine = _load_engine("pda.json")
    engine.step_model()
    pda = engine.models.get("PDA")
    if pda is None:
        return False, "pda: PDA model missing"
    ok = float(getattr(pda, "res_ao", 0.0) or 0.0) > 0.0 and float(getattr(pda, "res_pa", 0.0) or 0.0) > 0.0
    return ok, f"pda: res_ao={getattr(pda, 'res_ao', None):.3f}, res_pa={getattr(pda, 'res_pa', None):.3f}"


def check_shunts() -> tuple[bool, str]:
    engine = _load_engine("shunts.json")
    engine.step_model()
    shunts = engine.models.get("SHUNTS")
    if shunts is None:
        return False, "shunts: SHUNTS model missing"
    ok = float(getattr(shunts, "res_fo", 0.0) or 0.0) > 0.0 and float(getattr(shunts, "res_vsd", 0.0) or 0.0) > 0.0
    return ok, f"shunts: res_fo={getattr(shunts, 'res_fo', None):.3f}, res_vsd={getattr(shunts, 'res_vsd', None):.3f}"


def check_placenta() -> tuple[bool, str]:
    engine = _load_engine("placenta.json")
    engine.step_model()
    placenta = engine.models.get("PLACENTA")
    if placenta is None:
        return False, "placenta: PLACENTA model missing"
    required = ["PL_GASEX", "UMB_ART", "UMB_VEN", "PLF", "PLM", "AD_UMB_ART", "UMB_VEN_IVCI"]
    has_required = all(name in engine.models for name in required)
    ok = bool(getattr(placenta, "placenta_running", False)) and has_required
    return ok, (
        f"placenta: running={getattr(placenta, 'placenta_running', None)}, "
        f"umb_art_flow={getattr(placenta, 'umb_art_flow', None):.6f}, "
        f"umb_ven_flow={getattr(placenta, 'umb_ven_flow', None):.6f}"
    )


def check_fluids() -> tuple[bool, str]:
    engine = _load_engine("fluids.json")
    fluids = engine.models.get("FL")
    target = engine.models.get("VLB")
    if fluids is None or target is None:
        return False, "fluids: FL or VLB model missing"

    before = float(getattr(target, "vol", 0.0) or 0.0)
    fluids.add_volume(30, in_time=0.03, fluid_in="normal_saline", site="VLB")
    engine.step_model()
    engine.step_model()
    after = float(getattr(target, "vol", 0.0) or 0.0)
    ok = after > before
    return ok, f"fluids: before={before:.6f}, after={after:.6f}, infused={ok}"


def check_ans() -> tuple[bool, str]:
    engine = _load_engine("ans.json")
    ans = engine.models.get("ANS")
    eff = engine.models.get("ANS_EFF")
    aff = engine.models.get("ANS_AFF")
    target = engine.models.get("R1")

    if ans is None or eff is None or aff is None or target is None:
        return False, "ans: ANS, ANS_AFF, ANS_EFF, or R1 model missing"

    before = float(getattr(target, "r_factor_ps", 1.0) or 1.0)
    engine.step_model()
    after = float(getattr(target, "r_factor_ps", 1.0) or 1.0)
    ok = after != before
    return ok, f"ans: active={getattr(ans, 'ans_active', None)}, r_factor_ps before={before:.6f}, after={after:.6f}, firing={getattr(eff, 'firing_rate', 0.0):.6f}"


def check_ecls() -> tuple[bool, str]:
    engine = _load_engine("ecls.json")
    ecls = engine.models.get("ECLS")
    required = [
        "ECLS_DRAINAGE",
        "ECLS_TUBIN",
        "ECLS_PUMP",
        "ECLS_OXY",
        "ECLS_TUBOUT",
        "ECLS_RETURN",
        "ECLS_GASIN",
        "ECLS_GASOXY",
        "ECLS_GASOUT",
        "ECLS_GASEX",
    ]
    if ecls is None or not all(name in engine.models for name in required):
        return False, "ecls: ECLS controller or required subcomponents missing"

    for _ in range(120):
        engine.step_model()

    blood_flow = float(getattr(ecls, "blood_flow", 0.0) or 0.0)
    p_art = float(getattr(ecls, "p_art", 0.0) or 0.0)
    ok = bool(getattr(ecls, "ecls_running", False)) and p_art == p_art
    return ok, f"ecls: running={getattr(ecls, 'ecls_running', None)}, blood_flow={blood_flow:.6f}, p_art={p_art:.3f}"


def check_ventilator() -> tuple[bool, str]:
    engine = _load_engine("ventilator.json")
    vent = engine.models.get("VENT")
    required = [
        "VENT_GASIN",
        "VENT_GASCIRCUIT",
        "VENT_GASOUT",
        "VENT_INSP_VALVE",
        "VENT_ETTUBE",
        "VENT_EXP_VALVE",
        "DS",
        "MOUTH_DS",
    ]
    if vent is None or not all(name in engine.models for name in required):
        return False, "ventilator: controller or required circuit components missing"

    for _ in range(120):
        engine.step_model()

    pressure = float(getattr(vent, "pres", 0.0) or 0.0)
    flow = float(getattr(vent, "flow", 0.0) or 0.0)
    minute_volume = float(getattr(vent, "minute_volume", 0.0) or 0.0)
    ok = bool(getattr(vent, "is_enabled", False)) and pressure == pressure and flow == flow
    return ok, f"ventilator: mode={getattr(vent, 'vent_mode', None)}, pres={pressure:.3f}, flow={flow:.3f}, minute_volume={minute_volume:.6f}"


def check_resuscitation() -> tuple[bool, str]:
    engine = _load_engine("resuscitation.json")
    resus = engine.models.get("RESUS")
    vent = engine.models.get("VENT")
    breathing = engine.models.get("Breathing")
    ds = engine.models.get("DS")

    if resus is None or vent is None or breathing is None or ds is None:
        return False, "resuscitation: RESUS, VENT, Breathing, or DS model missing"

    if not hasattr(resus, "switch_cpr"):
        return False, "resuscitation: switch_cpr method missing"

    resus.switch_cpr(True)
    for _ in range(300):
        engine.step_model()

    chest_comp_pres = float(getattr(resus, "chest_comp_pres", 0.0) or 0.0)
    cpr_enabled = bool(getattr(resus, "cpr_enabled", False))
    vent_mode = str(getattr(vent, "vent_mode", ""))
    breathing_enabled = bool(getattr(breathing, "breathing_enabled", True))
    compression_applied = chest_comp_pres > 0.0

    ok = cpr_enabled and vent_mode == "PC" and (not breathing_enabled) and compression_applied
    return ok, (
        f"resuscitation: cpr_enabled={cpr_enabled}, vent_mode={vent_mode}, "
        f"breathing_enabled={breathing_enabled}, chest_comp_pres={chest_comp_pres:.3f}"
    )


def check_monitor() -> tuple[bool, str]:
    engine = _load_engine("monitor.json")
    monitor = engine.models.get("MON")
    required = ["AA", "AD", "PA", "RA", "VENT", "DS"]

    if monitor is None or not all(name in engine.models for name in required):
        return False, "monitor: MON or required source models missing"

    for _ in range(120):
        engine.step_model()

    heart_rate = float(getattr(monitor, "heart_rate", 0.0) or 0.0)
    abp_signal = float(getattr(monitor, "abp_signal", 0.0) or 0.0)
    etco2 = float(getattr(monitor, "etco2", 0.0) or 0.0)
    spo2_pre = float(getattr(monitor, "spo2_pre", 0.0) or 0.0)
    valid_numbers = all(value == value for value in [heart_rate, abp_signal, etco2, spo2_pre])
    ok = bool(getattr(monitor, "is_enabled", False)) and valid_numbers
    return ok, (
        f"monitor: hr={heart_rate:.3f}, abp_signal={abp_signal:.3f}, "
        f"etco2={etco2:.3f}, spo2_pre={spo2_pre:.3f}"
    )


def main() -> int:
    checks = [
        check_baseline,
        check_pda,
        check_shunts,
        check_placenta,
        check_fluids,
        check_ans,
        check_ecls,
        check_ventilator,
        check_resuscitation,
        check_monitor,
    ]

    failed = False
    for check in checks:
        ok, message = check()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {message}")
        if not ok:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
