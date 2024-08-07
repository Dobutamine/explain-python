import math
from explain_core.core_models.GasCapacitance import GasCapacitance

# define an object which holds the gas composition at 0 degrees celcius and 0 humidity
fo2_dry = 0.205
fco2_dry = 0.000392
fn2_dry = 0.794608
fother_dry = 0.0


def set_gas_composition(
    gc: GasCapacitance,
    fio2: float,
    temp: float,
    humidity: float,
    fico2: float = 0.000392,
):
    result = calc_gas_composition(gc, fio2, temp, humidity, fico2)

    # process the result
    gc.po2 = result["po2"]
    gc.pco2 = result["pco2"]
    gc.pn2 = result["pn2"]
    gc.ph2o = result["ph2o"]
    gc.pother = result["pother"]

    gc.fo2 = result["fo2"]
    gc.fco2 = result["fco2"]
    gc.fn2 = result["fn2"]
    gc.fh2o = result["fh2o"]
    gc.fother = result["fother"]

    gc.co2 = result["co2"]
    gc.cco2 = result["cco2"]
    gc.cn2 = result["cn2"]
    gc.ch2o = result["ch2o"]
    gc.cother = result["cother"]


def calc_gas_composition(
    gascomp, fio2=0.205, temp=None, humidity=None, fico2: float = 0.000392
) -> object:
    # check that the gascomp is a gas capacitance
    if type(gascomp) is GasCapacitance:
        # make sure the latest pressure is available
        gascomp.calc_model()
        # calculate the dry gas composition depending on the supplied fio2
        new_fo2_dry = fio2
        new_fco2_dry = fico2
        new_fn2_dry = fn2_dry * (1.0 - (fio2 + fico2)) / (1.0 - (fo2_dry + fco2_dry))
        new_fother_dry = (
            fother_dry * (1.0 - (fio2 + fico2)) / (1.0 - (fo2_dry + fco2_dry))
        )
        # if temp is set then transfer that temp to the gascomp
        if temp is not None:
            gascomp.target_temp = temp
            gascomp.temp = temp
        # if humidity is set then transfer that humidity to the gascomp
        if humidity is not None:
            gascomp.humidity = humidity

        # calculate the gas composition
        result = gas_composition(
            gascomp.pres,
            new_fo2_dry,
            new_fco2_dry,
            new_fn2_dry,
            new_fother_dry,
            gascomp.temp,
            gascomp.humidity,
        )

        return result


def gas_composition(
    pressure, new_fo2_dry, new_fco2_dry, new_fn2_dry, new_fother_dry, temp, humidity
):
    # local constant
    _gas_constant: float = 62.36367

    # calculate the concentration at this pressure and temperature in mmol/l using the gas law
    ctotal: float = (pressure / (_gas_constant * (273.15 + temp))) * 1000.0

    # calculate the water vapour pressure, concentration and fraction for this temperature and humidity (0 - 1)
    ph2o: float = math.pow(math.e, 20.386 - 5132 / (temp + 273)) * humidity
    fh2o: float = ph2o / pressure
    ch2o = fh2o * ctotal

    # calculate the o2 partial pressure, fraction and concentration
    po2 = new_fo2_dry * (pressure - ph2o)
    fo2 = po2 / pressure
    co2 = fo2 * ctotal

    # calculate the co2 partial pressure, fraction and concentration
    pco2 = new_fco2_dry * (pressure - ph2o)
    fco2 = pco2 / pressure
    cco2 = fco2 * ctotal

    # calculate the n2 partial pressure, fraction and concentration
    pn2 = new_fn2_dry * (pressure - ph2o)
    fn2 = pn2 / pressure
    cn2 = fn2 * ctotal

    # calculate the other gas partial pressure, fraction and concentration
    pother = new_fother_dry * (pressure - ph2o)
    fother = pother / pressure
    cother = fother * ctotal

    return {
        "po2": po2,
        "pco2": pco2,
        "pn2": pn2,
        "pother": pother,
        "ph2o": ph2o,
        "fo2": fo2,
        "fco2": fco2,
        "fn2": fn2,
        "fother": fother,
        "fh2o": fh2o,
        "co2": co2,
        "cco2": cco2,
        "cn2": cn2,
        "cother": cother,
        "ch2o": ch2o,
    }
