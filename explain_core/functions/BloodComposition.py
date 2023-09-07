import math
from explain_core.functions.BrentRootFinding import brent_root_finding

# set the brent root finding properties
brent_accuracy = 1e-8
max_iterations = 100.0


# acidbase constants
kw = math.pow(10.0, -13.6) * 1000.0
kc = math.pow(10.0, -6.1) * 1000.0
kd = math.pow(10.0, -10.22) * 1000.0
alpha_co2p = 0.03067
left_hp = math.pow(10.0, -7.8) * 1000.0
right_hp = math.pow(10.0, -6.5) * 1000.0

# acidbase state variables
tco2: float = 0.0
pco2: float = 0.0
hco3: float = 0.0
be: float = 0.0
sid: float = 0.0
sid_app: float = 0.0
albumin: float = 0.0
phosphates: float = 0.0
uma: float = 0.0
hemoglobin: float = 0.0

# oxygenation constants
left_o2 = 0.01
right_o2 = 1000.0
alpha_o2p = 0.0095
mmoltoml = 22.2674
gas_constant = 62.36367

# oxygenation
dpg = 5
temp = 37
pres = 0.0
to2 = 0.0
ph = 0.0
temp = 0.0
po2 = 0.0
so2 = 0.0


class AcidBaseResult:
    valid: bool = False
    ph: float
    pco2: float
    hco3: float
    be: float
    sid_app: float

    def __init__(self, valid, ph, pco2, hco3, be, sid_app):
        self.valid = valid
        self.ph = ph
        self.pco2 = pco2
        self.hco3 = hco3
        self.be = be
        self.sid_app = sid_app

class OxyResult:
    valid: bool = False
    po2: float
    so2: float

    def __init__(self, valid, po2, so2) -> None:
        self.valid = valid
        self.po2 = po2
        self.so2 = so2

def set_blood_composition(bc) -> None:
    result: AcidBaseResult = calc_acidbase_from_tco2(bc)
    if result.valid:
        bc.aboxy['ph'] = result.ph
        bc.aboxy['pco2'] = result.pco2
        bc.aboxy['hco3'] = result.hco3
        bc.aboxy['be'] = result.be
        bc.aboxy['sid_app'] = result.sid_app

    result: OxyResult = calc_oxygenation_from_to2(bc)
    if result.valid:
        bc.aboxy['po2'] = result.po2
        bc.aboxy['so2'] = result.so2

def calc_acidbase_from_tco2(comp) -> AcidBaseResult:
    global tco2, pco2, hco3, be, sid, albumin, phosphates, uma, hemoglobin
    # calculate the apparent strong ion difference (SID) in mEq/l
    # comp.sid = comp.sodium + comp.potassium + 2 * comp.calcium + 2 * comp.magnesium - comp.chloride - comp.lactate - comp.urate

    # get the total co2 concentration in mmol/l
    tco2 = comp.aboxy['tco2']

    # calculate the apparent SID
    sid = comp.solutes['na'] + comp.solutes['k'] + 2 * comp.solutes['ca'] + 2 * comp.solutes['mg'] - comp.solutes['cl'] - comp.solutes['lact']

    # 𝑆𝐼𝐷𝑎𝑝𝑝=[𝑁𝑎+]+[𝐾+]+2[𝐶𝑎2+]+2[𝑀𝑔2+]−[𝐶𝑙−]−[𝐿𝑎−]

    # store the apparent SID
    # sid = comp.aboxy['sid']

    # get the albumin concentration in g/l
    albumin = comp.aboxy['albumin']

    # get the inorganic phosphates concentration in mEq/l
    phosphates = comp.aboxy['phosphates']

    # get the unmeasured anions in mEq/l
    uma = comp.aboxy['uma']

    # # get the hemoglobin concentration in mmol/l
    hemoglobin = comp.aboxy['hemoglobin']

    # now try to find the hydrogen concentration at the point where the net charge of the plasma is zero within limits of the brent accuracy
    hp = brent_root_finding(net_charge_plasma, left_hp, right_hp, max_iterations, brent_accuracy)

    # if this hydrogen concentration is found then return the result
    if (hp > 0):
        return AcidBaseResult(True, (-math.log10(hp / 1000)), pco2, hco3, be,sid)
    else:
        return AcidBaseResult(False, 7.40, 0, 0, 0, 0)

