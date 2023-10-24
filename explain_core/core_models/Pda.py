from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Resistor import Resistor


class Pda(BaseModel):
    # independent model parameters
    da_model: str = "DA"
    no_flow: bool = True
    diameter: float = 0.1
    length: float = 0.1
    viscosity: float = 6.0
    non_lin_factor: float = 1.0

    # dependent parameters
    flow: float = 0.0
    velocity: float = 0.0

    # references to the model components
    _pda: Resistor = {}
    _current_diameter: float = 0.0
    _target_diameter: float = 0.0
    _diameter_stepsize: float = 0.0
    _in_time: float = 5.0
    _at_time: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        self._pda = self._model.models[self.da_model]

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        self._pda.no_flow = self.no_flow
        self._pda.is_enabled = self.is_enabled
        self._pda.r_k = self.non_lin_factor

        self.velocity = self._pda.velocity
        self.flow = self._pda.flow * 60.0

        if self.no_flow:
            self.flow = 0.0
            self.velocity = 0.0
            return

        if self._at_time > 0:
            self._at_time -= self._t
            return

        if self._diameter_stepsize != 0:
            self._current_diameter += self._diameter_stepsize
            self._in_time -= self._t
            if abs(self._current_diameter - self._target_diameter) < abs(
                self._diameter_stepsize
            ):
                self._diameter_stepsize = 0.0
                self._current_diameter = self._target_diameter
                if self._target_diameter < 0.11:
                    self.no_flow = True

            self._pda.set_diameter(self._current_diameter)

    def open_ductus(self, new_diameter=2.5, in_time: float = 5.0, at_time: float = 0.0):
        if new_diameter > 5.0:
            print("Error! De ductus arteriosus diameter can't be higher then 5.0 mm")
            return

        self.no_flow = False
        self._target_diameter = new_diameter
        self._current_diameter = self._pda.diameter
        self._in_time = in_time
        self._at_time = at_time
        self._diameter_stepsize = (
            (self._target_diameter - self._current_diameter) / self._in_time
        ) * self._t

    def close_ductus(self, in_time: float = 5.0, at_time: float = 0.0):
        self._target_diameter = 0.1
        self._current_diameter = self._pda.diameter
        self._in_time = in_time
        self._at_time = at_time
        self._diameter_stepsize = (
            (self._target_diameter - self._current_diameter) / self._in_time
        ) * self._t

    def set_diameter(self, new_diameter):
        self.diameter = new_diameter
        self._pda.set_diameter(new_diameter)

    def set_length(self, new_length):
        self.length = new_length
        self._pda.set_length(new_length)

    def set_non_linear_factor(self, new_nonlink):
        self.non_lin_factor = new_nonlink
        self._pda.set_r_k(new_nonlink)
