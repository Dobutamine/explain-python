import math
from explain_core.base_models.BaseModel import BaseModel


class Capacitance(BaseModel):
    # independent variables
    u_vol: float = 0.0
    u_vol_factor: float = 1.0
    u_vol_ans_factor: float = 1.0
    u_vol_drug_factor: float = 1.0
    u_vol_scaling_factor: float = 1.0

    el_base: float = 0.0
    el_base_factor: float = 1.0
    el_base_ans_factor: float = 1.0
    el_base_drug_factor: float = 1.0
    el_base_scaling_factor: float = 1.0

    el_k: float = 0.0
    el_k_factor: float = 1.0
    el_k_ans_factor: float = 1.0
    el_k_drug_factor: float = 1.0
    el_k_scaling_factor: float = 1.0

    pres_ext: float = 0.0
    pres_cc: float = 0.0
    pres_atm: float = 0.0
    pres_mus: float = 0.0

    act_factor: float = 0.0
    ans_activity_factor: float = 1.0

    fixed_composition: bool = False

    # dependent variables
    vol: float = 0.0
    pres: float = 0.0
    pres_in: float = 0.0
    pres_out: float = 0.0
    pres_tm: float = 0.0

    # implement the calc_model method
    def calc_model(self) -> None:
        # calculate the baseline elastance depending on the scaling factor
        _el_base: float = self.el_base * self.el_base_scaling_factor

        # adjust the elastance depending on the activity of the external factor, autonomic nervous system and the drug model
        _el: float = (
            _el_base
            + self.act_factor
            + (self.el_base_factor * _el_base - _el_base)
            + (self.el_base_ans_factor * _el_base - _el_base) * self.ans_activity_factor
            + (self.el_base_drug_factor * _el_base - _el_base)
        )

        # calculate the non-linear elastance factor depending on the scaling factor
        _el_k_base: float = self.el_k * self.el_k_scaling_factor

        # adjust the non-linear elastance depending on the activity of the external factor, autonomic nervous system and the drug model
        _el_k: float = (
            _el_k_base
            + (self.el_k_factor * _el_k_base - _el_k_base)
            + (self.el_k_ans_factor * _el_k_base - _el_k_base)
            * self.ans_activity_factor
            + (self.el_k_drug_factor * _el_k_base - _el_k_base)
        )

        # calculate the unstressed volume depending on the scaling factor
        _u_vol_base: float = self.u_vol * self.u_vol_scaling_factor

        # adjust the unstressed volume depending on the activity of the external factor, autonomic nervous system and the drug model
        _u_vol: float = (
            _u_vol_base
            + (_u_vol_base * self.u_vol_factor - _u_vol_base)
            + (_u_vol_base * self.u_vol_ans_factor - _u_vol_base)
            * self.ans_activity_factor
            + (_u_vol_base * self.u_vol_drug_factor - _u_vol_base)
        )

        # calculate the recoil pressure depending on the volume, unstressed volume and elastance
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

    def get_el_base(self) -> float:
        return self.el_base * self.el_base_scaling_factor

    def get_u_vol(self) -> float:
        return self.u_vol * self.u_vol_scaling_factor
    
    def get_el_k(self) -> float:
        return self.el_k * self.el_k_scaling_factor

    def volume_in(self, dvol: float) -> None:
        # increase the volume
        self.vol += dvol

    def volume_out(self, dvol: float) -> float:
        # do not change the volume if the composition is fixed
        if self.fixed_composition:
            return 0

        # assume all dvol can be removed
        vol_not_removed: float = 0.0

        # decrease the volume
        self.vol -= dvol

        # guard against negative volumes
        if self.vol < 0:
            # so we need to remove more volume then we have which is not possible. Calculate how much volume can be removed
            # this is an undesirable situation and it means that the modeling stepsize is too large
            vol_not_removed = -self.vol
            # reset the volume to zero
            self.vol = 0.0

        # return the amount of volume that could not be removed
        return vol_not_removed
