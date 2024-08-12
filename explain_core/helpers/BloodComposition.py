import math

import explain_core.cpp_models._blood_composition as bcomp


def set_blood_composition(bc) -> None:
    # calculate the acidbase and oxygenation
    aboxy = bc.aboxy
    sol = bc.solutes

    # calculate the apparent SID
    sid = sol["na"] + sol["k"] + 2 * sol["ca"] + 2 * sol["mg"] - sol["cl"] - sol["lact"]

    bg = bcomp.lib.GetBloodComposition(
        aboxy["to2"],
        aboxy["tco2"],
        sid,
        aboxy["albumin"],
        aboxy["phosphates"],
        aboxy["uma"],
        aboxy["hemoglobin"],
        aboxy["dpg"],
        aboxy["temp"],
    )

    if bg.valid_ab:
        bc.ph = bg.ph
        bc.pco2 = bg.pco2
        aboxy["ph"] = bg.ph
        aboxy["pco2"] = bg.pco2
        aboxy["hco3"] = bg.hco3
        aboxy["be"] = bg.be

    if bg.valid_o2:
        bc.po2 = bg.po2
        bc.so2 = bg.so2
        aboxy["po2"] = bg.po2
        aboxy["so2"] = bg.so2
