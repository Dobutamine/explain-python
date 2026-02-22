from base_models.base_model import BaseModel
from composite_models.blood_vessel import BloodVessel


class MicroVascularUnit(BaseModel):
    model_type = "micro_vascular_unit"

    def __init__(self, model_ref={}, name=None):
        super().__init__(model_ref=model_ref, name=name)

        self.inputs = []
        self.vol = 0.0055
        self.u_vol = 0.005
        self.el_base = 25000.0
        self.el_k = 0.0
        self.r_for = 25000.0
        self.r_back = 25000.0
        self.r_k = 0.0
        self.l = 0.0
        self.no_flow = False
        self.no_back_flow = False
        self.ans_activity = 1.0
        self.ans_sens = 0.0
        self.ans_sens_settings = {"art": 1.0, "cap": 0.0, "ven": 0.75}
        self.alpha_settings = {"art": 0.63, "cap": 0.0, "ven": 0.75}
        self.el_dist = {"art": 0.10, "cap": 0.15, "ven": 0.75}
        self.vol_dist = {"art": 0.10, "cap": 0.55, "ven": 0.35}
        self.res_dist = {"art": 0.75, "cap": 0.15, "ven": 0.10}

        self.temp = 37.0
        self.viscosity = 6.0
        self.solutes = {}
        self.drugs = {}
        self.to2 = 0.0
        self.tco2 = 0.0
        self.ph = -1.0
        self.pco2 = -1.0
        self.po2 = -1.0
        self.so2 = -1.0
        self.hco3 = -1.0
        self.be = -1.0

        self.r_factor = 1.0
        self.r_k_factor = 1.0
        self.l_factor = 1.0

        self.u_vol_factor = 1.0
        self.el_base_factor = 1.0
        self.el_k_factor = 1.0

        self.r_factor_ps = 1.0
        self.r_k_factor_ps = 1.0
        self.l_factor_ps = 1.0

        self.u_vol_factor_ps = 1.0
        self.el_base_factor_ps = 1.0
        self.el_k_factor_ps = 1.0

        self.flow = 0.0
        self.flow_in = 0.0
        self.flow_out = 0.0
        self.pres = 0.0
        self.pres_in = 0.0
        self.pres_out = 0.0

        self._el = 0.0
        self._el_art = 0.0
        self._el_cap = 0.0
        self._el_ven = 0.0

        self._r_for = 1000.0
        self._r_back = 1000.0
        self._r_k = 0.0

        self._r_for_art = 0.0
        self._r_back_art = 0.0
        self._r_for_cap = 0.0
        self._r_back_cap = 0.0
        self._r_for_ven = 0.0
        self._r_back_ven = 0.0

        self._l = 0.0

        self._u_vol = 0.0
        self._u_vol_art = 0.0
        self._u_vol_cap = 0.0
        self._u_vol_ven = 0.0

        self._el_k = 0.0
        self._el_k_art = 0.0
        self._el_k_cap = 0.0
        self._el_k_ven = 0.0

        self._art = None
        self._cap = None
        self._ven = None

    def init_model(self, args=None):
        super().init_model(args)

        self.calc_elastance_dist(self.el_base, self.el_dist)

        model_registry = self.model_ref if isinstance(self.model_ref, dict) else {}
        if not model_registry and getattr(self, "_model_engine", None) is not None:
            model_registry = getattr(self._model_engine, "models", {})

        vessel_model_ref = self._model_engine if getattr(self, "_model_engine", None) is not None else model_registry

        art_name = f"{self.name}_ART"
        cap_name = f"{self.name}_CAP"
        ven_name = f"{self.name}_VEN"

        self._art = self._get_or_create_vessel(model_registry, vessel_model_ref, art_name)
        self._art.init_model(
            {
                "name": art_name,
                "description": f"arteriole of {self.name}",
                "is_enabled": self.is_enabled,
                "vol": self.vol * self.vol_dist["art"],
                "u_vol": self.u_vol * self.vol_dist["art"],
                "el_base": self._el_art,
                "el_k": self.el_k * self.el_dist["art"],
                "inputs": list(self.inputs),
                "r_for": self.r_for * self.res_dist["art"],
                "r_back": self.r_back * self.res_dist["art"],
                "r_k": self.r_k * self.res_dist["art"],
                "no_flow": self.no_flow,
                "no_back_flow": self.no_back_flow,
                "ans_activity": self.ans_activity,
                "ans_sens": self.ans_sens_settings["art"],
                "alpha": self.alpha_settings["art"],
            }
        )

        self._cap = self._get_or_create_vessel(model_registry, vessel_model_ref, cap_name)
        self._cap.init_model(
            {
                "name": cap_name,
                "description": f"capillaries of {self.name}",
                "is_enabled": self.is_enabled,
                "vol": self.vol * self.vol_dist["cap"],
                "u_vol": self.u_vol * self.vol_dist["cap"],
                "el_base": self._el_cap,
                "el_k": self.el_k * self.el_dist["cap"],
                "inputs": [art_name],
                "r_for": self.r_for * self.res_dist["cap"],
                "r_back": self.r_back * self.res_dist["cap"],
                "r_k": self.r_k * self.res_dist["cap"],
                "no_flow": self.no_flow,
                "no_back_flow": self.no_back_flow,
                "ans_activity": self.ans_activity,
                "ans_sens": self.ans_sens_settings["cap"],
                "alpha": self.alpha_settings["cap"],
            }
        )

        self._ven = self._get_or_create_vessel(model_registry, vessel_model_ref, ven_name)
        self._ven.init_model(
            {
                "name": ven_name,
                "description": f"venules of {self.name}",
                "is_enabled": self.is_enabled,
                "vol": self.vol * self.vol_dist["ven"],
                "u_vol": self.u_vol * self.vol_dist["ven"],
                "el_base": self._el_ven,
                "el_k": self.el_k * self.el_dist["ven"],
                "inputs": [cap_name],
                "r_for": self.r_for * self.res_dist["ven"],
                "r_back": self.r_back * self.res_dist["ven"],
                "r_k": self.r_k * self.res_dist["ven"],
                "no_flow": self.no_flow,
                "no_back_flow": self.no_back_flow,
                "ans_activity": self.ans_activity,
                "ans_sens": self.ans_sens_settings["ven"],
                "alpha": self.alpha_settings["ven"],
            }
        )

    def _get_or_create_vessel(self, model_registry, model_ref_for_vessel, vessel_name):
        if vessel_name in model_registry:
            vessel = model_registry[vessel_name]
            if isinstance(vessel, BloodVessel):
                return vessel

        vessel = BloodVessel(model_ref=model_ref_for_vessel, name=vessel_name)
        model_registry[vessel_name] = vessel
        return vessel

    def calc_model(self):
        if self._art is None or self._cap is None or self._ven is None:
            return

        ans_activity = 1.0 + (self.ans_activity - 1.0) * self.ans_sens

        self._art.ans_activity = ans_activity
        self._cap.ans_activity = ans_activity
        self._ven.ans_activity = ans_activity

        self.calc_resistance()
        self.calc_elastance()
        self.calc_inertance()
        self.calc_volume()

        self._art.el_base = self._el_art
        self._cap.el_base = self._el_cap
        self._ven.el_base = self._el_ven

        self._art.el_k = self._el_k_art
        self._cap.el_k = self._el_k_cap
        self._ven.el_k = self._el_k_ven

        self._art.r_for = self._r_for_art
        self._art.r_back = self._r_back_art
        self._art.r_k = self._r_k

        self._cap.r_for = self._r_for_cap
        self._cap.r_back = self._r_back_cap
        self._cap.r_k = self._r_k

        self._ven.r_for = self._r_for_ven
        self._ven.r_back = self._r_back_ven
        self._ven.r_k = self._r_k

        self._art.u_vol = self._u_vol_art
        self._art.l = self._l
        self._art.no_flow = self.no_flow
        self._art.no_back_flow = self.no_back_flow

        self._cap.u_vol = self._u_vol_cap
        self._cap.l = self._l
        self._cap.no_flow = self.no_flow
        self._cap.no_back_flow = self.no_back_flow

        self._ven.u_vol = self._u_vol_ven
        self._ven.l = self._l
        self._ven.no_flow = self.no_flow
        self._ven.no_back_flow = self.no_back_flow

        self.pres = self._cap.pres
        self.pres_in = self._art.pres
        self.pres_out = self._cap.pres

        self.flow = self._cap.flow
        self.flow_in = self._art.flow
        self.flow_out = self._ven.flow

        self.vol = self._art.vol + self._cap.vol + self._ven.vol

        self.solutes = self._cap.solutes
        self.drugs = self._cap.drugs
        self.to2 = self._cap.to2
        self.tco2 = self._cap.tco2
        self.ph = self._cap.ph
        self.pco2 = self._cap.pco2
        self.po2 = self._cap.po2
        self.so2 = self._cap.so2
        self.hco3 = self._cap.hco3
        self.be = self._cap.be
        self.temp = self._cap.temp
        self.viscosity = self._cap.viscosity

    def calc_resistance(self):
        self._r_for = (
            self.r_for
            + (self.r_factor - 1.0) * self.r_for
            + (self.r_factor_ps - 1.0) * self.r_for
        )

        self._r_back = (
            self.r_back
            + (self.r_factor - 1.0) * self.r_back
            + (self.r_factor_ps - 1.0) * self.r_back
        )

        self._r_k = (
            self.r_k
            + (self.r_k_factor - 1.0) * self.r_k
            + (self.r_k_factor_ps - 1.0) * self.r_k
        )

        self._r_for_art = self._r_for * self.res_dist["art"]
        self._r_back_art = self._r_back * self.res_dist["art"]

        self._r_for_cap = self._r_for * self.res_dist["cap"]
        self._r_back_cap = self._r_back * self.res_dist["cap"]

        self._r_for_ven = self._r_for * self.res_dist["ven"]
        self._r_back_ven = self._r_back * self.res_dist["ven"]

        self.r_factor = 1.0
        self.r_k_factor = 1.0

    def calc_elastance(self):
        self._el = (
            self.el_base
            + (self.el_base_factor - 1.0) * self.el_base
            + (self.el_base_factor_ps - 1.0) * self.el_base
        )

        self.calc_elastance_dist(self._el, self.el_dist)

        self._el_k = (
            self.el_k
            + (self.el_k_factor - 1.0) * self.el_k
            + (self.el_k_factor_ps - 1.0) * self.el_k
        )

        self._el_k_art = self._el_k * self.el_dist["art"]
        self._el_k_cap = self._el_k * self.el_dist["cap"]
        self._el_k_ven = self._el_k * self.el_dist["ven"]

        self.el_base_factor = 1.0
        self.el_k_factor = 1.0

    def calc_elastance_dist(self, el_base, el_dist):
        if el_base <= 0.0:
            self._el_art = 0.0
            self._el_cap = 0.0
            self._el_ven = 0.0
            return

        unit = 1.0 / (3.0 * el_base) / 33.3333

        art_dist = max(el_dist["art"], 1e-12)
        cap_dist = max(el_dist["cap"], 1e-12)
        ven_dist = max(el_dist["ven"], 1e-12)

        self._el_art = 1.0 / (art_dist * 100.0 * unit)
        self._el_cap = 1.0 / (cap_dist * 100.0 * unit)
        self._el_ven = 1.0 / (ven_dist * 100.0 * unit)

    def calc_inertance(self):
        self._l = self.l + (self.l_factor - 1.0) * self.l + (self.l_factor_ps - 1.0) * self.l
        self.l_factor = 1.0

    def calc_volume(self):
        self._u_vol = (
            self.u_vol
            + (self.u_vol_factor - 1.0) * self.u_vol
            + (self.u_vol_factor_ps - 1.0) * self.u_vol
        )

        self._u_vol_art = self._u_vol * self.vol_dist["art"]
        self._u_vol_cap = self._u_vol * self.vol_dist["cap"]
        self._u_vol_ven = self._u_vol * self.vol_dist["ven"]

        self.u_vol_factor = 1.0
