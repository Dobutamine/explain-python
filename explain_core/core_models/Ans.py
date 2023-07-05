import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance
from explain_core.core_models.Heart import Heart


class Ans(BaseModel):
    # local variables
    _baroreceptor: Capacitance = {}
    _chemoreceptor: Capacitance = {}
    _heart: Heart = {}
    _a_map: float = 0.0
    _d_map_hp: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the basemodel parent class
        super().init_model(model)

        # get a reference to the baroreceptor location
        self._baroreceptor = self._model.models[self.baroreceptor_location]
        self._heart = self._model.models['Heart']

        return self._is_initialized

    def calc_model(self) -> None:

        # get the baroreflex input
        _baro_pres: float = self._baroreceptor.mean

        # calculate the activation function
        self._a_map = self.activation_function(
            _baro_pres, self.max_baro, self.set_baro, self.min_baro)

        # calculate the effectors
        self._d_map_hp = self._t * \
            ((1 / self.tc_map_hp) * (-self._d_map_hp + self._a_map)) + self._d_map_hp

        # apply the effects
        self._heart.heart_rate = 60000.0 / \
            (60000.0 / self.heart_rate_ref + self.g_map_hp * self._d_map_hp)

    def activation_function(self, value: float, max: float, setpoint: float, min: float):
        activation: float = 0.0

        if value >= max:
            activation = max - setpoint
        else:
            if value <= min:
                activation = min - setpoint
            else:
                activation = value - setpoint

        return activation
