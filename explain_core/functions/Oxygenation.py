import math
from explain_core.functions.BrentRootFinding import brent_root_finding

# set the brent root finding properties
brent_accuracy = 1e-8
max_iterations = 100.0
gas_constant = 62.36367
steps = 0

# oxygenation constants
left_o2 = 0.01
right_o2 = 1000.0
alpha_o2p = 0.0095
mmoltoml = 22.2674

# oxygenation
dpg = 5
hemoglobin = 10
temp = 37
pres = 0.0

to2 = 0.0
ph = 0.0
be = 0.0
dpg = 0.0
hemoglobin = 8.0
temp = 0.0
po2 = 0.0
so2 = 0.0

# UNITS
# po2_estimate in kPa


def calc_oxygenation_from_to2(comp) -> object:
    global to2, ph, be, dpg, hemoglobin, temp, po2, pres
    # get the for the oxygenation independent parameters from the component
    to2 = comp.aboxy['to2']
    ph = comp.aboxy['ph']
    be = comp.aboxy['be']
    dpg = comp.aboxy['dpg']
    hemoglobin = comp.aboxy['hemoglobin']
    temp = comp.aboxy['temp']
    pres = comp.pres

    # calculate the po2 from the to2 using a brent root finding function and oxygen dissociation curve
    po2 = brent_root_finding(
        oxygen_content, left_o2, right_o2, max_iterations, brent_accuracy)

    # if a po2 is found then return the result
    if (po2 > 0):
        return {
            "po2": po2 * 7.5,
            "so2": so2 * 100.0
        }
    else:
        return None


def oxygen_content(po2_estimate: float) -> float:
    global so2
    # calculate the saturation from the current po2 from the current po2 estimate
    so2 = oxygen_dissociation_curve(po2_estimate)
    # calculate the to2 from the current po2 estimate
    # convert the hemoglobin unit from mmol/l to g/dL  (= factor 1.6113)
    # convert the po2 from kPa to mmHg
    # convert to output from ml O2/dL blood to ml O2/l blood

    # O2 bound to Hb (ml/dL) = SaO2 (%) × Hb (g/dL) × 1.34
    to2_new_estimate = (0.0031 * (po2_estimate / 0.1333) +
                        1.36 * (hemoglobin / 0.6206) * so2) * 10.0

    # conversion factor for converting ml O2/l to mmol/l
    mmol_to_ml: float = (gas_constant * (273.15 + temp)) / 760.0

    # convert the ml O2/l to mmol/l
    to2_new_estimate = to2_new_estimate / mmol_to_ml

    # calculate the difference between the real to2 and the to2 based on the new po2 estimate and return it to the brent root finding function
    dto2 = to2 - to2_new_estimate

    return dto2


def oxygen_dissociation_curve(po2_estimate: float) -> float:
    # calculate the saturation from the po2 depending on the ph,be, temperature and dpg level.
    a = 1.04 * (7.4 - ph) + 0.005 * be + 0.07 * (dpg - 5.0)
    b = 0.055 * (temp + 273.15 - 310.15)
    y0 = 1.875
    x0 = 1.875 + a + b
    h0 = 3.5 + a
    k = 0.5343
    x = math.log(po2_estimate, math.e)
    y = x - x0 + h0 * math.tanh(k * (x - x0)) + y0

    # return the o2 saturation in fraction so 0.98
    return 1.0 / (math.pow(math.e, -y) + 1.0)
