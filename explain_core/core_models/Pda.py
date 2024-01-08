from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Resistor import Resistor
from explain_core.base_models.Capacitance import Capacitance


class Pda(BaseModel):
    # independent model parameters
    da_model: str = "DA"
    da_connectors = ["AAR_DA", "DA_PA"]
    no_flow: bool = True
    diameter: float = 0.1
    length: float = 0.1
    viscosity: float = 6.0
    non_lin_factor: float = 1.0

    # dependent parameters
    flow: float = 0.0
    velocity: float = 0.0

    # references to the model components
    _pda: Capacitance = {}
    _pda_in: Resistor = {}
    _pda_out: Resistor = {}

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
        self._pda_in = self._model.models[self.da_connectors[0]]
        self._pda_out = self._model.models[self.da_connectors[1]]

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # open the connectors when the model is enabled
        self._pda_in.no_flow = self.no_flow
        self._pda_out.no_flow = self.no_flow

        # enable the pda components
        self._pda.is_enabled = self.is_enabled
        self._pda_in.is_enabled = self.is_enabled
        self._pda_out.is_enabled = self.is_enabled

        # set the length of the duct
        self._pda_out.length = self.length

        # set the non linear factors
        self._pda_out.r_k = self.non_lin_factor

        self.velocity = self._pda_out.velocity
        self.flow = self._pda_out.flow

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

            self._pda_out.set_diameter(self._current_diameter)
            self._pda_in.set_diameter(self._current_diameter)

    def open_ductus(self, new_diameter=2.5, in_time: float = 5.0, at_time: float = 0.0):
        if new_diameter > 15.0:
            print("Error! De ductus arteriosus diameter can't be higher then 5.0 mm")
            return

        self.no_flow = False
        self._target_diameter = new_diameter
        self._current_diameter = self._pda_out.diameter
        self._in_time = in_time
        self._at_time = at_time
        self._diameter_stepsize = (
            (self._target_diameter - self._current_diameter) / self._in_time
        ) * self._t

    def close_ductus(self, in_time: float = 5.0, at_time: float = 0.0):
        self._target_diameter = 0.1
        self._current_diameter = self._pda_out.diameter
        self._in_time = in_time
        self._at_time = at_time
        self._diameter_stepsize = (
            (self._target_diameter - self._current_diameter) / self._in_time
        ) * self._t

    def set_diameter(self, new_diameter):
        self.diameter = new_diameter
        self._pda_out.set_diameter(new_diameter)

    def set_length(self, new_length):
        self.length = new_length
        self._pda_out.set_length(new_length)

    def set_non_linear_factor(self, new_nonlink):
        self.non_lin_factor = new_nonlink
        self._pda_out.set_r_k(new_nonlink)
