from base_models.base_model import BaseModel
from functions.gas_composition import calc_gas_composition

class GasDiffusor(BaseModel):
    """Diffusive exchange model between two gas-containing compartments."""

    model_type = "gas_diffusor"

    def __init__(self, model_ref = {}, name=None):
        """Initialize gas diffusion settings and component references."""
        # initialize the base model properties
        super().__init__(model_ref=model_ref, name=name)

        # initialize independent properties
        self.comp_gas1 = ""  # name of the first gas-containing model
        self.comp_gas2 = ""  # name of the second gas-containing model
        self.dif_o2 = 0.01  # diffusion constant for o2 (mmol/mmHg * s)
        self.dif_co2 = 0.01  # diffusion constant for co2 (mmol/mmHg * s)
        self.dif_n2 = 0.01  # diffusion constant for n2 (mmol/mmHg * s)
        self.dif_other = 0.01  # diffusion constant for other gasses (mmol/mmHg * s)

        # non-persistent property factors. These factors reset to 1.0 after each model step
        self.dif_o2_factor = 1.0  # non-persistent diffusion factor for o2 (unitless)
        self.dif_co2_factor = 1.0  # non-persistent diffusion factor for co2 (unitless)
        self.dif_n2_factor = 1.0  # non-persistent diffusion factor for n2 (unitless)
        self.dif_other_factor = 1.0  # non-persistent diffusion factor for other gasses (unitless)

        # persistent property factors. These factors are persistent and do not reset
        self.dif_o2_factor_ps = 1.0  # persistent diffusion factor for o2 (unitless)
        self.dif_co2_factor_ps = 1.0  # persistent diffusion factor for co2 (unitless)
        self.dif_n2_factor_ps = 1.0  # persistent diffusion factor for n2 (unitless)
        self.dif_other_factor_ps = 1.0  # persistent diffusion factor for other gasses (unitless)

        # local variables
        self._comp_gas1 = None  # reference to the first gas-containing model
        self._comp_gas2 = None  # reference to the second gas-containing model

    def _resolve_component(self, component_name):
        """Resolve a component name from local registry or attached model engine."""
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
        """Run one diffusion step for configured gas species."""
        # find the two gas-containing models and store references
        self._comp_gas1 = self._resolve_component(self.comp_gas1)
        self._comp_gas2 = self._resolve_component(self.comp_gas2)

        if self._comp_gas1 is None or self._comp_gas2 is None:
            return

        # calculate the gas composition of the gas components in this diffusor as we need the partial pressures for the gas diffusion
        calc_gas_composition(self._comp_gas1)
        calc_gas_composition(self._comp_gas2)

        # incorporate the factors
        _dif_o2 = self.dif_o2 + (self.dif_o2_factor - 1.0) * self.dif_o2 + (self.dif_o2_factor_ps - 1.0) * self.dif_o2
        _dif_co2 = self.dif_co2 + (self.dif_co2_factor - 1.0) * self.dif_co2 + (self.dif_co2_factor_ps - 1.0) * self.dif_co2
        _dif_n2 = self.dif_n2 + (self.dif_n2_factor - 1.0) * self.dif_n2 + (self.dif_n2_factor_ps - 1.0) * self.dif_n2
        _dif_other = self.dif_other + (self.dif_other_factor - 1.0) * self.dif_other + (self.dif_other_factor_ps - 1.0) * self.dif_other

        time_step = getattr(self, "_t", 0.0)
        if time_step <= 0.0:
            self.dif_o2_factor = 1.0
            self.dif_co2_factor = 1.0
            self.dif_n2_factor = 1.0
            self.dif_other_factor = 1.0
            return

        if getattr(self._comp_gas1, "vol", 0.0) <= 0.0 or getattr(self._comp_gas2, "vol", 0.0) <= 0.0:
            self.dif_o2_factor = 1.0
            self.dif_co2_factor = 1.0
            self.dif_n2_factor = 1.0
            self.dif_other_factor = 1.0
            return

        # diffuse the gases, where diffusion is partial pressure-driven
        do2 = (self._comp_gas1.po2 - self._comp_gas2.po2) * _dif_o2 * time_step

        # update the concentrations
        self._comp_gas1.co2 = (self._comp_gas1.co2 * self._comp_gas1.vol - do2) / self._comp_gas1.vol
        self._comp_gas2.co2 = (self._comp_gas2.co2 * self._comp_gas2.vol + do2) / self._comp_gas2.vol

        dco2 = (self._comp_gas1.pco2 - self._comp_gas2.pco2) * _dif_co2 * time_step
        # update the concentrations
        self._comp_gas1.cco2 = (self._comp_gas1.cco2 * self._comp_gas1.vol - dco2) / self._comp_gas1.vol
        self._comp_gas2.cco2 = (self._comp_gas2.cco2 * self._comp_gas2.vol + dco2) / self._comp_gas2.vol

        dn2 = (self._comp_gas1.pn2 - self._comp_gas2.pn2) * _dif_n2 * time_step
        # update the concentrations
        self._comp_gas1.cn2 = (self._comp_gas1.cn2 * self._comp_gas1.vol - dn2) / self._comp_gas1.vol
        self._comp_gas2.cn2 = (self._comp_gas2.cn2 * self._comp_gas2.vol + dn2) / self._comp_gas2.vol

        dother = (self._comp_gas1.pother - self._comp_gas2.pother) * _dif_other * time_step
        # update the concentrations
        self._comp_gas1.cother = (self._comp_gas1.cother * self._comp_gas1.vol - dother) / self._comp_gas1.vol
        self._comp_gas2.cother = (self._comp_gas2.cother * self._comp_gas2.vol + dother) / self._comp_gas2.vol

        # reset the non-persistent factors
        self.dif_o2_factor = 1.0
        self.dif_co2_factor = 1.0
        self.dif_n2_factor = 1.0
        self.dif_other_factor = 1.0
