import math


def _gc_get(container, key, default=None):
    if isinstance(container, dict):
        return container.get(key, default)
    return getattr(container, key, default)


def _gc_set(container, key, value):
    if isinstance(container, dict):
        container[key] = value
    else:
        setattr(container, key, value)


def _gc_call_calc_model(gc):
    if isinstance(gc, dict):
        return

    calc_model = getattr(gc, "calc_model", None)
    if callable(calc_model):
        calc_model()


def calc_gas_composition(gc, fio2=0.205, temp=37.0, humidity=1.0, fico2=0.000392):
    fo2_dry = 0.205
    fco2_dry = 0.000392
    fn2_dry = 0.794608
    fother_dry = 0.0
    gas_constant = 62.36367

    new_fo2_dry = fio2
    new_fco2_dry = fico2
    denominator = 1.0 - (fo2_dry + fco2_dry)
    new_fn2_dry = (fn2_dry * (1.0 - (fio2 + fico2))) / denominator
    new_fother_dry = (fother_dry * (1.0 - (fio2 + fico2))) / denominator

    _gc_call_calc_model(gc)
    pressure = _gc_get(gc, "pres", 0.0)

    ctotal = (pressure / (gas_constant * (273.15 + temp))) * 1000.0
    _gc_set(gc, "ctotal", ctotal)

    ph2o = math.exp(20.386 - 5132.0 / (temp + 273.0)) * humidity
    _gc_set(gc, "ph2o", ph2o)

    fh2o = ph2o / pressure
    _gc_set(gc, "fh2o", fh2o)
    _gc_set(gc, "ch2o", fh2o * ctotal)

    po2 = new_fo2_dry * (pressure - ph2o)
    _gc_set(gc, "po2", po2)
    fo2 = po2 / pressure
    _gc_set(gc, "fo2", fo2)
    _gc_set(gc, "co2", fo2 * ctotal)

    pco2 = new_fco2_dry * (pressure - ph2o)
    _gc_set(gc, "pco2", pco2)
    fco2 = pco2 / pressure
    _gc_set(gc, "fco2", fco2)
    _gc_set(gc, "cco2", fco2 * ctotal)

    pn2 = new_fn2_dry * (pressure - ph2o)
    _gc_set(gc, "pn2", pn2)
    fn2 = pn2 / pressure
    _gc_set(gc, "fn2", fn2)
    _gc_set(gc, "cn2", fn2 * ctotal)

    pother = new_fother_dry * (pressure - ph2o)
    _gc_set(gc, "pother", pother)
    fother = pother / pressure
    _gc_set(gc, "fother", fother)
    _gc_set(gc, "cother", fother * ctotal)
