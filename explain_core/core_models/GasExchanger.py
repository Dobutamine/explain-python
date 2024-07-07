import math

from explain_core.helpers.BloodComposition import set_blood_composition


class GasExchanger:
    # static properties
    model_type: str = "GasExchanger"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.dif_o2 = 0.01
        self.dif_o2_factor = 1.0
        self.dif_o2_scaling_factor = 1.0
        self.dif_co2 = 0.01
        self.dif_co2_factor = 1.0
        self.dif_co2_scaling_factor = 1.0
        self.comp_blood = ""
        self.comp_gas = ""

        # dependent properties
        self.flux_o2 = 0
        self.flux_co2 = 0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._blood = None
        self._gas = None

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the blood and gas capacitances
        if type(self.comp_blood) == str:
            self._blood = self._model_engine.models[self.comp_blood]
        else:
            self._blood = self.comp_blood

        if type(self.comp_gas) == str:
            self._gas = self._model_engine.models[self.comp_gas]
        else:
            self._gas = self.comp_gas

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # set the blood composition
        set_blood_composition(self._blood)

        # get the partial pressures and gas concentrations from the components
        po2_blood = self._blood.aboxy["po2"]
        pco2_blood = self._blood.aboxy["pco2"]
        to2_blood = self._blood.aboxy["to2"]
        tco2_blood = self._blood.aboxy["tco2"]

        co2_gas = self._gas.co2
        cco2_gas = self._gas.cco2
        po2_gas = self._gas.po2
        pco2_gas = self._gas.pco2

        # calculate the O2 flux from the blood to the gas compartment
        self.flux_o2 = (
            (po2_blood - po2_gas)
            * self.dif_o2
            * self.dif_o2_factor
            * self.dif_o2_scaling_factor
            * self._t
        )

        # calculate the new O2 concentrations of the gas and blood compartments
        new_to2_blood = (to2_blood * self._blood.vol - self.flux_o2) / self._blood.vol
        if new_to2_blood < 0:
            new_to2_blood = 0.0

        new_co2_gas = (co2_gas * self._gas.vol + self.flux_o2) / self._gas.vol
        if new_co2_gas < 0:
            new_co2_gas = 0.0

        # calculate the CO2 flux from the blood to the gas compartment
        self.flux_co2 = (
            (pco2_blood - pco2_gas)
            * self.dif_co2
            * self.dif_co2_factor
            * self.dif_co2_scaling_factor
            * self._t
        )

        # calculate the new CO2 concentrations of the gas and blood compartments
        new_tco2_blood = (
            tco2_blood * self._blood.vol - self.flux_co2
        ) / self._blood.vol
        if new_tco2_blood < 0:
            new_tco2_blood = 0.0

        new_cco2_gas = (cco2_gas * self._gas.vol + self.flux_co2) / self._gas.vol
        if new_cco2_gas < 0:
            new_cco2_gas = 0.0

        # transfer the new concentrations
        self._blood.aboxy["to2"] = new_to2_blood
        self._blood.aboxy["tco2"] = new_tco2_blood
        self._gas.co2 = new_co2_gas
        self._gas.cco2 = new_cco2_gas
