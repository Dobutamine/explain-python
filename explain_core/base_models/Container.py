import math
from explain_core.base_models.Capacitance import Capacitance


class Container(Capacitance):
    # independent variables
    vol_extra: float = 0.0
    el: float = 0.0
    act_factor: float = 0.0

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # get the current volume from all contained model components
        self.vol = self.vol_extra
        for c in self.contained_components:
            self.vol += self._model.models[c].vol

        # calculate the elastance
        _el_base: float = (
            self.el_base * self.el_base_factor * self.el_base_scaling_factor
        )
        _el: float = (
            _el_base
            + self.act_factor
            + +(self.el_base_ans_factor * _el_base - _el_base)
            * self.ans_activity_factor
            + (self.el_base_drug_factor * _el_base - _el_base)
        )

        # calculate the non-linear elastance factor
        _el_k_base: float = self.el_k * self.el_k_factor * self.el_k_scaling_factor
        _el_k: float = _el_k_base

        # calculate the unstressed volume
        _u_vol_base: float = self.u_vol * self.u_vol_factor * self.u_vol_scaling_factor
        _u_vol: float = (
            _u_vol_base
            + (_u_vol_base * self.u_vol_ans_factor - _u_vol_base)
            * self.ans_activity_factor
        )

        # calculate the pressure depending on the volume, unstressed volume, elastance and non-linear elastance factor
        self.pres_in = (
            _el * (self.vol - _u_vol)
            + _el_k * math.pow(self.vol - _u_vol, 2)
            + self.pres_atm
        )

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
        self.act_factor = 0.0

        # transfer the pressures to the models the container contains
        for c in self.contained_components:
            self._model.models[c].pres_ext += self.pres
