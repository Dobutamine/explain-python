from base_models.base_model import BaseModel
from functions.blood_composition import calc_blood_composition

class GasExchanger(BaseModel):
    """Bidirectional gas exchange model between blood and gas compartments."""

    model_type = "gas_exchanger"

    def __init__(self, model_ref = {}, name=None):
        """Initialize exchanger connectivity, diffusion constants, and flux state."""
        # initialize the base model properties
        super().__init__(model_ref=model_ref, name=name)

        # initialize independent properties
        self.comp_blood = ""  # name of the blood component
        self.comp_gas = ""  # name of the gas component
        self.dif_o2 = 0.0  # diffusion constant for oxygen (mmol/mmHg * s)
        self.dif_co2 = 0.0  # diffusion constant for carbon dioxide (mmol/mmHg * s)

        # non-persistent factors
        self.dif_o2_factor = 1.0  # factor modifying the oxygen diffusion constant
        self.dif_co2_factor = 1.0  # factor modifying the carbon diffusion constant

        # persistent factors
        self.dif_o2_factor_ps = 1.0  # factor modifying the oxygen diffusion constant
        self.dif_co2_factor_ps = 1.0  # factor modifying the carbon diffusion constant

        # dependent properties
        self.flux_o2 = 0.0  # oxygen flux (mmol)
        self.flux_co2 = 0.0  # carbon dioxide flux (mmol)

        # local variables
        self._blood = None  # reference to the blood component
        self._gas = None  # reference to the gas component

    def calc_model(self):
        """Run one exchange step and update blood/gas concentrations."""
        # find the blood and gas components
        self._blood = self._model_engine.models[self.comp_blood]
        self._gas = self._model_engine.models[self.comp_gas]

        # set the blood composition of the blood component
        calc_blood_composition(self._blood)

        # get the partial pressures and gas concentrations from the components
        po2_blood = self._blood.po2
        pco2_blood = self._blood.pco2
        to2_blood = self._blood.to2
        tco2_blood = self._blood.tco2

        co2_gas = self._gas.co2
        cco2_gas = self._gas.cco2
        po2_gas = self._gas.po2
        pco2_gas = self._gas.pco2

        if self._blood.vol == 0.0:
            return

        # incorporate the factors
        _dif_o2 = self.dif_o2 
        + (self.dif_o2_factor - 1) * self.dif_o2
        + (self.dif_o2_factor_ps - 1) * self.dif_o2

        _dif_co2 = self.dif_co2 
        + (self.dif_co2_factor - 1) * self.dif_co2
        + (self.dif_co2_factor_ps - 1) * self.dif_co2


        # calculate the O2 flux from the blood to the gas compartment
        self.flux_o2 = (po2_blood - po2_gas) * _dif_o2 * self._t

        # calculate the new O2 concentrations of the gas and blood compartments
        new_to2_blood = (to2_blood * self._blood.vol - self.flux_o2) / self._blood.vol
        if new_to2_blood < 0:
            new_to2_blood = 0.0

        new_co2_gas = (co2_gas * self._gas.vol + self.flux_o2) / self._gas.vol
        if new_co2_gas < 0:
            new_co2_gas = 0.0

        # calculate the CO2 flux from the blood to the gas compartment
        self.flux_co2 = (pco2_blood - pco2_gas) * _dif_co2 * self._t

        # calculate the new CO2 concentrations of the gas and blood compartments
        new_tco2_blood = (tco2_blood * self._blood.vol - self.flux_co2) / self._blood.vol
        if new_tco2_blood < 0:
            new_tco2_blood = 0.0

        new_cco2_gas = (cco2_gas * self._gas.vol + self.flux_co2) / self._gas.vol
        if new_cco2_gas < 0:
            new_cco2_gas = 0.0

        # transfer the new concentrations
        self._blood.to2 = new_to2_blood
        self._blood.tco2 = new_tco2_blood
        self._gas.co2 = new_co2_gas
        self._gas.cco2 = new_cco2_gas

        # reset the non-persistent factors
        self.dif_o2_factor = 1.0
        self.dif_co2_factor = 1.0