import math

# blood volume according to gestational age: blood_volume = -1.4 * gest_age + 133.6     (24 weeks = 100 ml/kg and 42 weeks = 75 ml/kg)
# res and el_min relation with gest_age: factor = 0.0285 * gest_age - 0.085
# el_base and el_max relation with gest_age: factor = 0.014 * gest_age + 0.46


class Scaling:
    model = {}

    scale_factor: float = 1.0
    scale_factor_correction: float = 1.0

    el_base_factor_circ = 1.0
    el_base_factor_circ_correction = 1.0

    el_base_factor_resp = 1.0
    el_base_factor_resp_correction = 1.0

    res_factor_circ = 1.0
    res_factor_circ_correction = 0.8  # for 1.5 kg and 0.6 for 0.75 kg

    res_factor_resp = 1.0
    res_factor_resp_correction = 1.0

    el_min_factor = 1.0
    el_min_factor_correction = 1.0

    el_max_factor = 1.0
    el_max_factor_correction = 0.9  # for 1.5 kg and 0.8 for 0.75 kg

    u_vol_factor_circ = 1.0
    u_vol_factor_circ_correction = 1.0

    u_vol_factor_resp = 1.0
    u_vol_factor_resp_correction = 1.0

    hr_ref: float = 140.0
    mv_ref: float = 0.0

    hr_target: float = 0.0
    lvo_target: float = 0.0
    mv_target: float = 0.0
    resp_rate_target: float = 0.0

    map_ref: float = 50.0

    scaling_dict: dict = {
        "24": {
            "weight": 0.75,
        }
    }

    def __init__(self, model):
        # get a reference to the model engine
        self.model = model

    def scale_to_weight(self, weight: float):
        pass

    def scale_to_gestation_age(self, gestation_age: float):
        pass
        # # adjust the elastance of the circulation
        # self.el_base_factor_circ_correction = 1.0

        # # adjust the resistance of the circulation
        # self.res_factor_circ_correction = 1.0

        # # adjusr the heart function of the circulation
        # self.el_min_factor_correction = 1.0
        # self.el_max_factor_correction = 1.0

    def scale_to_postnatal_age(self, postnatal_age: float):
        pass

    def set_scale_factors(self, output=False):
        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor_circ: float = (
            self.scale_factor * self.el_base_factor_circ_correction
        )
        if output:
            print(f"el_base_factor_circ = {self.el_base_factor_circ}")

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.res_factor_circ: float = (
            self.scale_factor * self.res_factor_circ_correction
        )
        if output:
            print(f"res_factor_circ = {self.res_factor_circ}")

        # calculate the el_max factor based on the weight change. The lower the weight the higher the el_max
        self.el_min_factor: float = self.scale_factor * self.el_min_factor_correction
        if output:
            print(f"el_min_factor = {self.el_min_factor}")

        # calculate the el_max factor based on the weight change. The lower the weight the higher the el_max
        self.el_max_factor: float = self.scale_factor * self.el_max_factor_correction
        if output:
            print(f"el_max_factor = {self.el_max_factor}")

        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor_resp: float = (
            self.scale_factor * self.el_base_factor_resp_correction
        )
        if output:
            print(f"el_base_factor_resp = {self.el_base_factor_resp}")

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.res_factor_resp: float = (
            self.scale_factor * self.res_factor_resp_correction
        )
        if output:
            print(f"res_factor_resp = {self.res_factor_resp}")

        # calculate the u_vol factor based on the weight change. The lower the weight the lower the u_vol
        self.u_vol_factor_circ: float = (
            1.0 / self.scale_factor * self.u_vol_factor_circ_correction
        )
        if output:
            print(f"u_vol_factor_circ = {self.u_vol_factor_circ}")

        self.u_vol_factor_resp: float = (
            1.0 / self.scale_factor * self.u_vol_factor_resp_correction
        )
        if output:
            print(f"u_vol_factor_resp = {self.u_vol_factor_resp}")

    def scale_patient(
        self,
        gest_age: float,
        postnatal_age: float,
        weight: float,
        height: float,
        blood_volume: float,
        lung_volume: float,
        hr_ref: float,
        map: float,
    ):
        self.res_factor_circ_correction = 0.6
        self.el_base_factor_circ_correction = 0.8
        self.el_min_factor_correction = 0.6
        self.el_max_factor_correction = 0.8

        # calculate the scale factor based on the weight change
        self.scale_factor: float = (
            self.model.weight / weight
        ) * self.scale_factor_correction

        # set the weight and height
        self.model.set_weight(weight)  # in kg
        self.model.set_height(height)  # in m

        # scale the blood volume
        self.scale_blood_volume(blood_volume * weight)

        # scale the gas volume
        self.scale_lung_volume(lung_volume * weight)

        # set the reference heartrate
        self.model.models["Heart"].set_heart_rate_ref(hr_ref)

        # adjust the corrections depending on the gestational age
        self.scale_to_gestation_age(gest_age)

        # adjust the corrections depending on the postnatal age
        self.scale_to_postnatal_age(postnatal_age)

        # set the definitive scaling factors
        self.set_scale_factors()

        # scale the circulation
        self.scale_circulatory_system()

        # scale the heart
        self.scale_heart()

        # scale the respiratory system
        self.scale_respiratory_system()

        # scale the baroreflex of the autonomous nervous system
        self.scale_ans(map)

        # scale the metabolism
        self.scale_metabolism()

        # scale the myocardial oxygen balance and metabolism
        self.scale_mob()

    def get_total_lung_volume(self, output=True) -> float:
        total_gas_volume: float = 0.0

        for model in self.model.models.values():
            if "GasCapacitance" in model.model_type:
                if model.is_enabled and model.fixed_composition == False:
                    try:
                        total_gas_volume += model.vol
                    except:
                        total_gas_volume += 0.0
        if output:
            print(
                f"Total gas volume = {total_gas_volume * 1000.0} ml ({total_gas_volume * 1000.0 / self.model.weight} ml/kg)"
            )

        return total_gas_volume

    def get_total_blood_volume(self, output=True) -> float:
        total_blood_volume: float = 0.0

        for model in self.model.models.values():
            if "Blood" in model.model_type:
                if model.is_enabled:
                    try:
                        total_blood_volume += model.vol
                    except:
                        total_blood_volume += 0.0
        if output:
            print(
                f"Total blood volume = {total_blood_volume * 1000.0} ml ({total_blood_volume * 1000.0 / self.model.weight} ml/kg)"
            )

        return total_blood_volume

    def scale_lung_volume(self, new_gas_volume: float, output=False) -> None:
        # get the current gas volume
        current_gas_volume = self.get_total_lung_volume(output=False)

        # divide the new gas volume over all gas containing capacitances
        for model in self.model.models.values():
            # select all gas containing capacitances
            if "GasCapacitance" in model.model_type:
                if model.is_enabled and model.fixed_composition == False:
                    try:
                        # calculate the current fraction of the gas volume in this gas containing capacitance
                        current_fraction = model.vol / current_gas_volume
                        if output:
                            print(
                                f"{model.name} volume = {model.vol * 1000.0} ml -> ",
                                end="",
                            )
                        # calculate the fraction of the unstressed volume of the current volume
                        fraction_unstressed = 0.0
                        if model.vol > 0.0:
                            fraction_unstressed = model.u_vol / model.vol

                        # now change the total volume by adding the same fraction of the desired volume change to the gas containing capacitance
                        model.vol += current_fraction * (
                            new_gas_volume - current_gas_volume
                        )

                        # determine how much of this total volume is unstressed volume
                        model.u_vol = model.vol * fraction_unstressed

                        # guard for negative volumes
                        if model.vol < 0.0:
                            model.vol = 0.0

                        if output:
                            print(
                                f"{model.vol * 1000.0} ml = ({current_fraction * 100}% of total gas volume)"
                            )
                    except:
                        current_fraction = 0

    def scale_blood_volume(self, new_blood_volume: float, output=False) -> None:
        # get the current blood volume
        current_blood_volume = self.get_total_blood_volume(output=False)

        # divide the new blood volume over all blood holding capacitances
        for model in self.model.models.values():
            # select all blood containing capacitances
            if "BloodCapacitance" in model.model_type:
                if model.is_enabled:
                    try:
                        # calculate the current fraction of the blood volume in this blood containing capacitance
                        current_fraction = model.vol / current_blood_volume
                        if output:
                            print(
                                f"{model.name} volume = {model.vol * 1000.0} ml -> ",
                                end="",
                            )
                        # calculate the fraction of the unstressed volume of the current volume
                        fraction_unstressed = 0.0
                        if model.vol > 0.0:
                            fraction_unstressed = model.u_vol / model.vol

                        # now change the total volume by adding the same fraction of the desired volume change to the blood containing capacitance
                        model.vol += current_fraction * (
                            new_blood_volume - current_blood_volume
                        )

                        # determine how much of this total volume is unstressed volume
                        model.u_vol = model.vol * fraction_unstressed

                        # guard for negative volumes
                        if model.vol < 0.0:
                            model.vol = 0.0

                        if output:
                            print(
                                f"{model.vol * 1000.0} ml = ({current_fraction * 100}% of total blood volume)"
                            )
                    except:
                        current_fraction = 0

            if "BloodTimeVaryingElastance" in model.model_type:
                if model.is_enabled:
                    try:
                        # calculate the current fraction of the blood volume in this blood containing capacitance
                        current_fraction = model.vol / current_blood_volume
                        if output:
                            print(
                                f"{model.name} volume = {model.vol * 1000.0} ml -> ",
                                end="",
                            )
                        # calculate the fraction of the unstressed volume of the current volume
                        fraction_unstressed = 0.0
                        if model.vol > 0.0:
                            fraction_unstressed = model.u_vol / model.vol

                        # now change the total volume by adding the same fraction of the desired volume change to the blood containing capacitance
                        model.vol += current_fraction * (
                            new_blood_volume - current_blood_volume
                        )

                        # determine how much of this total volume is unstressed volume
                        model.u_vol = model.vol * fraction_unstressed

                        # guard for negative volumes
                        if model.vol < 0.0:
                            model.vol = 0.0
                        if output:
                            print(
                                f"{model.vol * 1000.0} ml = ({current_fraction * 100}% of total blood volume)"
                            )
                    except:
                        current_fraction = 0

    def scale_heart(self):
        # adjust the heart elastances
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "BloodTimeVaryingElastance" in _model.model_type:
                    _model.el_min_scaling_factor = self.el_min_factor
                    _model.el_max_scaling_factor = self.el_max_factor

        # adjust the elastance and unstressed volume of the pericardium
        self.model.models["PC"].u_vol_scaling_factor = self.u_vol_factor_circ
        self.model.models["PC"].el_base_scaling_factor = self.el_base_factor_circ

        # make sure the heart valves are not scaled disproportionally
        self.model.models["LV_AA"].r_scaling_factor = self.scale_factor
        self.model.models["RV_PA"].r_scaling_factor = self.scale_factor
        self.model.models["LA_LV"].r_scaling_factor = self.scale_factor
        self.model.models["RA_RV"].r_scaling_factor = self.scale_factor

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
        # adjust the resistance of the airways
        for _model in self.model.models.values():
            if _model.is_enabled:
                if "Resistor" in _model.model_type:
                    if "Gas" in _model._model_comp_from.model_type:
                        _model.r_scaling_factor = self.res_factor_resp

        # adjust the elastance of the respiratory system
        for _model in self.model.models.values():
            if _model.is_enabled:
                if (
                    _model.model_type == "GasCapacitance"
                    and _model.fixed_composition == False
                ):
                    _model.el_base_scaling_factor = self.el_base_factor_resp

        # adjust the elastance of the respiratory system
        self.model.models["THORAX"].el_base_scaling_factor = self.el_base_factor_resp
        self.model.models["CHEST_L"].el_base_scaling_factor = self.el_base_factor_resp
        self.model.models["CHEST_R"].el_base_scaling_factor = self.el_base_factor_resp

        # adjust the unstressed volume of the respiratory system
        self.model.models["THORAX"].u_vol_scaling_factor = self.u_vol_factor_resp
        self.model.models["CHEST_L"].u_vol_scaling_factor = self.u_vol_factor_resp
        self.model.models["CHEST_R"].u_vol_scaling_factor = self.u_vol_factor_resp

    def scale_ans(self, map: float):
        # adjust the baroreceptor
        self.model.models["Ans"].min_map = map / 2.0
        self.model.models["Ans"].set_map = map
        self.model.models["Ans"].max_map = map * 2.0
        self.model.models["Ans"].init_effectors()

    def scale_metabolism(self):
        pass

    def scale_mob(self):
        pass
