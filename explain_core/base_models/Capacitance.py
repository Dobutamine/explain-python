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

    # dependent variables
    vol: float = 0.0
    pres: float = 0.0
    pres_ext: float = 0.0

    # implement the calc_model method
    def calc_model(self) -> None:
        # calculate the pressure depending on the volume, unstressed volume, elastance and external pressure
        if self.vol > self.u_vol * self.u_vol_factor:
            self.pres = self.el_k * self.el_k_factor * math.pow(self.vol - (self.u_vol * self.u_vol_factor), 2) + \
                self.el_base * self.el_base_factor * \
                (self.vol - (self.u_vol * self.u_vol_factor)) + self.pres_ext
        else:
            self.pres = self.pres_ext

    def volume_in(self, dvol: float) -> None:
        # increase the volume
        self.vol += dvol

    def volume_out(self, dvol: float) -> float:
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
        return vol_not_removed
