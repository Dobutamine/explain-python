import math

from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance


class Resistor(BaseModel):
    # independent variables
    p1_ext: float = 0.0
    p2_ext: float = 0.0
    r_for: float = 1.0
    r_for_factor: float = 1.0
    r_back: float = 1.0
    r_back_factor: float = 1.0
    r_k: float = 0.0
    r_k_factor: float = 1.0
    no_back_flow: bool = False
    no_flow: bool = False

    # dependent variables
    flow: float = 0.0

    # define object which hold references to a BloodCapacitance or TimeVaryingElastance
    _model_comp_from: Capacitance = {}
    _model_comp_to: Capacitance = {}

    def calc_model(self) -> None:
        # get the pressures
        _p1: float = self._model_comp_from.pres + self.p1_ext
        _p2: float = self._model_comp_to.pres + self.p2_ext

        # reset the external pressures
        self.p1_ext = 0
        self.p2_ext = 0

        if self.no_flow:
            self.flow = 0.0
            return

        # forward flow
        if (_p1 > _p2):
            self.flow = (_p1 - _p2) / (self.r_for * self.r_for_factor) - \
                self.r_k * self.r_k_factor * math.pow(self.no_flow, 2)
            self.update_volumes()
            return

        # so there is no forward flow, if no_back_flow is true then set flow to zero and return
        if self.no_back_flow:
            self.flow = 0.0
            return

        # back flow
        if (_p1 < _p2):
            self.flow = (_p1 - _p2) / (self.r_back * self.r_back_factor) + \
                self.r_k * self.r_k_factor * math.pow(self.no_flow, 2)
            self.update_volumes()
            return

    def update_volumes(self) -> None:
        # now update the volumes of the model components which are connected by this resistor
        if self.flow > 0:
            # flow is from comp_from to comp_to
            vol_not_removed: float = self._model_comp_from.volume_out(
                self.flow * self._t)
            self._model_comp_to.volume_in(
                (self.flow * self._t) - vol_not_removed, self._model_comp_from)
            return

        if self.flow < 0:
            # flow is from comp_to to comp_from
            vol_not_removed: float = self._model_comp_to.volume_out(
                -self.flow * self._t)
            self._model_comp_from.volume_in(
                (-self.flow * self._t) - vol_not_removed, self._model_comp_to)
            return
