import math

# blood volume according to gestational age: blood_volume = -1.4 * gest_age + 133.6     (24 weeks = 100 ml/kg and 42 weeks = 75 ml/kg)
# res and el_min relation with gest_age: factor = 0.0285 * gest_age - 0.085
# el_base and el_max relation with gest_age: factor = 0.014 * gest_age + 0.46


class Scaler:
    # reference to the entire model
    model = {}

    reference_weight: float = 3.545

    # model components which need te be scaled
    left_atrium = []
    right_atrium = []
    left_ventricle = []
    right_ventricle = []
    coronaries = []
    arteries = []
    veins = []
    capillaries = []

    heart_valves = []
    shunts = []
    blood_connectors = []
    pericardium = []
    lungs = []
    airways = []
    thorax = []

    # preprogrammed scaling factors
    patients: dict = {}

    # general scaler
    scale_factor: float = 1.0

    # scaler based on weight
    scale_factor_weight: float = 1.0

    # scaler based on gestational age
    scale_factor_gestational_age: float = 1.0

    # scaler based on age
    scale_factor_age: float = 1.0

    # blood volume in L/kg
    blood_volume: float = 0.08

    # lung volume in L/kg
    lung_volume: float = 0.03

    # reference heartrate in bpm (-1 = no change) neonate = 110.0
    hr_ref: float = -1.0

    # reference mean arterial pressure in mmHg (-1 = no change) neonate = 51.26
    map_ref: float = -1.0

    # reference respiratory rate in bpm (-1 = no change) neonate = 40
    resp_rate_ref: float = -1.0

    # vt/rr ratio in L/bpm/kg (-1 = no change) neonate = 0.0001212
    vt_rr_ratio: float = -1.0

    # reference minute volume in L/min (-1 = no change) neonate = 0.2
    mv_ref: float = -1.0

    # oxygen consumption in ml/min/kg (-1 = no change)
    vo2: float = -1.0

    # respiratory quotient  (-1 = no change)
    resp_q: float = -1.0

    # heart chamber scalers
    el_min_ra_factor = 1.0
    el_max_ra_factor = 1.0
    u_vol_ra_factor = 1.0

    el_min_rv_factor = 1.0
    el_max_rv_factor = 1.0
    u_vol_rv_factor = 1.0

    el_min_la_factor = 1.0
    el_min_lv_factor = 1.0
    u_vol_la_factor = 1.0

    el_max_la_factor = 1.0
    el_max_lv_factor = 1.0
    u_vol_lv_factor = 1.0

    # coronary scalers
    el_min_cor_factor = 1.0
    el_max_cor_factor = 1.0
    u_vol_cor_factor = 1.0

    # heart valve scalers
    res_valve_factor = 1.0

    # pericardium scalers
    el_base_pericardium_factor = 1.0
    u_vol_pericardium_factor = 1.0

    # arteries
    el_base_art_factor = 1.0
    u_vol_art_factor = 1.0

    # veins
    el_base_ven_factor = 1.0
    u_vol_ven_factor = 1.0

    # capillaries
    el_base_cap_factor = 1.0
    u_vol_cap_factor = 1.0

    # blood connectors
    res_blood_connectors_factor = 1.0

    # lungs
    el_base_lungs_factor = 1.0
    u_vol_lungs_factor = 1.0

    # airways
    res_airway_factor = 1.0

    # thorax
    el_base_thorax_factor = 1.0
    u_vol_thorax_factor = 1.0

    def __init__(self, model, **args: dict[str, any]):
        # set the model
        self.model = model
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # set the reference weight
        self.reference_weight = self.model.weight

    def scale_patient(
        self,
        scale_factor: float = 1.0,
        scale_by_weight: bool = False,
        scale_by_gestational_age: bool = False,
        scale_by_age: bool = False,
        blood_volume: float = -1.0,
        weight: float = -1.0,
        height: float = -1.0,
        gestation_age: float = -1.0,
        age: float = -1.0,
        hr_ref: float = -1.0,
        map_ref: float = -1.0,
        el_min_ra_factor: float = 1.0,
        el_max_ra_factor: float = 1.0,
        u_vol_ra_factor: float = 1.0,
        el_min_rv_factor: float = 1.0,
        el_max_rv_factor: float = 1.0,
        u_vol_rv_factor: float = 1.0,
        el_min_la_factor: float = 1.0,
        el_max_la_factor: float = 1.0,
        u_vol_la_factor: float = 1.0,
        el_min_lv_factor: float = 1.0,
        el_max_lv_factor: float = 1.0,
        u_vol_lv_factor: float = 1.0,
        el_min_cor_factor: float = 1.0,
        el_max_cor_factor: float = 1.0,
        u_vol_cor_factor: float = 1.0,
        res_valve_factor: float = 1.0,
        el_base_pericardium_factor: float = 1.0,
        u_vol_pericardium_factor: float = 1.0,
        el_base_art_factor: float = 1.0,
        u_vol_art_factor: float = 1.0,
        el_base_ven_factor: float = 1.0,
        u_vol_ven_factor: float = 1.0,
        el_base_cap_factor: float = 1.0,
        u_vol_cap_factor: float = 1.0,
        res_blood_connectors_factor: float = 1.0,
        lung_volume: float = -1.0,
        el_base_lungs_factor: float = 1.0,
        u_vol_lungs_factor: float = 1.0,
        res_airway_factor: float = 1.0,
        el_base_thorax_factor: float = 1.0,
        u_vol_thorax_factor: float = 1.0,
        resp_rate_ref: float = -1.0,
        vt_rr_ratio: float = -1.0,
        mv_ref: float = -1.0,
        vo2: float = -1.0,
        resp_q: float = -1.0,
        output: bool = False,
    ):
        # get the current weight
        current_weight = self.model.weight

        # calculate the scale factor based on the weight change
        self.weight = self.model.weight
        if weight > 0.0:
            if output:
                print(f"Adjusted weight from {self.weight} to {weight}")
            if scale_by_weight:
                print(
                    f"Scaling by weight {weight} to reference weight {self.reference_weight} kg"
                )
                self.scale_factor_weight = self.reference_weight / weight
            self.model.set_weight(weight)
            self.weight = self.model.weight

        # set the height
        self.height = self.model.height
        if height > 0.0:
            if output:
                print(f"Adjusted height from {self.height} to {height}")
            self.model.set_height(height)
            self.height = self.model.height

        # set the gestational age
        self.gestation_age = gestation_age
        if gestation_age > 0.0:
            if output:
                print(
                    f"Adjusted gestational age from {self.gestation_age} to {gestation_age}"
                )
            if scale_by_gestational_age:
                print(f"Scaling by gestational age")
                self.scale_factor_gestational_age = self.gestation_age / gestation_age
            self.scale_factor_gestational_age: float = (
                self.gestation_age / gestation_age
            )

        # set the age
        self.age = age
        if age > 0.0:
            if output:
                print(f"Adjusted age from {self.age} to {age}")
            if scale_by_age:
                print(f"Scaling by age")
                self.scale_factor_age = self.age / age
            self.scale_factor_age: float = self.age / age

        # calculate the definitive scale factor
        self.scale_factor = (
            1.0
            * self.scale_factor_weight
            * self.scale_factor_gestational_age
            * self.scale_factor_age
        )
        if scale_factor > 0.0:
            # scale factor of 2 means that the elastances and resistances are halved and the volumes are doubled
            self.scale_factor: float = (
                scale_factor
                * self.scale_factor_weight
                * self.scale_factor_gestational_age
                * self.scale_factor_age
            )

        if output:
            print(f"Global scaling factor = {self.scale_factor}")

        # scale the blood volume according to weight
        self.blood_volume = self.get_total_blood_volume(output=False) / current_weight
        # if scaled by weight and the bloodvolume is not explicitely set, scale the blood volume according to new weight
        if scale_by_weight and blood_volume < 0.0:
            blood_volume = self.blood_volume

        if blood_volume > 0.0:
            if output:
                print(
                    f"Adjusted blood volume from {self.blood_volume * 1000.0 * current_weight} ml ({self.blood_volume * 1000.0} ml/kg) to {blood_volume * 1000.0 * weight} ml  ({blood_volume * 1000.0} ml/kg)"
                )
            self.scale_blood_volume(blood_volume * self.weight)

        # scale the lung volume according to weight
        self.lung_volume = self.get_total_lung_volume(output=False) / current_weight
        # if scaled by weight and the lung volume is not explicitely set, scale the lung volume according to new weight
        if scale_by_weight and lung_volume < 0.0:
            lung_volume = self.lung_volume

        if lung_volume > 0.0:
            if output:
                print(
                    f"Adjusted lung volume from {self.lung_volume * 1000.0 * current_weight} ml ({self.lung_volume * 1000.0} ml/kg) to {lung_volume * 1000.0 * weight} ml  ({lung_volume * 1000.0} ml/kg)"
                )
            self.scale_lung_volume(lung_volume * self.weight)

        # scale the baroreflex of the autonomous nervous system
        self.map_ref = self.model.models["Ans"].set_map
        if map_ref > 0.0:
            if output:
                print(
                    f"Adjusted mean arterial pressure from {self.map_ref} to {map_ref}"
                )
            self.scale_ans(map_ref)
            self.map_ref = map_ref

        # set the reference heartrate
        self.hr_ref = self.model.models["Heart"].heart_rate_ref
        if hr_ref > 0.0:
            if output:
                print(f"Adjusted heart rate from {self.hr_ref} bpm to {hr_ref} bpm")
            self.model.models["Heart"].set_heart_rate_ref(hr_ref)
            self.hr_ref = hr_ref

        # set respiratory rate
        self.resp_rate_ref = self.model.models["Breathing"].resp_rate
        if resp_rate_ref > 0.0:
            if output:
                print(
                    f"Adjusted respiratory rate from {self.resp_rate_ref} bpm to {resp_rate_ref} bpm"
                )
            self.model.models["Breathing"].set_resp_rate(self.resp_rate_ref)
            self.resp_rate_ref = resp_rate_ref

        # set the vt/rr ratio
        self.vt_rr_ratio = self.model.models["Breathing"].vt_rr_ratio
        if vt_rr_ratio > 0.0:
            if output:
                print(
                    f"Adjusted vt/rr ratio from {self.vt_rr_ratio} L/bpm/kg to {vt_rr_ratio} L/bpm/kg"
                )
            self.model.models["Breathing"].set_vt_rr_ratio(self.vt_rr_ratio)
            self.vt_rr_ratio = vt_rr_ratio

        # set the reference minute volume
        self.mv_ref = self.model.models["Breathing"].minute_volume_ref
        if mv_ref > 0.0:
            if output:
                print(
                    f"Adjusted minute volume from {self.mv_ref} L/min to {mv_ref} L/min"
                )
            self.model.models["Breathing"].set_mv_ref(mv_ref)
            self.mv_ref = mv_ref

        # set the definitive scaling factors for the heart chambers
        self.el_min_ra_factor = self.scale_factor
        if el_min_ra_factor != 1.0:
            if output:
                print(
                    f"Adjusted minimum right atrial elastance scaling factor to {el_min_ra_factor * self.scale_factor}"
                )
            self.el_min_ra_factor = self.scale_factor * el_min_ra_factor

        self.el_max_ra_factor = self.scale_factor
        if el_max_ra_factor != 1.0:
            if output:
                print(
                    f"Adjusted maximum right atrial elastance scaling factor to {el_max_ra_factor * self.scale_factor}"
                )
            self.el_max_ra_factor = self.scale_factor * el_max_ra_factor

        self.u_vol_ra_factor = 1.0
        if u_vol_ra_factor != 1.0:
            if output:
                print(
                    f"Adjusted right atrial unstressed volume scaling factor to {u_vol_ra_factor}"
                )
            self.u_vol_ra_factor = u_vol_ra_factor

        self.el_min_rv_factor = self.scale_factor
        if el_min_rv_factor != 1.0:
            if output:
                print(
                    f"Adjusted minimum right ventricular elastance scaling factor to {el_min_rv_factor * self.scale_factor}"
                )
            self.el_min_rv_factor = self.scale_factor * el_min_rv_factor

        self.el_max_rv_factor = self.scale_factor
        if el_max_rv_factor != 1.0:
            if output:
                print(
                    f"Adjusted maximum right ventricular elastance scaling factor to {el_max_rv_factor * self.scale_factor}"
                )
            self.el_max_rv_factor = self.scale_factor * el_max_rv_factor

        self.u_vol_rv_factor = 1.0
        if u_vol_rv_factor != 1.0:
            if output:
                print(
                    f"Adjusted right ventricular unstressed volume scaling factor to {u_vol_rv_factor}"
                )
            self.u_vol_rv_factor = u_vol_rv_factor

        self.el_min_la_factor = self.scale_factor
        if el_min_la_factor != 1.0:
            if output:
                print(
                    f"Adjusted minimum left atrial elastance scaling factor to {el_min_la_factor * self.scale_factor}"
                )
            self.el_min_la_factor = self.scale_factor * el_min_la_factor

        self.el_max_la_factor = self.scale_factor
        if el_max_la_factor != 1.0:
            if output:
                print(
                    f"Adjusted maximum left atrial elastance scaling factor to {el_max_la_factor * self.scale_factor}"
                )
            self.el_max_la_factor = self.scale_factor * el_max_la_factor

        self.u_vol_la_factor = 1.0
        if u_vol_la_factor != 1.0:
            if output:
                print(
                    f"Adjusted left atrial unstressed volume scaling factor to {u_vol_la_factor}"
                )
            self.u_vol_la_factor = u_vol_la_factor

        self.el_min_lv_factor = self.scale_factor
        if el_min_lv_factor != 1.0:
            if output:
                print(
                    f"Adjusted minimum left ventricular elastance scaling factor to {el_min_lv_factor * self.scale_factor}"
                )
            self.el_min_lv_factor = self.scale_factor * el_min_lv_factor

        self.el_max_lv_factor = self.scale_factor
        if el_max_lv_factor != 1.0:
            if output:
                print(
                    f"Adjusted maximum left ventricular elastance scaling factor to {el_max_lv_factor * self.scale_factor}"
                )
            self.el_max_lv_factor = self.scale_factor * el_max_lv_factor

        self.u_vol_lv_factor = 1.0
        if u_vol_lv_factor != 1.0:
            if output:
                print(
                    f"Adjusted left ventricular unstressed volume scaling factor to {u_vol_lv_factor}"
                )
            self.u_vol_lv_factor = u_vol_lv_factor

        # set the definitive scaling factors for the coronary circulation
        self.el_min_cor_factor = self.scale_factor
        if el_min_cor_factor != 1.0:
            if output:
                print(
                    f"Adjusted minimum coronary elastance scaling factor to {el_min_cor_factor * self.scale_factor}"
                )
            self.el_min_cor_factor = self.scale_factor * el_min_cor_factor

        self.el_max_cor_factor = self.scale_factor
        if el_max_cor_factor != 1.0:
            if output:
                print(
                    f"Adjusted maximum coronary elastance scaling factor to {el_max_cor_factor * self.scale_factor}"
                )
            self.el_max_cor_factor = self.scale_factor * el_max_cor_factor

        self.u_vol_cor_factor = 1.0
        if u_vol_cor_factor != 1.0:
            if output:
                print(
                    f"Adjusted coronary unstressed volume scaling factor to {u_vol_cor_factor}"
                )
            self.u_vol_cor_factor = u_vol_cor_factor

        # set the definitive scaling factors for the arteries
        self.el_base_art_factor = self.scale_factor
        if el_base_art_factor != 1.0:
            if output:
                print(
                    f"Adjusted arterial elastance scaling factor to {el_base_art_factor * self.scale_factor}"
                )
            self.el_base_art_factor = self.scale_factor * el_base_art_factor

        self.u_vol_art_factor = 1.0
        if u_vol_art_factor != 1.0:
            if output:
                print(
                    f"Adjusted arterial unstressed volume scaling factor to {u_vol_art_factor}"
                )
            self.u_vol_art_factor = u_vol_art_factor

        # set the definitive scaling factors for the veins
        self.el_base_ven_factor = self.scale_factor
        if el_base_ven_factor != 1.0:
            if output:
                print(
                    f"Adjusted venous elastance scaling factor to {el_base_ven_factor * self.scale_factor}"
                )
            self.el_base_ven_factor = self.scale_factor * el_base_ven_factor

        self.u_vol_ven_factor = 1.0
        if u_vol_ven_factor != 1.0:
            if output:
                print(
                    f"Adjusted venous unstressed volume scaling factor to {u_vol_ven_factor}"
                )
            self.u_vol_ven_factor = u_vol_ven_factor

        # set the definitive scaling factors for the capillaries
        self.el_base_cap_factor = self.scale_factor
        if el_base_cap_factor != 1.0:
            if output:
                print(
                    f"Adjusted capillary elastance scaling factor to {el_base_cap_factor * self.scale_factor}"
                )
            self.el_base_cap_factor = self.scale_factor * el_base_cap_factor

        self.u_vol_cap_factor = 1.0
        if u_vol_cap_factor != 1.0:
            if output:
                print(
                    f"Adjusted capillary unstressed volume scaling factor to {u_vol_cap_factor}"
                )
            self.u_vol_cap_factor = u_vol_cap_factor

        # set the definitive scaling factors for the blood connectors
        self.res_blood_connectors_factor = self.scale_factor
        if res_blood_connectors_factor != 1.0:
            if output:
                print(
                    f"Adjusted blood connector resistance scaling factor to {res_blood_connectors_factor * self.scale_factor}"
                )
            self.res_blood_connectors_factor = (
                self.scale_factor * res_blood_connectors_factor
            )

        # set the definitive scaling factors for the heart valves
        self.res_valve_factor = self.scale_factor
        if res_valve_factor != 1.0:
            if output:
                print(
                    f"Adjusted heart valve resistance scaling factor to {res_valve_factor * self.scale_factor}"
                )
            self.res_valve_factor = self.scale_factor * res_valve_factor

        # set the definitive scaling factors for the pericardium
        self.el_base_pericardium_factor = self.scale_factor
        if el_base_pericardium_factor != 1.0:
            if output:
                print(
                    f"Adjusted pericardium elastance scaling factor to {el_base_pericardium_factor * self.scale_factor}"
                )
            self.el_base_pericardium_factor = (
                self.scale_factor * el_base_pericardium_factor
            )

        self.u_vol_pericardium_factor = 1.0 / self.scale_factor
        if u_vol_pericardium_factor != 1.0:
            if output:
                print(
                    f"Adjusted pericardium unstressed volume scaling factor to {1.0 / (u_vol_pericardium_factor * self.scale_factor)}"
                )
            self.u_vol_pericardium_factor = 1.0 / (
                self.scale_factor * u_vol_pericardium_factor
            )

        # set the definitive scaling factors for the lungs
        self.el_base_lungs_factor = self.scale_factor
        if el_base_lungs_factor != 1.0:
            if output:
                print(
                    f"Adjusted lung elastance scaling factor to {el_base_lungs_factor * self.scale_factor}"
                )
            self.el_base_lungs_factor = self.scale_factor * el_base_lungs_factor

        self.u_vol_lungs_factor = 1.0
        if u_vol_lungs_factor != 1.0:
            if output:
                print(
                    f"Adjusted lung unstressed volume scaling factor to {u_vol_lungs_factor}"
                )
            self.u_vol_lungs_factor = u_vol_lungs_factor

        # set the definitive scaling factors for the airways
        self.res_airway_factor = self.scale_factor
        if res_airway_factor != 1.0:
            if output:
                print(
                    f"Adjusted airway resistance scaling factor to {res_airway_factor * self.scale_factor}"
                )
            self.res_airway_factor = self.scale_factor * res_airway_factor

        # set the definitive scaling factors for the thorax
        self.el_base_thorax_factor = self.scale_factor
        if el_base_thorax_factor != 1.0:
            if output:
                print(
                    f"Adjusted thorax elastance scaling factor to {el_base_thorax_factor * self.scale_factor}"
                )
            self.el_base_thorax_factor = self.scale_factor * el_base_thorax_factor

        self.u_vol_thorax_factor = 1.0 / self.scale_factor
        if u_vol_thorax_factor != 1.0:
            if output:
                print(
                    f"Adjusted thorax unstressed volume scaling factor to {1.0 / (u_vol_thorax_factor * self.scale_factor)}"
                )
            self.u_vol_thorax_factor = 1.0 / (self.scale_factor * u_vol_thorax_factor)

        # set the definitive scaling factors for the shunts
        self.res_shunt_factor = self.scale_factor
        if res_blood_connectors_factor != 1.0:
            if output:
                print(
                    f"Adjusted shunt resistance scaling factor to {res_blood_connectors_factor * self.scale_factor}"
                )
            self.res_shunt_factor = self.scale_factor * res_blood_connectors_factor

        # scale the heart
        self.scale_heart()

        # scale the circulation
        self.scale_circulatory_system()

        # scale the respiratory system
        self.scale_respiratory_system()

        # scale the metabolism
        self.scale_metabolism()

        # scale the myocardial oxygen balance and metabolism
        self.scale_mob()

    def get_total_lung_volume(self, output=True) -> float:
        total_gas_volume: float = 0.0

        # build an array holding all gas containing capacitances
        gas_containing_capacitances = self.lungs

        for model_name in gas_containing_capacitances:
            model = self.model.models[model_name]
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

        # build an array holding all blood containing capacitances
        blood_containing_capacitances = (
            self.arteries
            + self.veins
            + self.capillaries
            + self.left_atrium
            + self.right_atrium
            + self.left_ventricle
            + self.right_ventricle
            + self.coronaries
        )

        for model_name in blood_containing_capacitances:
            model = self.model.models[model_name]
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

        # build an array holding all gas containing capacitances
        gas_containing_capacitances = self.lungs

        for model_name in gas_containing_capacitances:
            model = self.model.models[model_name]
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

        # build an array holding all blood containing capacitances
        blood_containing_capacitances = (
            self.arteries
            + self.veins
            + self.capillaries
            + self.left_atrium
            + self.right_atrium
            + self.left_ventricle
            + self.right_ventricle
            + self.coronaries
        )

        # divide the new blood volume over all blood holding capacitances
        for model_name in blood_containing_capacitances:
            model = self.model.models[model_name]
            # select all blood containing capacitances
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
        # scale the left atrium
        for _left_atrium in self.left_atrium:
            self.model.models[
                _left_atrium
            ].el_min_scaling_factor = self.el_min_la_factor
            self.model.models[
                _left_atrium
            ].el_max_scaling_factor = self.el_max_la_factor
            self.model.models[_left_atrium].u_vol_scaling_factor = self.u_vol_la_factor

        # scale the right atrium
        for _right_atrium in self.right_atrium:
            self.model.models[
                _right_atrium
            ].el_min_scaling_factor = self.el_min_ra_factor
            self.model.models[
                _right_atrium
            ].el_max_scaling_factor = self.el_max_ra_factor
            self.model.models[_right_atrium].u_vol_scaling_factor = self.u_vol_ra_factor

        # scale the left ventricle
        for _left_ventricle in self.left_ventricle:
            self.model.models[
                _left_ventricle
            ].el_min_scaling_factor = self.el_min_lv_factor
            self.model.models[
                _left_ventricle
            ].el_max_scaling_factor = self.el_max_lv_factor
            self.model.models[
                _left_ventricle
            ].u_vol_scaling_factor = self.u_vol_lv_factor

        # scale the right ventricle
        for _right_ventricle in self.right_ventricle:
            self.model.models[
                _right_ventricle
            ].el_min_scaling_factor = self.el_min_rv_factor
            self.model.models[
                _right_ventricle
            ].el_max_scaling_factor = self.el_max_rv_factor
            self.model.models[
                _right_ventricle
            ].u_vol_scaling_factor = self.u_vol_rv_factor

        # scale the coronary circulation
        for _coronary in self.coronaries:
            self.model.models[_coronary].el_min_scaling_factor = self.el_min_cor_factor
            self.model.models[_coronary].el_max_scaling_factor = self.el_max_cor_factor
            self.model.models[_coronary].u_vol_scaling_factor = self.u_vol_cor_factor

        # scale the heart valves
        for _heart_valve in self.heart_valves:
            self.model.models[_heart_valve].r_scaling_factor = self.res_valve_factor

        # scale the pericardium
        for _pericardium in self.pericardium:
            self.model.models[
                _pericardium
            ].el_base_scaling_factor = self.el_base_pericardium_factor
            self.model.models[
                _pericardium
            ].u_vol_scaling_factor = self.u_vol_pericardium_factor

    def scale_circulatory_system(self):
        # scale the arteries
        for _artery in self.arteries:
            self.model.models[_artery].el_base_scaling_factor = self.el_base_art_factor
            self.model.models[_artery].u_vol_scaling_factor = self.u_vol_art_factor

        # scale the veins
        for _vein in self.veins:
            self.model.models[_vein].el_base_scaling_factor = self.el_base_ven_factor
            self.model.models[_vein].u_vol_scaling_factor = self.u_vol_ven_factor

        # scale the capillaries
        for _capillary in self.capillaries:
            self.model.models[
                _capillary
            ].el_base_scaling_factor = self.el_base_cap_factor
            self.model.models[_capillary].u_vol_scaling_factor = self.u_vol_cap_factor

        # scale the shunts
        for _shunt in self.shunts:
            self.model.models[_shunt].res_scaling_factor = self.res_shunt_factor

        # scale the blood connectors
        for _blood_connector in self.blood_connectors:
            self.model.models[
                _blood_connector
            ].r_scaling_factor = self.res_blood_connectors_factor

    def scale_respiratory_system(self):
        # scale the lungs
        for _lung in self.lungs:
            self.model.models[_lung].el_base_scaling_factor = self.el_base_lungs_factor
            self.model.models[_lung].u_vol_scaling_factor = self.u_vol_lungs_factor

        # scale the airways
        for _airway in self.airways:
            self.model.models[_airway].res_scaling_factor = self.res_airway_factor

        # scale the thorax
        for _thorax in self.thorax:
            self.model.models[
                _thorax
            ].el_base_scaling_factor = self.el_base_thorax_factor
            self.model.models[_thorax].u_vol_scaling_factor = self.u_vol_thorax_factor

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
