import math
from explain_core.functions.BrentRootFinding import brent_root_finding

# set the brent root finding properties
brent_accuracy = 1e-8
max_iterations = 100.0
steps = 0

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


def calc_acidbase_from_tco2(comp) -> object:
    global tco2, pco2, hco3, be, sid, albumin, phosphates, uma, hemoglobin
    # calculate the apparent strong ion difference (SID) in mEq/l
    # comp.sid = comp.sodium + comp.potassium + 2 * comp.calcium + 2 * \
    #     comp.magnesium - comp.chloride - comp.lactate - comp.urate

    # get the total co2 concentration in mmol/l
    tco2 = comp.aboxy['tco2']

    # calculate the apparent SID
    sid = comp.solutes['na'] + comp.solutes['k'] + 2 * comp.solutes['ca'] + \
        2 * comp.solutes['mg'] - comp.solutes['cl'] - comp.solutes['lact']

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
    hp = brent_root_finding(
        net_charge_plasma, left_hp, right_hp, max_iterations, brent_accuracy)

    # if this hydrogen concentration is found then return the result
    if (hp > 0):
        return {
            "ph": (-math.log10(hp / 1000)),
            "pco2": pco2,
            "hco3": hco3,
            "be": be,
            "sid_app": sid
        }
    else:
        return None


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
