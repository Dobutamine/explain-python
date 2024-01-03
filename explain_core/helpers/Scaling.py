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
    syst_ref: float = 50.0
    diast_ref: float = 23.0
    map_ref: float = 50.0
    resp_rate: float = 0.0
    vt_rr_ratio: float = 0.0001212
    mv_ref: float = 0.0

    heart = ["LA", "RA", "LV", "RV", "COR"]
    heart_valves = ["LA_LV", "RA_RV", "LV_AA", "RV_PA", "LV_PA", "RV_AA"]
    pericardium = ["PC"]
    arteries = ["AA", "AAR", "AD", "PA", "DA"]
    veins = ["IVCE", "IVCI", "SVC", "PV"]
    capillaries = ["LS", "INT", "KID", "RLB", "BR", "RUB", "LL", "RL"]
    shunts = ["IPS", "FO"]
    blood_connectors = [
        "AA_AAR",
        "AA_COR",
        "AAR_AD",
        "AD_INT",
        "AD_KID",
        "AD_LS",
        "AD_RLB",
        "AAR_RUB",
        "AAR_BR",
        "COR_RA",
        "RUB_SVC",
        "BR_SVC",
        "RLB_IVCE",
        "LS_IVCE",
        "KID_IVCE",
        "INT_IVCE",
        "IVCE_IVCI",
        "IVCI_RA",
        "SVC_RA",
        "PA_LL",
        "PA_RL",
        "LL_PV",
        "RL_PV",
        "PV_LA",
    ]
    lungs = ["ALL", "ALR", "DS"]
    airways = ["MOUTH_DS", "DS_ALL", "DS_ALR"]
    thorax = ["THORAX", "CHEST_L", "CHEST_R"]

    scaling_dict: dict = {
        "22": {
            "weight": 0.496,
            "height": 0.281,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 48.0,
            "diast": 22.0,
            "hr_ref": 140.0,
            "map": 30.6,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "23": {
            "weight": 0.571,
            "height": 0.295,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 50.0,
            "diast": 23.0,
            "hr_ref": 140.0,
            "map": 32.0,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "24": {
            "weight": 0.651,
            "height": 0.309,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 51.21,
            "diast": 23.07,
            "hr_ref": 160.0,
            "map": 34.22,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "25": {
            "weight": 0.741,
            "height": 0.323,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 51.61,
            "diast": 23.36,
            "hr_ref": 140.0,
            "map": 34.79,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "26": {
            "weight": 0.841,
            "height": 0.337,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 52.12,
            "diast": 24.3,
            "hr_ref": 140.0,
            "map": 35.71,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "27": {
            "weight": 0.953,
            "height": 0.351,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 52.69,
            "diast": 26.23,
            "hr_ref": 140.0,
            "map": 37.01,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "28": {
            "weight": 1.079,
            "height": 0.364,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 53.53,
            "diast": 28.48,
            "hr_ref": 140.0,
            "map": 38.52,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "29": {
            "weight": 1.223,
            "height": 0.378,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 54.89,
            "diast": 30.1,
            "hr_ref": 140.0,
            "map": 40.03,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "30": {
            "weight": 1.388,
            "height": 0.392,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 56.43,
            "diast": 30.93,
            "hr_ref": 140.0,
            "map": 41.28,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "31": {
            "weight": 1.578,
            "height": 0.406,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 57.48,
            "diast": 31.3,
            "hr_ref": 140.0,
            "map": 42.04,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "32": {
            "weight": 1.790,
            "height": 0.42,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 57.9,
            "diast": 31.51,
            "hr_ref": 140.0,
            "map": 42.37,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "33": {
            "weight": 2.018,
            "height": 0.434,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 58.2,
            "diast": 31.84,
            "hr_ref": 140.0,
            "map": 42.68,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "34": {
            "weight": 2.255,
            "height": 0.447,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 58.88,
            "diast": 32.54,
            "hr_ref": 140.0,
            "map": 43.35,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "35": {
            "weight": 2.493,
            "height": 0.46,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 60.28,
            "diast": 33.71,
            "hr_ref": 140.0,
            "map": 44.67,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "36": {
            "weight": 2.726,
            "height": 0.472,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 62.51,
            "diast": 35.37,
            "hr_ref": 140.0,
            "map": 46.73,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "37": {
            "weight": 2.947,
            "height": 0.483,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 64.73,
            "diast": 37.16,
            "hr_ref": 140.0,
            "map": 48.79,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "38": {
            "weight": 3.156,
            "height": 0.493,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 65.96,
            "diast": 38.62,
            "hr_ref": 140.0,
            "map": 50.03,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "39": {
            "weight": 3.360,
            "height": 0.502,
            "blood_volume": 0.08,
            "lung_volume": 0.03,
            "res_circ_factor": 1.0,
            "el_base_circ_factor": 1.0,
            "el_min_circ_factor": 1.0,
            "el_max_circ_factor": 1.0,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 66.32,
            "diast": 39.63,
            "hr_ref": 140.0,
            "map": 50.62,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "40": {
            "weight": 3.568,
            "height": 0.512,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 66.44,
            "diast": 40.22,
            "hr_ref": 140.0,
            "map": 51.26,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "41": {
            "weight": 3.785,
            "height": 0.521,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 66.78,
            "diast": 40.51,
            "hr_ref": 140.0,
            "map": 52.29,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
        "42": {
            "weight": 4.014,
            "height": 0.529,
            "blood_volume": 0.1,
            "lung_volume": 0.03,
            "res_circ_factor": 0.6,
            "el_base_circ_factor": 0.8,
            "el_min_circ_factor": 0.6,
            "el_max_circ_factor": 0.8,
            "res_resp_factor": 1.0,
            "el_base_resp_factor": 1.0,
            "syst": 67.12,
            "diast": 40.8,
            "hr_ref": 140.0,
            "map": 53.32,
            "resp_rate": 40.0,
            "vt_rr_ratio": 0.0001212,
            "minute_volume_ref": 0.2,
        },
    }

    def __init__(self, model):
        # get a reference to the model engine
        self.model = model

    def scale_to_weight(self, weight: float):
        pass

    def scale_to_gestational_age(self, gestation_age: float):
        # get the scaling properties for the gestational age
        ga_props = self.scaling_dict[str(math.floor(gestation_age))]

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
            hr_ref=ga_props["hr_ref"],
            syst_ref=ga_props["syst"],
            diast_ref=ga_props["diast"],
            map_ref=ga_props["map"],
            resp_rate=ga_props["resp_rate"],
            vt_rr_ratio=ga_props["vt_rr_ratio"],
            mv_ref=ga_props["minute_volume_ref"],
        )

        print(f"Scaling to gestational age {gestation_age} weeks")
        print(f"Weight (Fenton p50) = {self.model.weight} kg")
        print(f"Height (Fenton p50) = {self.model.height} m")
        self.get_total_blood_volume()
        self.get_total_lung_volume()
        print(f"Systole target = {ga_props['syst']} mmHg")
        print(f"Diastole target = {ga_props['diast']} mmHg")
        print(f"Mean arterial pressure target = {ga_props['map']} mmHg")
        print(f"Respiratory rate target = {ga_props['resp_rate']} bpm")
        print(
            f"Vt/RR ratio target = {ga_props['vt_rr_ratio'] * self.model.weight} L/bpm/kg"
        )
        print(
            f"Minute volume target = {ga_props['minute_volume_ref'] * self.model.weight} L/min"
        )

    def set_scale_factors(self, output=False):
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
        hr_ref: float,
        syst_ref: float,
        diast_ref: float,
        map_ref: float,
        resp_rate: float,
        vt_rr_ratio: float,
        mv_ref: float,
    ):
        self.res_factor_circ_correction = res_circ_factor
        self.el_base_factor_circ_correction = el_base_circ_factor
        self.el_min_factor_correction = el_min_circ_factor
        self.el_max_factor_correction = el_max_circ_factor
        self.res_factor_resp_correction = res_resp_factor
        self.el_base_factor_resp_correction = el_base_resp_factor

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
        self.set_scale_factors()

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
        for _heart_chamber in self.heart:
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
