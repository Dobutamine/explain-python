import math

# blood volume according to gestational age: blood_volume = -1.4 * gest_age + 133.6     (24 weeks = 100 ml/kg and 42 weeks = 75 ml/kg)
# res and el_min relation with gest_age: factor = 0.0285 * gest_age - 0.085
# el_base and el_max relation with gest_age: factor = 0.014 * gest_age + 0.46


class Scaler:
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
    u_vol_factor_circ = 1.0
    u_vol_factor_circ_correction = 1.0
    u_vol_factor_resp = 1.0
    u_vol_factor_resp_correction = 1.0
    u_vol_ratio_factor = 1.0
    hr_ref: float = 110.0
    syst_ref: float = 66.0
    diast_ref: float = 40.0
    map_ref: float = 51.26
    resp_rate: float = 40.0
    vt_rr_ratio: float = 0.0001212
    mv_ref: float = 0.2

    heart_chambers = []
    heart_valves = []
    pericardium = []
    arteries = []
    veins = []
    capillaries = []
    shunts = []
    blood_connectors = []
    lungs = []
    airways = []
    thorax = []
    patients: dict = {}

    def __init__(self, model, **args: dict[str, any]):
        # set the model
        self.model = model
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

    def scale_to_weight(self, weight: float, height: float, output=False):
        # scale the patient
        self.scale_patient(
            weight=weight,
            height=height,
            blood_volume=0.08,
            lung_volume=0.03,
            res_circ_factor=1.0,
            el_base_circ_factor=1.0,
            el_min_circ_factor=1.0,
            el_max_circ_factor=1.0,
            res_resp_factor=1.0,
            el_base_resp_factor=1.0,
            u_vol_factor=1.0,
            hr_ref=150.0,
            syst_ref=67,
            diast_ref=40,
            map_ref=53,
            resp_rate=40.0,
            vt_rr_ratio=0.0001212,
            mv_ref=0.2,
        )

        if output:
            print(f"Scaling to weight {weight} kg and height {height} m")
            self.get_total_blood_volume()
            self.get_total_lung_volume()
            print(f"Systole target = {syst_ref} mmHg")
            print(f"Diastole target = {diast_ref} mmHg")
            print(f"Mean arterial pressure target = {map_ref} mmHg")
            print(f"Respiratory rate target = {resp_rate} bpm")
            print(f"Vt/RR ratio target = {vt_rr_ratio * self.model.weight} L/bpm/kg")
            print(f"Minute volume target = {mv_ref * self.model.weight} L/min")

    def scale_to_gestational_age(self, gestation_age: float, output=False):
        # get the scaling properties for the gestational age
        ga_props = self.patients[str(math.floor(gestation_age))]

        # scale the patient
        self.scale_patient(
            weight=ga_props["weight"],
            height=ga_props["height"],
            blood_volume=ga_props["blood_volume"],
            lung_volume=ga_props["lung_volume"],
            res_circ_factor=ga_props["res_circ_factor"],
            el_base_circ_factor=ga_props["el_base_circ_factor"],
            el_min_circ_factor=ga_props["el_min_circ_factor"],
            el_max_circ_factor=ga_props["el_max_circ_factor"],
            res_resp_factor=ga_props["res_resp_factor"],
            el_base_resp_factor=ga_props["el_base_resp_factor"],
            u_vol_factor=ga_props["u_vol_factor"],
            hr_ref=ga_props["hr_ref"],
            syst_ref=ga_props["syst_ref"],
            diast_ref=ga_props["diast_ref"],
            map_ref=ga_props["map_ref"],
            resp_rate=ga_props["resp_rate"],
            vt_rr_ratio=ga_props["vt_rr_ratio"],
            mv_ref=ga_props["mv_ref"],
        )

        if output:
            print(f"Scaling to gestational age {gestation_age} weeks")
            print(f"Weight (Fenton p50) = {self.model.weight} kg")
            print(f"Height (Fenton p50) = {self.model.height} m")
            self.get_total_blood_volume()
            self.get_total_lung_volume()
            print(f"Systole target = {ga_props['syst_ref']} mmHg")
            print(f"Diastole target = {ga_props['diast_ref']} mmHg")
            print(f"Mean arterial pressure target = {ga_props['map_ref']} mmHg")
            print(f"Respiratory rate target = {ga_props['resp_rate']} bpm")
            print(
                f"Vt/RR ratio target = {ga_props['vt_rr_ratio'] * self.model.weight} L/bpm/kg"
            )
            print(
                f"Minute volume target = {ga_props['mv_ref'] * self.model.weight} L/min"
            )

    def set_scale_factors(
        self,
        res_circ_factor: float,
        el_base_circ_factor: float,
        el_min_circ_factor: float,
        el_max_circ_factor: float,
        res_resp_factor: float,
        el_base_resp_factor: float,
        output=False,
    ):
        if output:
            print(
                f"Adjusting res_factor_circ_correction from {self.res_factor_circ_correction} to {res_circ_factor}"
            )
            print(
                f"Adjusting el_base_factor_circ_correction from {self.el_base_factor_circ_correction} to {el_base_circ_factor}"
            )
            print(
                f"Adjusting el_min_factor_circ_correction from {self.el_min_factor_correction} to {el_min_circ_factor}"
            )
            print(
                f"Adjusting el_max_factor_circ_correction from {self.el_max_factor_correction} to {el_max_circ_factor}"
            )
            print(
                f"Adjusting res_factor_resp_correction from {self.res_factor_resp_correction} to {res_resp_factor}"
            )
            print(
                f"Adjusting el_base_factor_resp_correction from {self.el_base_factor_resp_correction} to {el_base_resp_factor}"
            )

        self.res_factor_circ_correction = res_circ_factor
        self.el_base_factor_circ_correction = el_base_circ_factor
        self.el_min_factor_correction = el_min_circ_factor
        self.el_max_factor_correction = el_max_circ_factor
        self.res_factor_resp_correction = res_resp_factor
        self.el_base_factor_resp_correction = el_base_resp_factor

        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor_circ: float = (
            self.scale_factor * self.el_base_factor_circ_correction
        )

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.res_factor_circ: float = (
            self.scale_factor * self.res_factor_circ_correction
        )

        # calculate the el_max factor based on the weight change. The lower the weight the higher the el_max
        self.el_min_factor: float = self.scale_factor * self.el_min_factor_correction

        # calculate the el_max factor based on the weight change. The lower the weight the higher the el_max
        self.el_max_factor: float = self.scale_factor * self.el_max_factor_correction

        # calculate the elastance factor based on the weight change. The lower the weight the higher the elastance
        self.el_base_factor_resp: float = (
            self.scale_factor * self.el_base_factor_resp_correction
        )

        # calculate the resistance factor based on the weight change. The lower the weight the higher the resistance
        self.res_factor_resp: float = (
            self.scale_factor * self.res_factor_resp_correction
        )

        # calculate the u_vol factor based on the weight change. The lower the weight the lower the u_vol
        self.u_vol_factor_circ: float = (
            1.0 / self.scale_factor * self.u_vol_factor_circ_correction
        )

        self.u_vol_factor_resp: float = (
            1.0 / self.scale_factor * self.u_vol_factor_resp_correction
        )

        # scale the circulation
        self.scale_circulatory_system()

        # scale the heart
        self.scale_heart()

        # scale the respiratory system
        self.scale_respiratory_system()

    def scale_patient(
        self,
        weight: float,
        height: float,
        blood_volume: float,
        lung_volume: float,
        res_circ_factor: float,
        el_base_circ_factor: float,
        el_min_circ_factor: float,
        el_max_circ_factor: float,
        res_resp_factor: float,
        el_base_resp_factor: float,
        u_vol_factor: float,
        hr_ref: float,
        syst_ref: float,
        diast_ref: float,
        map_ref: float,
        resp_rate: float,
        vt_rr_ratio: float,
        mv_ref: float,
    ):
        # calculate the scale factor based on the weight change
        self.scale_factor: float = (
            self.model.weight / weight
        ) * self.scale_factor_correction

        # set the weight and height
        self.model.set_weight(weight)  # in kg
        self.model.set_height(height)  # in m

        # set the u_vol_ratio_factor
        self.u_vol_ratio_factor = u_vol_factor

        # scale the blood volume
        self.scale_blood_volume(blood_volume * weight)

        # scale the gas volume
        self.scale_lung_volume(lung_volume * weight)

        # set circulatory system reference values
        self.syst_ref = syst_ref
        self.diast_ref = diast_ref
        self.map_ref = map_ref
        # set the reference heartrate
        self.model.models["Heart"].set_heart_rate_ref(hr_ref)
        # scale the baroreflex of the autonomous nervous system
        self.scale_ans(map_ref)

        # set respiratory system reference values
        self.resp_rate_ref = resp_rate
        self.vt_rr_ratio_ref = vt_rr_ratio
        self.mv_ref = mv_ref
        self.model.models["Breathing"].set_resp_rate(self.resp_rate)
        self.model.models["Breathing"].set_vt_rr_ratio(self.vt_rr_ratio)
        self.model.models["Breathing"].set_mv_ref(mv_ref)

        # set the definitive scaling factors
        self.set_scale_factors(
            res_circ_factor,
            el_base_circ_factor,
            el_min_circ_factor,
            el_max_circ_factor,
            res_resp_factor,
            el_base_resp_factor,
            False,
        )

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
                        model.u_vol = (
                            model.vol * fraction_unstressed * self.u_vol_ratio_factor
                        )

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
                        model.u_vol = (
                            model.vol * fraction_unstressed * self.u_vol_ratio_factor
                        )

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
        for _heart_chamber in self.heart_chambers:
            self.model.models[_heart_chamber].el_min_scaling_factor = self.el_min_factor
            self.model.models[_heart_chamber].el_max_scaling_factor = self.el_max_factor

        # make sure the heart valves are not scaled disproportionally
        for _heart_valve in self.heart_valves:
            self.model.models[_heart_valve].r_scaling_factor = self.scale_factor

        # adjust the elastance and unstressed volume of the pericardium
        for _pericardium in self.pericardium:
            self.model.models[
                _pericardium
            ].el_base_scaling_factor = self.el_base_factor_circ
            self.model.models[
                _pericardium
            ].u_vol_scaling_factor = self.u_vol_factor_circ

    def scale_circulatory_system(self):
        # adjust the resistance of the circulation
        for _blood_connector in self.blood_connectors:
            self.model.models[_blood_connector].r_scaling_factor = self.res_factor_circ

        for _shunt in self.shunts:
            self.model.models[_shunt].r_scaling_factor = self.res_factor_circ

        # adjust the elastance of the circulation
        for _artery in self.arteries:
            self.model.models[_artery].el_base_scaling_factor = self.el_base_factor_circ

        for _veins in self.veins:
            self.model.models[_veins].el_base_scaling_factor = self.el_base_factor_circ

        for _capillary in self.capillaries:
            self.model.models[
                _capillary
            ].el_base_scaling_factor = self.el_base_factor_circ

    def scale_respiratory_system(self):
        # adjust the resistance of the airways
        for _airway in self.airways:
            self.model.models[_airway].r_scaling_factor = self.res_factor_resp

        # adjust the elastance of the respiratory system
        for _lung in self.lungs:
            self.model.models[_lung].el_base_scaling_factor = self.el_base_factor_resp

        # adjust the elastance and unstressed volumes of the thorax
        for _thorax in self.thorax:
            self.model.models[_thorax].el_base_scaling_factor = self.el_base_factor_resp
            self.model.models[_thorax].u_vol_scaling_factor = self.u_vol_factor_resp

    def scale_ans(self, map_ref: float):
        # adjust the baroreceptor
        self.model.models["Ans"].min_map = map_ref / 2.0
        self.model.models["Ans"].set_map = map_ref
        self.model.models["Ans"].max_map = map_ref * 2.0
        self.model.models["Ans"].init_effectors()

    def scale_metabolism(self):
        pass

    def scale_mob(self):
        pass
