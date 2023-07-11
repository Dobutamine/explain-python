from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance


class Diffusor(BaseModel):
    # independent variables
    dif_o2: float = 0.01
    dif_o2_factor: float = 1.0
    dif_co2: float = 0.01
    dif_co2_factor: float = 1.0

    # local variables
    _blood1: Capacitance = {}
    _blood2: Capacitance = {}
    _calc_acidbase = {}
    _calc_oxy = {}
    _flux_o2: float = 0
    _flux_co2: float = 0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        if type(self.comp_blood1) is str:
            self._blood1 = self._model.models[self.comp_blood1]
        else:
            self._blood1 = self.comp_blood1

        if type(self.comp_blood2) is str:
            self._model_comp_to = self._model.models[self.comp_blood2]
        else:
            self._model_comp_to = self.comp_blood2

        self._calc_acidbase = self._model.models['Blood'].calc_acidbase_from_tco2
        self._calc_oxy = self._model.models['Blood'].calc_oxygenation_from_to2

    def calc_model(self) -> None:
        super().calc_model()

        # calculate the po2 and pco2 in the blood compartments
        self._calc_acidbase(self._blood1)
        self._calc_oxy(self._blood1)

        self._calc_acidbase(self._blood2)
        self._calc_oxy(self._blood2)

        # get the partial pressures and gas concentrations from the components
        po2_blood1: float = self._blood1.aboxy['po2']
        pco2_blood1: float = self._blood1.aboxy['pco2']
        to2_blood1: float = self._blood1.aboxy['to2']
        tco2_blood1: float = self._blood1.aboxy['tco2']

        po2_blood2: float = self._blood2.aboxy['po2']
        pco2_blood2: float = self._blood2.aboxy['pco2']
        to2_blood2: float = self._blood2.aboxy['to2']
        tco2_blood2: float = self._blood2.aboxy['tco2']

        # calculate the O2 flux from the blood to the gas compartment
        self._flux_o2 = (po2_blood1 - po2_blood2) * self.dif_o2 * \
            self.dif_o2_factor * self._t

        # calculate the new O2 concentrations of the gas and blood compartments
        new_to2_blood1: float = (
            to2_blood1 * self._blood1.vol - self._flux_o2) / self._blood1.vol
        if new_to2_blood1 < 0:
            new_to2_blood1 = 0

        new_to2_blood2: float = (
            to2_blood2 * self._blood2.vol + self._flux_o2) / self._blood2.vol
        if new_to2_blood2 < 0:
            new_to2_blood2 = 0

        # calculate the CO2 flux from the blood to the gas compartment
        self._flux_co2 = (pco2_blood1 - pco2_blood2) * \
            self.dif_co2 * self.dif_co2_factor * self._t

        # calculate the new CO2 concentrations of the gas and blood compartments
        new_tco2_blood1: float = (
            tco2_blood1 * self._blood1.vol - self._flux_co2) / self._blood1.vol
        if new_tco2_blood1 < 0:
            new_tco2_blood1 = 0

        new_tco2_blood2: float = (
            tco2_blood2 * self._blood2.vol + self._flux_co2) / self._blood2.vol
        if new_tco2_blood2 < 0:
            new_tco2_blood2 = 0

        # transfer the new concentrations
        self._blood1.aboxy['to2'] = new_to2_blood1
        self._blood1.aboxy['tco2'] = new_tco2_blood1
        self._blood2.aboxy['to2'] = new_to2_blood2
        self._blood2.aboxy['tco2'] = new_tco2_blood2
