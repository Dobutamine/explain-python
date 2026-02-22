from base_models.time_varying_elastance import TimeVaryingElastance


class HeartChamber(TimeVaryingElastance):
    """Heart chamber model with ANS-modulated elastance and blood mixing."""

    model_type = "heart_chamber"

    def __init__(self, model_ref={}, name=None):
        """Initialize chamber mechanics and blood-related state."""
        super().__init__(model_ref=model_ref, name=name)

        self.fixed_composition = False

        self.temp = 37.0
        self.viscosity = 6.0
        self.solutes = {}
        self.drugs = {}
        self.ans_sens = 1.0
        self.ans_activity = 1.0

        self.to2 = 0.0
        self.tco2 = 0.0
        self.ph = -1.0
        self.pco2 = -1.0
        self.po2 = -1.0
        self.so2 = -1.0
        self.hco3 = -1.0
        self.be = -1.0
        self.el = 0.0

        self.elmin_calc = 0.0
        self.elmax_calc = 0.9

    def calc_elastance(self):
        """Compute ANS-adjusted elastance bounds and current chamber elastance."""
        self._el_min = (
            self.el_min
            + (self.el_min_factor - 1.0) * self.el_min
            + (self.el_min_factor_ps - 1.0) * self.el_min
            - (self.ans_activity - 1.0) * self.el_min * self.ans_sens
        )

        self._el_max = (
            self.el_max
            + (self.el_max_factor - 1.0) * self.el_max
            + (self.el_max_factor_ps - 1.0) * self.el_max
            + (self.ans_activity - 1.0) * self.el_max * self.ans_sens
        )

        self._el_k = (
            self.el_k
            + (self.el_k_factor - 1.0) * self.el_k
            + (self.el_k_factor_ps - 1.0) * self.el_k
        )

        if self._el_max < self._el_min:
            self._el_max = self._el_min

        self.el = self._el_min + (self._el_max - self._el_min) * self.act_factor

        self.el_min_factor = 1.0
        self.el_max_factor = 1.0
        self.el_k_factor = 1.0

    def volume_in(self, dvol, comp_from=None):
        """Add incoming volume and mix chemistry from source compartment."""
        super().volume_in(dvol)

        if comp_from is None or self.vol <= 0.0:
            return

        self.to2 += ((getattr(comp_from, "to2", 0.0) - self.to2) * dvol) / self.vol
        self.tco2 += ((getattr(comp_from, "tco2", 0.0) - self.tco2) * dvol) / self.vol

        comp_from_solutes = getattr(comp_from, "solutes", {}) or {}
        for solute_name in self.solutes:
            source_value = comp_from_solutes.get(solute_name, 0.0)
            self.solutes[solute_name] += ((source_value - self.solutes[solute_name]) * dvol) / self.vol

        self.temp += ((getattr(comp_from, "temp", self.temp) - self.temp) * dvol) / self.vol
        self.viscosity += ((getattr(comp_from, "viscosity", self.viscosity) - self.viscosity) * dvol) / self.vol

        comp_from_drugs = getattr(comp_from, "drugs", {}) or {}
        for drug_name in self.drugs:
            source_value = comp_from_drugs.get(drug_name, 0.0)
            self.drugs[drug_name] += ((source_value - self.drugs[drug_name]) * dvol) / self.vol
