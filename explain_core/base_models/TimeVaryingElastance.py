import math
from explain_core.base_models.Capacitance import Capacitance


class TimeVaryingElastance(Capacitance):
    # independent variables
    el_min: float = 0.0
    el_min_factor: float = 1.0
    el_min_ans_factor: float = 1.0
    el_min_drug_factor: float = 1.0
    el_min_mob_factor: float = 1.0
    el_min_scaling_factor: float = 1.0

    el_max: float = 0.0
    el_max_factor: float = 1.0
    el_max_ans_factor: float = 1.0
    el_max_drug_factor: float = 1.0
    el_max_mob_factor: float = 1.0
    el_max_scaling_factor: float = 1.0

    # dependent variables
    pres_ed: float = 0.0
    pres_ms: float = 0.0

    # implement the calc_model method
    def calc_model(self) -> None:
        # calculate the minimal elastance depending on the scaling factor
        _e_min_base: float = self.el_min * self.el_min_scaling_factor
        # adjust the elastance depending on the activity of the external factor, autonomic nervous system and the drug model
        _e_min: float = (
            _e_min_base
            + (self.el_min_factor * _e_min_base - _e_min_base)
            + (self.el_min_ans_factor * _e_min_base - _e_min_base)
            * self.ans_activity_factor
            + (self.el_base_drug_factor * _e_min_base - _e_min_base)
        )

        # calculate the maximal elastance depending on the scaling factor
        _e_max_base: float = self.el_max * self.el_max_scaling_factor
        # adjust the elastance depending on the activity of the external factor, autonomic nervous system, the drug model and mob model
        _e_max: float = (
            _e_max_base
            + (self.el_max_factor * _e_max_base - _e_max_base)
            + (self.el_max_ans_factor * _e_max_base - _e_max_base)
            * self.ans_activity_factor
            + (self.el_max_drug_factor * _e_max_base - _e_max_base)
            + (self.el_max_mob_factor * _e_max_base - _e_max_base)
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

        # calculate the volume difference
        vol_diff = self.vol - _u_vol

        # calculate the pressure
        self.pres_ed = (
            _e_min * vol_diff
            + self.el_k
            * self.el_k_factor
            * self.el_k_scaling_factor
            * math.pow(vol_diff, 2)
        )
        self.pres_ms = _e_max * vol_diff
        if self.pres_ms < self.pres_ed:
            self.pres_ms = self.pres_ed

        self.pres_in = (
            self.act_factor * (self.pres_ms - self.pres_ed)
            + self.pres_ed
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
