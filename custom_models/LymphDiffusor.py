from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from custom_models.LymphCapacitance import LymphCapacitance

class LymphDiffusor(BaseModel):
    # independent variables
    dif_albumin: float = 0.0000
    dif_albumin_factor: float = 1.0       


    # local variables
    _comp1: BloodCapacitance or LymphCapacitance = {}
    _comp2: BloodCapacitance or LymphCapacitance = {}

    _flux_albumin: float = 0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the blood and/or lymph capacitances
        if type(self.comp1) is str:
            self._comp1 = self._model.models[self.comp1]
        else:
            self._comp1 = self.comp1

        if type(self.comp2) is str:
            self._comp2 = self._model.models[self.comp2]
        else:
            self._comp2 = self.comp2

    def calc_model(self) -> None:
        super().calc_model()

        # we need to po2 and pco2 so we need to calculate the blood composition
        #set_blood_composition(self._comp1)
        #set_blood_composition(self._comp2)

        # get the concentration albumin in both components
        albumin_comp1: float = self._comp1.aboxy['albumin']
        albumin_comp2: float = self._comp2.aboxy['albumin']

        # calculate the albumin flux
        self._flux_albumin = (albumin_comp1 - albumin_comp2) * self.dif_albumin * self.dif_albumin_factor * self._t

        # calculate the new albumin concentrations
        _comp1_vol:float = self._comp1.vol + self._comp1.u_vol
        _comp2_vol:float = self._comp2.vol + self._comp2.u_vol

        new_albumin_comp1: float = (albumin_comp1 * _comp1_vol - self._flux_albumin) / _comp1_vol
        if new_albumin_comp1 < 0:
            new_albumin_comp1 = 0

        new_albumin_comp2: float = (albumin_comp2 * _comp2_vol + self._flux_albumin) / _comp2_vol
        if new_albumin_comp2 < 0:
            new_albumin_comp2 = 0

        # set the new concentrations
        self._comp1.aboxy['albumin'] = new_albumin_comp1
        self._comp2.aboxy['albumin'] = new_albumin_comp2