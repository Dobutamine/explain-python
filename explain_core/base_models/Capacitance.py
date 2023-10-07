import math
from explain_core.base_models.BaseModel import BaseModel


class Capacitance(BaseModel):

    # independent variables
    u_vol: float = 0.0
    u_vol_factor: float = 1.0
    el_base: float = 0.0
    el_base_factor: float = 1.0
    el_k: float = 0.0
    el_k_factor: float = 1.0
    fixed_composition: bool = False

    # dependent variables
    vol: float = 0.0
    pres: float = 0.0
    pres_ext: float = 0.0
    pres_cc: float = 0.0
    pres_atm: float = 0.0
    pres_mus: float = 0.0
    pres_tm: float = 0.0
    pres_in: float = 0.0
    pres_out: float = 0.0

    # implement the calc_model method
    def calc_model(self) -> None:

        # calculate the pressure depending on the volume, unstressed volume, elastance
        self.pres_in = self.el_k * self.el_k_factor * math.pow(self.vol - (self.u_vol * self.u_vol_factor), 2) + \
            self.el_base * self.el_base_factor * (self.vol - (self.u_vol * self.u_vol_factor)) + self.pres_atm
        
        # calculate the pressures exerted by the surrounding tissues or other forces
        self.pres_out = self.pres_ext + self.pres_cc + self.pres_mus

        # calculate the transmural pressure
        self.pres_tm = self.pres_in - self.pres_out

        # calculate the total pressure
        self.pres = self.pres_in + self.pres_out
           
        # reset the pressure which are recalculated every model iterattion
        self.pres_ext = 0.0
        self.pres_cc = 0.0
        self.pres_mus = 0.0

    def volume_in(self, dvol: float) -> None:
        # increase the volume
        self.vol += dvol

    def volume_out(self, dvol: float) -> float:
        if self.fixed_composition:
            return 0

        # assume all dvol can be removed
        vol_not_removed: float = 0.0

        # decrease the volume
        self.vol -= dvol

        # guard against negative volumes
        if self.vol < 0:
            # so we need to remove more volume then we have which is not possible. Calculate how much volume can be removed
            vol_not_removed = -self.vol

            # reset the volume to zero
            self.vol = 0.0

        # return the amount of volume out
        vol_not_removed = 0

        return vol_not_removed
