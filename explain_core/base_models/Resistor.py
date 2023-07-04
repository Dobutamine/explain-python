import math

from explain_core.base_models.BaseModel import BaseModel


class Resistor(BaseModel):
    # independent variables
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

    # local variable holding the pressures
    _p1: float = 0.0
    _p2: float = 0.0

    def calc_model(self) -> None:
        if self.no_flow:
            self.flow = 0.0
            return

        # forward flow
        if (self._p1 > self._p2):
            self.flow = (self._p1 - self._p2) / (self.r_for * self.r_for_factor) - \
                self.r_k * self.r_k_factor * math.pow(self.no_flow, 2)
            return

        # so there is no forward flow, if no_back_flow is true then set flow to zero and return
        if self.no_back_flow:
            self.flow = 0.0
            return

        # back flow
        if (self._p1 < self._p2):
            self.flow = (self._p1 - self._p2) / (self.r_for * self.r_for_factor) + \
                self.r_k * self.r_k_factor * math.pow(self.no_flow, 2)
