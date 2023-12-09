import math


class Scaling:
    model = {}

    el_base_factor = 1.0
    el_base_factor_correction = 1.0

    resistance_factor = 0.6
    resistance_factor_correction = 0.6

    el_max_factor = 0.0
    el_max_factor_correction = 0.6

    u_vol_factor = 1.0
    u_vol_factor_correction = 1.0

    def __init__(self, model):
        # get a reference to the model engine
        self.model = model

    def scale_patient(
        self,
        target_weight: float,
        target_height: float,
        target_blood_volume: float,
        target_hr_ref: float,
        target_map: float,
    ):
        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor: float = (
            self.model.weight / target_weight * self.el_base_factor_correction
        )

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.resistance_factor: float = (
            self.model.weight / target_weight * self.resistance_factor_correction
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
        self.model.set_height(target_height)  # in m

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

        # the breathing, myocoardial oxygen balance and metabolism model are already weight dependent so no need to scale them

    def scale_blood_volume(self, new_blood_volume: float):
        self.model.models["Blood"].set_total_blood_volume(new_blood_volume)

    def scale_heart(self, heartrate_ref: float):
        # adjust the reference heartdate
        self.model.models["Heart"].set_heart_rate_ref(heartrate_ref)

        # adjust the heart
        for model in self.model.models.values():
            if model.is_enabled:
                if "BloodTimeVaryingElastance" in model.model_type:
                    model.el_min_scaling_factor = self.el_base_factor
                    model.el_max_scaling_factor = self.el_max_factor

        # adjust the elastance and unstressed volume of the pericardium
        self.model.models["PC"].u_vol_factor = self.u_vol_factor
        self.model.models["PC"].el_base_scaling_factor = self.el_base_factor

    def scale_circulatory_system(self):
        # adjust the resistance of the circulation
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "Resistor" in _model.model_type:
                    if "Blood" in _model._model_comp_from.model_type:
                        _model.r_for_scaling_factor = self.resistance_factor
                        _model.r_back_scaling_factor = self.resistance_factor

        # adjust the elastance of the circulation
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "BloodCapacitance" in _model.model_type:
                    _model.el_base_scaling_factor = self.el_base_factor

    def scale_respiratory_system(self):
        # adjust the elastance of the lungs
        self.model.models["ALL"].u_vol = (
            self.model.models["ALL"].u_vol * self.u_vol_factor
        )
        self.model.models["ALR"].u_vol = (
            self.model.models["ALR"].u_vol * self.u_vol_factor
        )

        self.model.models["ALL"].el_base_scaling_factor = self.el_base_factor
        self.model.models["ALR"].el_base_scaling_factor = self.el_base_factor

        # adjust the resistance of the airways
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "Resistor" in _model.model_type:
                    if "Gas" in _model._model_comp_from.model_type:
                        _model.r_for_scaling_factor = self.resistance_factor
                        _model.r_back_scaling_factor = self.resistance_factor

        # adjust the thorax
        self.model.models["THORAX"].u_vol = (
            self.model.models["THORAX"].u_vol * self.u_vol_factor
        )
        self.model.models["THORAX"].el_base_scaling_factor = self.el_base_factor

    def scale_ans(self, target_map: float):
        # adjust the baroreceptor
        self.model.models["Ans"].min_map = target_map / 2.0
        self.model.models["Ans"].set_map = target_map
        self.model.models["Ans"].max_map = target_map * 2.0
        self.model.models["Ans"].init_effectors()
