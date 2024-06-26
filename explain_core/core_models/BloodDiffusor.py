from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance
from explain_core.functions.BloodComposition import set_blood_composition


class BloodDiffusor(BaseModel):
    # independent variables
    dif_o2: float = 0.01
    dif_o2_factor: float = 1.0
    dif_o2_scaling_factor: float = 1.0
    dif_co2: float = 0.01
    dif_co2_factor: float = 1.0
    dif_co2_scaling_factor: float = 1.0

    # local variables
    _comp_blood1: Capacitance = {}
    _comp_blood2: Capacitance = {}
    _flux_o2: float = 0
    _flux_co2: float = 0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the blood capacitances
        if type(self.comp_blood1) is str:
            self._comp_blood1 = self._model.models[self.comp_blood1]
        else:
            self._comp_blood1 = self.comp_blood1

        if type(self.comp_blood2) is str:
            self._comp_blood2 = self._model.models[self.comp_blood2]
        else:
            self._comp_blood2 = self.comp_blood2

    def calc_model(self) -> None:
        super().calc_model()

        # we need to po2 and pco2 so we need to calculate the blood composition
        set_blood_composition(self._comp_blood1)
        set_blood_composition(self._comp_blood2)

        # get the partial pressures and gas concentrations from the components
        po2_comp_blood1: float = self._comp_blood1.aboxy["po2"]
        to2_comp_blood1: float = self._comp_blood1.aboxy["to2"]

        pco2_comp_blood1: float = self._comp_blood1.aboxy["pco2"]
        tco2_comp_blood1: float = self._comp_blood1.aboxy["tco2"]

        po2_comp_blood2: float = self._comp_blood2.aboxy["po2"]
        to2_comp_blood2: float = self._comp_blood2.aboxy["to2"]

        pco2_comp_blood2: float = self._comp_blood2.aboxy["pco2"]
        tco2_comp_blood2: float = self._comp_blood2.aboxy["tco2"]

        # calculate the O2 and CO2 flux
        self._flux_o2 = (
            (po2_comp_blood1 - po2_comp_blood2)
            * self.dif_o2
            * self.dif_o2_factor
            * self.dif_o2_scaling_factor
            * self._t
        )
        self._flux_co2 = (
            (pco2_comp_blood1 - pco2_comp_blood2)
            * self.dif_co2
            * self.dif_co2_factor
            * self.dif_co2_scaling_factor
            * self._t
        )

        # calculate the new O2 and CO2 concentrations
        _comp_blood1_vol: float = self._comp_blood1.vol + self._comp_blood1.u_vol
        _comp_blood2_vol: float = self._comp_blood2.vol + self._comp_blood2.u_vol

        new_to2_comp_blood1: float = (
            to2_comp_blood1 * _comp_blood1_vol - self._flux_o2
        ) / _comp_blood1_vol
        if new_to2_comp_blood1 < 0:
            new_to2_comp_blood1 = 0

        new_to2_comp_blood2: float = (
            to2_comp_blood2 * _comp_blood2_vol + self._flux_o2
        ) / _comp_blood2_vol
        if new_to2_comp_blood2 < 0:
            new_to2_comp_blood2 = 0

        new_tco2_comp_blood1: float = (
            tco2_comp_blood1 * _comp_blood1_vol - self._flux_co2
        ) / _comp_blood1_vol
        if new_tco2_comp_blood1 < 0:
            new_tco2_comp_blood1 = 0

        new_tco2_comp_blood2: float = (
            tco2_comp_blood2 * _comp_blood2_vol + self._flux_co2
        ) / _comp_blood2_vol
        if new_tco2_comp_blood2 < 0:
            new_tco2_comp_blood2 = 0

        # set the new concentrations
        self._comp_blood1.aboxy["to2"] = new_to2_comp_blood1
        self._comp_blood1.aboxy["tco2"] = new_tco2_comp_blood1

        self._comp_blood2.aboxy["to2"] = new_to2_comp_blood2
        self._comp_blood2.aboxy["tco2"] = new_tco2_comp_blood2
