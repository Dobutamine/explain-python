import math
from explain_core.base_models.Capacitance import Capacitance

class TimeVaryingElastance(Capacitance):
    # independent variables
    u_vol: float = 0.0
    u_vol_factor: float = 1.0
    el_base: float = 0.0
    el_min: float = 0.0
    el_min_factor: float = 1.0
    el_max: float = 0.0
    el_max_factor: float = 1.0
    el_k: float = 0.0
    el_k_factor: float = 1.0
    act_factor: float = 0.0

    # dependent variables
    vol: float = 0.0
    pres: float = 0.0
    pres_atm: float = 0.0
    pres_mus: float = 0.0
    pres_cc: float = 0.0
    pres_ed: float = 0.0
    pres_ms: float = 0.0
    pres_ext: float = 0.0
    pres_tm: float = 0.0
    pres_in: float = 0.0
    pres_out: float = 0.0

    # implement the calc_model method
    def calc_model(self) -> None:

        # calculate the pressure depending on the volume, unstressed volume, elastance and activation factor
        vol_diff = self.vol - (self.u_vol * self.u_vol_factor)
        self.pres_ed = self.el_k * self.el_k_factor * math.pow(vol_diff, 2) + \
            self.el_min * self.el_min_factor * vol_diff
        self.pres_ms = self.el_max * self.el_max_factor * vol_diff
        self.pres_in = self.act_factor * \
            (self.pres_ms - self.pres_ed) + self.pres_ed + \
            self.pres_cc + self.pres_atm + self.pres_mus

        # calculate the pressures exerted by the surrounding tissues or other forces
        self.pres_out = self.pres_ext + self.pres_cc + self.pres_atm + self.pres_mus 

        # calculate the transmural pressure
        self.pres_tm = self.pres_in - self.pres_out

        # calculate the total pressure
        self.pres = self.pres_in + self.pres_out
        
        # reset the pressure which are recalculated every model iterattion
        self.pres_ext = 0.0
        self.pres_cc = 0.0
        self.pres_mus = 0.0

