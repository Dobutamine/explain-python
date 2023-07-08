from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance


class GasExchanger(BaseModel):
    # independent variables
    dif_o2: float = 0.01
    dif_o2_factor: float = 1.0
    dif_co2: float = 0.01
    dif_co2_factor: float = 1.0

    # local variables
    _blood: Capacitance = {}
    _gas: Capacitance = {}
    _calc_acidbase = {}
    _calc_oxy = {}
    _flux_o2: float = 0
    _flux_co2: float = 0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the gas and blood capacitance
        self._blood = self._model.models[self.comp_blood]
        self._gas = self._model.models[self.comp_gas]
        self._calc_acidbase = self._model.models['Blood'].calc_acidbase_from_tco2
        self._calc_oxy = self._model.models['Blood'].calc_oxygenation_from_to2

    def calc_model(self) -> None:
        super().calc_model()

        # calculate the po2 and pco2 in the blood compartments
        self._calc_acidbase(self._blood)
        self._calc_oxy(self._blood)

        # get the partial pressures and gas concentrations from the components
        po2_blood: float = self._blood.oxy['po2']
        pco2_blood: float = self._blood.acidbase['pco2']
        to2_blood: float = self._blood.solutes['to2']
        tco2_blood: float = self._blood.solutes['tco2']

        co2_gas: float = self._gas.c_o2
        cco2_gas: float = self._gas.c_co2
        po2_gas: float = self._gas.p_o2
        pco2_gas: float = self._gas.p_co2

        # calculate the O2 flux from the blood to the gas compartment
        self._flux_o2 = (po2_blood - po2_gas) * self.dif_o2 * \
            self.dif_o2_factor * self._t

        # calculate the new O2 concentrations of the gas and blood compartments
        new_to2_blood: float = (
            to2_blood * self._blood.vol - self._flux_o2) / self._blood.vol
        if new_to2_blood < 0:
            new_to2_blood = 0

        new_co2_gas = (co2_gas * self._gas.vol + self._flux_o2) / self._gas.vol
        if new_co2_gas < 0:
            new_co2_gas = 0

        # calculate the CO2 flux from the blood to the gas compartment
        self._flux_co2 = (pco2_blood - pco2_gas) * \
            self.dif_co2 * self.dif_co2_factor * self._t

        # calculate the new CO2 concentrations of the gas and blood compartments
        new_tco2_blood: float = (
            tco2_blood * self._blood.vol - self._flux_co2) / self._blood.vol
        if new_tco2_blood < 0:
            new_tco2_blood = 0

        new_cco2_gas = (cco2_gas * self._gas.vol +
                        self._flux_co2) / self._gas.vol
        if new_cco2_gas < 0:
            new_cco2_gas = 0

        # transfer the new concentrations
        self._blood.solutes['to2'] = new_to2_blood
        self._blood.solutes['tco2'] = new_tco2_blood
        self._gas.c_o2 = new_co2_gas
        self._gas.c_co2 = new_cco2_gas
