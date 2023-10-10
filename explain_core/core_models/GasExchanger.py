from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance
from explain_core.functions.BloodComposition import set_blood_composition


class GasExchanger(BaseModel):
    # independent variables
    dif_o2: float = 0.01
    dif_o2_factor: float = 1.0
    dif_co2: float = 0.01
    dif_co2_factor: float = 1.0

    # local variables
    _blood: Capacitance = {}
    _gas: Capacitance = {}
    _flux_o2: float = 0
    _flux_co2: float = 0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the gas and blood capacitance
        if type(self.comp_blood) is str:
            self._blood = self._model.models[self.comp_blood]
        else:
            self._blood = self.comp_blood

        if type(self.comp_gas) is str:
            self._gas = self._model.models[self.comp_gas]
        else:
            self._gas = self.comp_gas

    def calc_model(self) -> None:
        super().calc_model()

        # set the blood composition
        set_blood_composition(self._blood)

        # get the partial pressures and gas concentrations from the components
        po2_blood: float = self._blood.aboxy['po2']
        pco2_blood: float = self._blood.aboxy['pco2']
        to2_blood: float = self._blood.aboxy['to2']
        tco2_blood: float = self._blood.aboxy['tco2']

        co2_gas: float = self._gas.co2
        cco2_gas: float = self._gas.cco2
        po2_gas: float = self._gas.po2
        pco2_gas: float = self._gas.pco2

        # calculate the O2 flux from the blood to the gas compartment
        self._flux_o2 = (po2_blood - po2_gas) * self.dif_o2 * \
            self.dif_o2_factor * self._t

        # calculate the new O2 concentrations of the gas and blood compartments
        _blood_vol = self._blood.vol + self._blood.u_vol
        new_to2_blood: float = (
            to2_blood * _blood_vol - self._flux_o2) / _blood_vol
        if new_to2_blood < 0:
            new_to2_blood = 0

        new_co2_gas = (co2_gas * self._gas.vol_total + self._flux_o2) / self._gas.vol_total
        if new_co2_gas < 0:
            new_co2_gas = 0

        # calculate the CO2 flux from the blood to the gas compartment
        self._flux_co2 = (pco2_blood - pco2_gas) * \
            self.dif_co2 * self.dif_co2_factor * self._t

        # calculate the new CO2 concentrations of the gas and blood compartments
        new_tco2_blood: float = (
            tco2_blood * _blood_vol - self._flux_co2) / _blood_vol
        if new_tco2_blood < 0:
            new_tco2_blood = 0

        new_cco2_gas = (cco2_gas * self._gas.vol_total +
                        self._flux_co2) / self._gas.vol_total
        if new_cco2_gas < 0:
            new_cco2_gas = 0

        # transfer the new concentrations
        self._blood.aboxy['to2'] = new_to2_blood
        self._blood.aboxy['tco2'] = new_tco2_blood
        self._gas.co2 = new_co2_gas
        self._gas.cco2 = new_cco2_gas
