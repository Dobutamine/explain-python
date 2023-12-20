import math


class Scaling:
    model = {}

    scale_factor: float = 1.0
    scale_factor_correction: float = 1.0

    el_base_factor_circ = 1.0
    el_base_factor_circ_correction = 1.0

    el_base_factor_resp = 1.0
    el_base_factor_resp_correction = 1.0

    res_factor_circ = 1.0
    res_factor_circ_correction = 1.0

    res_factor_resp = 1.0
    res_factor_resp_correction = 1.0

    el_min_factor = 1.0
    el_min_factor_correction = 1.0

    el_max_factor = 1.0
    el_max_factor_correction = 1.0

    u_vol_factor = 1.0
    u_vol_factor_correction = 1.0

    hr_ref: float = 140.0
    mv_ref: float = 0.0

    hr_target: float = 0.0
    lvo_target: float = 0.0
    mv_target: float = 0.0
    resp_rate_target: float = 0.0

    map_ref: float = 50.0

    def __init__(self, model):
        # get a reference to the model engine
        self.model = model

    def scale_patient(
        self,
        target_weight: float,
        target_blood_volume: float,
        target_hr_ref: float,
        target_map: float,
    ):
        # calculate the scale factor based on the weight change
        self.scale_factor: float = (
            self.model.weight / target_weight * self.scale_factor_correction
        )

        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor_circ: float = (
            self.model.weight / target_weight * self.el_base_factor_circ_correction
        )

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.res_factor_circ: float = (
            self.model.weight / target_weight * self.res_factor_circ_correction
        )

        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor_resp: float = (
            self.model.weight / target_weight * self.el_base_factor_resp_correction
        )

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.res_factor_resp: float = (
            self.model.weight / target_weight * self.res_factor_resp_correction
        )

        # calculate the el_max factor based on the weight change. The lower the weight the higher the el_max
        self.el_min_factor: float = (
            self.model.weight / target_weight * self.el_min_factor_correction
        )

        # calculate the el_max factor based on the weight change. The lower the weight the higher the el_max
        self.el_max_factor: float = (
            self.model.weight / target_weight * self.el_max_factor_correction
        )

        # calculate the u_vol factor based on the weight change. The lower the weight the lower the u_vol
        self.u_vol_factor: float = (
            target_weight / self.model.weight * self.u_vol_factor_correction
        )

        # scale the weight and height
        self.model.set_weight(target_weight)  # in kg
        # self.model.set_height(target_height)  # in m

        # scale the blood volume
        self.scale_blood_volume(target_blood_volume * target_weight)

        # scale the circulation
        self.scale_circulatory_system()

        # scale the heart
        self.scale_heart(target_hr_ref)

        # scale the respiratory system
        self.scale_respiratory_system()

        # scale the autonomous nervous system
        self.scale_ans(target_map)

        # # scale the metabolism
        # self.scale_metabolism()

        # # scale the myocardial oxygen balance and metabolism
        # self.scale_mob()

    def scale_blood_volume(self, new_blood_volume: float):
        self.model.models["Blood"].set_total_blood_volume(new_blood_volume)

    def scale_heart(self, heartrate_ref: float):
        # adjust the reference heartdate
        self.model.models["Heart"].set_heart_rate_ref(heartrate_ref)

        # adjust the heart elastances
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "BloodTimeVaryingElastance" in _model.model_type:
                    _model.el_min_scaling_factor = self.el_min_factor
                    _model.el_max_scaling_factor = self.el_max_factor

        # adjust the elastance and unstressed volume of the pericardium
        self.model.models["PC"].u_vol_factor = self.u_vol_factor
        self.model.models["PC"].el_base_scaling_factor = self.el_base_factor_circ

    def scale_circulatory_system(self):
        # adjust the resistance of the circulation
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "Resistor" in _model.model_type:
                    if "Blood" in _model._model_comp_from.model_type:
                        _model.r_scaling_factor = self.res_factor_circ

        # adjust the elastance of the circulation
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "BloodCapacitance" in _model.model_type:
                    _model.el_base_scaling_factor = self.el_base_factor_circ

    def scale_respiratory_system(self):
        # adjust the elastance of the respiratory system
        for _model in self.model.models.values():
            if _model.is_enabled:
                if (
                    _model.model_type == "GasCapacitance"
                    and _model.fixed_composition == False
                ):
                    _model.el_base_scaling_factor = self.el_base_factor_resp
                    _model.u_vol_scaling_factor = self.u_vol_factor

        # adjust the elastance of the respiratory system
        self.model.models["THORAX"].el_base_scaling_factor = self.el_base_factor_resp
        self.model.models["CHEST_L"].el_base_scaling_factor = self.el_base_factor_resp
        self.model.models["CHEST_R"].el_base_scaling_factor = self.el_base_factor_resp

        # adjust the unstressed volume of the respiratory system
        self.model.models["THORAX"].u_vol_scaling_factor = self.u_vol_factor
        self.model.models["CHEST_L"].u_vol_scaling_factor = self.u_vol_factor
        self.model.models["CHEST_R"].u_vol_scaling_factor = self.u_vol_factor

        # adjust the resistance of the airways
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "Resistor" in _model.model_type:
                    if "Gas" in _model._model_comp_from.model_type:
                        _model.r_for_scaling_factor = self.res_factor_resp
                        _model.r_back_scaling_factor = self.res_factor_resp

    def scale_ans(self, target_map: float):
        # adjust the baroreceptor
        self.model.models["Ans"].min_map = target_map / 2.0
        self.model.models["Ans"].set_map = target_map
        self.model.models["Ans"].max_map = target_map * 2.0
        self.model.models["Ans"].init_effectors()

    def scale_metabolism(self):
        pass

    def scale_mob(self):
        pass