def calc_oxygenation_from_to2(comp) -> OxyResult:
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
        return OxyResult(True, po2, so2 * 100.0)
    else:
        return OxyResult(False, 0, 0)
    
def net_charge_plasma(hp_estimate):
    global tco2, pco2, hco3, be, sid, albumin, phosphates, uma, hemoglobin

    # calculate the ph based on the current hp estimate
    ph = -math.log10(hp_estimate / 1000.0)

    # we do know the total co2 concentration but we now have to find out the distribution of the co2 where tco2 = cco2 + hco3 + cco3

    # cco2 = plasma concentration of co2 -> charge neutral
    # hco3 = plasma concentration of bicarbonate -> charge 1-
    # cco3 = plasma concentration of carbonate -> charge 2-

    # the distribution is described by
    # pH = pKc * HCO3 + log10(hco3 / cco2)
    # pH = pKd + log10(cco3 / hco3)

    # calculate the plasma co2 concentration based on the total co2 in the plasma, hydrogen concentration and the constants Kc and Kd
    cco2p = tco2 / (1.0 + kc / hp_estimate +
                    (kc * kd) / math.pow(hp_estimate, 2.0))

    # calculate the plasma hco3(-) concentration (bicarbonate)
    hco3p = (kc * cco2p) / hp_estimate

    # calculate the plasma co3(2-) concentration (carbonate)
    co3p = (kd * hco3p) / hp_estimate

    # calculate the plasma OH(-) concentration (water dissociation)
    ohp = kw / hp_estimate

    # calculate the pco2 of the plasma
    pco2p = cco2p / alpha_co2p

    # calculate the weak acids (albumin and phosphates)
    # Clin Biochem Rev 2009 May; 30(2): 41-54
    a_base = albumin * (0.123 * ph - 0.631) + \
        phosphates * (0.309 * ph - 0.469)
    # alb_base = albumin * (0.378 / (1.0 + math.pow(10, 7.1 - ph)))
    # phos_base = phosphates / (1.0 + math.pow(10, 6.8 - ph))

    # calculate the net charge of the plasma. If the netcharge is zero than the current hp_estimate is the correct one.
    netcharge = hp_estimate + sid - hco3p - 2.0 * co3p - ohp - a_base - uma

    # calculate the base excess according to the van Slyke equation
    be = (hco3p - 25.1 + (2.3 * hemoglobin + 7.7)
          * (ph - 7.4)) * (1.0 - 0.023 * hemoglobin)

    # calculate the pco2 and store the plasma hco3
    pco2 = pco2p
    hco3 = hco3p
    cco3 = co3p
    cco2 = cco2p

    # return the net charge to the brent function
    return netcharge

def oxygen_content(po2_estimate: float) -> float:
    global so2
    # calculate the saturation from the current po2 from the current po2 estimate
    so2 = oxygen_dissociation_curve(po2_estimate)
    # calculate the to2 from the current po2 estimate
    # INPUTS: po2 in mmHg, so2 in fraction, hemoglobin in mmol/l
    # convert the hemoglobin unit from mmol/l to g/dL  (/ 0.6206)
    # convert to output from ml O2/dL blood to ml O2/l blood (* 10.0)
    to2_new_estimate = (0.0031 * po2_estimate +
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
    x0 = 1.875 + a + b
    h0 = 3.5 + a
    x = math.log((po2_estimate * 0.1333), math.e)  # po2 in kPa
    y = x - x0 + h0 * math.tanh(0.5343 * (x - x0)) + 1.875

    # return the o2 saturation in fraction so 0.98
    # return 1.0 / (math.pow(math.e, -y) + 1.0)
    return 1.0 / (math.exp(-y) + 1.0)



