import math

from explain_core.helpers.BaseModel import BaseModel


class Capacitance(BaseModel):
    # independent variables
    u_vol = 0.0
    u_vol_factor = 1.0
    el_base = 0.0
    el_base_factor = 1.0
    el_k = 0.0
    el_k_factor = 1.0

    # dependent variables
    vol = 0.0
    vol_max = 0.0
    vol_min = 0.0
    pres = 0.0
    pres_max = 0.0
    pres_min = 0.0
    solutes = {}

    # external variables
    pres_ext = 0.0

    # local variables
    _temp_pres_max = 0
    _temp_pres_min = 0
    _temp_vol_max = 0
    _temp_vol_min = 0

    def __init__(self, **args):
        # initialize the super class (basemodel) which sets the mode properties
        super().__init__(**args)

    def calc_model(self, model):
        # calculate the pressure depending on the volume, unstressed volume and the elastance
        if self.vol > self.u_vol * self.u_vol_factor:
            self.pres = self.el_k * self.el_k_factor * math.sqrt(self.vol - (self.u_vol * self.u_vol_factor), 2) + \
                self.el_base * self.el_base_factor * \
                (self.vol - (self.u_vol * self.u_vol_factor)) + self.pres_ext
        else:
            self.pres = self.pres_ext

    def volume_in(self, dvol, comp_from):
        # increase the volume
        self.vol += self.dvol

    def volume_out(self, dvol):
        # assume all dvol can be removed
        vol_out = dvol

        # decrease the volume
        self.vol -= self.dvol

        # guard against negative volumes
        if self.vol < 0:
            # so we need to remove more volume then we have which is not possible. Calculate how much volume can be removed
            vol_out = self.vol + dvol

            # reset the volume to zero
            self.vol = 0.0

        # return the amount of volume out
        return vol_out
