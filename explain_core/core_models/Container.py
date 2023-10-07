import math
from explain_core.base_models.Capacitance import Capacitance


class Container(Capacitance):
    # independent variables
    vol_extra: float = 0.0
    el: float = 0.0
    act_factor: float = 1.0

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # get the current volume from all contained model components
        self.vol = self.vol_extra

        for c in self.contained_components:
            self.vol += self._model.models[c].vol

        # calculate the elastance
        self.el = self.el_base * self.el_base_factor + self.act_factor

        # calculate the pressure depending on the volume, unstressed volume and elastance
        self.pres_in = self.el_k * self.el_k_factor * math.pow(self.vol - (self.u_vol * self.u_vol_factor), 2) + self.el * (self.vol - (self.u_vol * self.u_vol_factor))
        
        # calculate the pressures exerted by the surrounding tissues or other forces
        self.pres_out =  self.pres_ext + self.pres_cc + self.pres_atm + self.pres_mus

        # calculate the transmural pressure
        self.pres_tm = self.pres_in - self.pres_out

        # calculate the total pressure
        self.pres = self.pres_in + self.pres_out

        # reset the pressure which are recalculated every model iterattion
        self.pres_ext = 0.0
        self.pres_cc = 0.0
        self.pres_mus = 0.0
        self.act_factor = 0.0

        # transfer the pressures to the models the container contains
        for c in self.contained_components:
            self._model.models[c].pres_ext += self.pres
