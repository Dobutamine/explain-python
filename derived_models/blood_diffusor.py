from base_models.base_model import BaseModel
from functions.blood_composition import calc_blood_composition


class BloodDiffusor(BaseModel):
    model_type = "blood_diffusor"

    def __init__(self, model_ref={}, name=None):
        super().__init__(model_ref=model_ref, name=name)

        self.comp_blood1 = ""
        self.comp_blood2 = ""
        self.dif_o2 = 0.01
        self.dif_co2 = 0.01
        self.dif_solutes = {}

        self.dif_o2_factor = 1.0
        self.dif_co2_factor = 1.0
        self.dif_solutes_factor = 1.0

        self.dif_o2_factor_ps = 1.0
        self.dif_co2_factor_ps = 1.0
        self.dif_solutes_factor_ps = 1.0

        self._comp_blood1 = None
        self._comp_blood2 = None

    def _resolve_component(self, component_name):
        if not component_name:
            return None

        if isinstance(self.model_ref, dict) and component_name in self.model_ref:
            return self.model_ref[component_name]

        model_engine = getattr(self, "_model_engine", None)
        if model_engine is not None:
            models = getattr(model_engine, "models", None)
            if isinstance(models, dict):
                return models.get(component_name)

        return None

    def calc_model(self):
        self._comp_blood1 = self._resolve_component(self.comp_blood1)
        self._comp_blood2 = self._resolve_component(self.comp_blood2)

        if self._comp_blood1 is None or self._comp_blood2 is None:
            return

        calc_blood_composition(self._comp_blood1)
        calc_blood_composition(self._comp_blood2)

        dif_o2 = self.dif_o2 + (self.dif_o2_factor - 1.0) * self.dif_o2 + (self.dif_o2_factor_ps - 1.0) * self.dif_o2
        dif_co2 = self.dif_co2 + (self.dif_co2_factor - 1.0) * self.dif_co2 + (self.dif_co2_factor_ps - 1.0) * self.dif_co2
        dif_solutes_factor = self.dif_solutes_factor + (self.dif_solutes_factor - 1.0) * self.dif_solutes_factor + (self.dif_solutes_factor_ps - 1.0) * self.dif_solutes_factor

        time_step = getattr(self, "_t", 0.0)
        if time_step <= 0.0:
            self.dif_o2_factor = 1.0
            self.dif_co2_factor = 1.0
            self.dif_solutes_factor = 1.0
            return

        if getattr(self._comp_blood1, "vol", 0.0) <= 0.0 or getattr(self._comp_blood2, "vol", 0.0) <= 0.0:
            self.dif_o2_factor = 1.0
            self.dif_co2_factor = 1.0
            self.dif_solutes_factor = 1.0
            return

        do2 = (self._comp_blood1.to2 - self._comp_blood2.to2) * dif_o2 * time_step
        if not getattr(self._comp_blood1, "fixed_composition", False):
            self._comp_blood1.to2 = (self._comp_blood1.to2 * self._comp_blood1.vol - do2) / self._comp_blood1.vol
        if not getattr(self._comp_blood2, "fixed_composition", False):
            self._comp_blood2.to2 = (self._comp_blood2.to2 * self._comp_blood2.vol + do2) / self._comp_blood2.vol

        dco2 = (self._comp_blood1.tco2 - self._comp_blood2.tco2) * dif_co2 * time_step
        if not getattr(self._comp_blood1, "fixed_composition", False):
            self._comp_blood1.tco2 = (self._comp_blood1.tco2 * self._comp_blood1.vol - dco2) / self._comp_blood1.vol
        if not getattr(self._comp_blood2, "fixed_composition", False):
            self._comp_blood2.tco2 = (self._comp_blood2.tco2 * self._comp_blood2.vol + dco2) / self._comp_blood2.vol

        solutes_1 = getattr(self._comp_blood1, "solutes", {})
        solutes_2 = getattr(self._comp_blood2, "solutes", {})

        for solute_name, base_diff in self.dif_solutes.items():
            if solute_name not in solutes_1 or solute_name not in solutes_2:
                continue

            dif = base_diff * dif_solutes_factor
            dsol = (solutes_1[solute_name] - solutes_2[solute_name]) * dif * time_step

            if not getattr(self._comp_blood1, "fixed_composition", False):
                solutes_1[solute_name] = (solutes_1[solute_name] * self._comp_blood1.vol - dsol) / self._comp_blood1.vol
            if not getattr(self._comp_blood2, "fixed_composition", False):
                solutes_2[solute_name] = (solutes_2[solute_name] * self._comp_blood2.vol + dsol) / self._comp_blood2.vol

        self.dif_o2_factor = 1.0
        self.dif_co2_factor = 1.0
        self.dif_solutes_factor = 1.0
