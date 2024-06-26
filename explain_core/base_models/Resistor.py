import math

from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance
from explain_core.functions.TubeResistance import calc_resistance_tube


class Resistor(BaseModel):
    # independent variables
    p1_ext: float = 0.0
    p1_ext_factor: float = 1.0
    p2_ext: float = 0.0
    p2_ext_factor: float = 1.0

    r_for: float = 1.0
    r_for_factor: float = 1.0
    r_back: float = 1.0
    r_back_factor: float = 1.0

    r_k: float = 0.0
    r_k_factor: float = 1.0

    r_mob_factor: float = 1.0
    r_ans_factor: float = 1.0
    r_drug_factor: float = 1.0
    r_scaling_factor: float = 1.0

    r_ext: float = 0.0
    r_ext_factor: float = 1.0
    r_ans_factor: float = 1.0
    ans_activity_factor: float = 1.0

    no_back_flow: bool = False
    no_flow: bool = False

    length: float = 0.0  # in mm
    diameter: float = 0.0  # in mm
    viscosity: float = 6.0  # in cP

    # dependent variables
    flow: float = 0.0
    velocity: float = 0.0
    area: float = 0.0

    # define object which hold references to a model component which derives from the Capacitance class
    _model_comp_from: Capacitance = {}
    _model_comp_to: Capacitance = {}

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        if type(self.comp_from) is str:
            self._model_comp_from = self._model.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) is str:
            self._model_comp_to = self._model.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to

        # if a diameter and length are set then calculate the resistance by using these parameters
        self.calc_resistance()

        # flag that the model is initialized
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # get the pressures of the connected model components
        _p1 = self._model_comp_from.pres + self.p1_ext * self.p1_ext_factor
        _p2 = self._model_comp_to.pres + self.p2_ext * self.p2_ext_factor

        # reset the external pressures
        self.p1_ext = 0
        self.p2_ext = 0

        # calculate the resistance if a diameter and length are set
        if self.diameter > 0.0 and self.length > 0.0:
            self.calc_resistance()

        # calculate the resistances
        _r_for_base = self.r_for * self.r_scaling_factor
        r_for: float = (
            _r_for_base
            + (self.r_for_factor * _r_for_base - _r_for_base)
            + (self.r_ans_factor * _r_for_base - _r_for_base) * self.ans_activity_factor
            + (self.r_mob_factor * _r_for_base - _r_for_base)
            + (self.r_drug_factor * _r_for_base - _r_for_base)
            + self.r_k * self.r_k_factor * self.r_scaling_factor * self.flow**2
        )
        _r_back_base = self.r_back * self.r_scaling_factor
        r_back: float = (
            _r_back_base
            + (self.r_back_factor * _r_back_base - _r_back_base)
            + (self.r_ans_factor * _r_back_base - _r_back_base)
            * self.ans_activity_factor
            + (self.r_mob_factor * _r_back_base - _r_back_base)
            + (self.r_drug_factor * _r_back_base - _r_back_base)
            + self.r_k * self.r_k_factor * self.r_scaling_factor * self.flow**2
        )

        # check if the resistances are not too small for the current stepsize
        if r_for < 20.0:
            r_for = 20.0

        if r_back < 20.0:
            r_back = 20.0

        # calculate the flow
        if self.no_flow or (_p1 <= _p2 and self.no_back_flow):
            self.flow = 0.0
        elif _p1 > _p2:  # forward flow
            self.flow = (_p1 - _p2) / r_for
        else:  # back flow
            self.flow = (_p1 - _p2) / r_back

        # calculate the velocity = flow_rate (in m^3/s) / (pi * radius^2) in m/s
        self.area = math.pow((self.diameter * 0.001) / 2.0, 2.0) * math.pi  # in m^2
        # flow is in l/s
        if self.area > 0:
            self.velocity = (self.flow * 0.001) / self.area
            self.velocity = self.velocity * 4.0

        # now update the volumes of the model components which are connected by this resistor
        if self.flow > 0:
            # flow is from comp_from to comp_to
            vol_not_removed: float = self._model_comp_from.volume_out(
                self.flow * self._t
            )
            # if not all volume can be removed from the model component then transfer the remaining volume to the other model component
            # this is undesirable but it is better than having a negative volume
            self._model_comp_to.volume_in(
                (self.flow * self._t) - vol_not_removed, self._model_comp_from
            )
            return

        if self.flow < 0:
            # flow is from comp_to to comp_from
            vol_not_removed: float = self._model_comp_to.volume_out(
                -self.flow * self._t
            )

            # if not all volume can be removed from the model component then transfer the remaining volume to the other model component
            # this is undesirable but it is better than having a negative volume
            self._model_comp_from.volume_in(
                (-self.flow * self._t) - vol_not_removed, self._model_comp_to
            )
            return

    def get_flow(self) -> float:
        return self.flow  # l/s

    def get_flow_lmin(self) -> float:
        return self.flow * 60.0  # l/min

    def get_velocity(self) -> float:
        return self.velocity  # in m/s

    def open(self):
        self.no_flow = False

    def close(self):
        self.no_flow = True

    def prevent_backflow(self):
        self.no_back_flow = True

    def allow_backflow(self):
        self.no_back_flow = False

    def set_diameter(self, new_diameter):
        if new_diameter > 0.0:
            self.diameter = new_diameter  # in mm
            self.calc_resistance()

    def set_length(self, new_length):
        if new_length > 0.0:
            self.length = new_length  # in mm
            self.calc_resistance()

    def set_viscosity(self, new_viscosity):
        if new_viscosity > 0.0:
            self.viscosity = new_viscosity  # in cP
            self.calc_resistance()

    def set_p1_ext(self, new_p1_ext):
        self.p1_ext = new_p1_ext  # in mmHg

    def set_p1_ext_factor(self, new_p1_ext_factor):
        self.p1_ext_factor = new_p1_ext_factor  # unitless

    def set_p2_ext(self, new_p2_ext):
        self.p2_ext = new_p2_ext  # in mmHg

    def set_p2_ext_factor(self, new_p2_ext_factor):
        self.p2_ext_factor = new_p2_ext_factor  # unitless

    def set_r_ext(self, new_r_ext):
        self.r_ext = new_r_ext  # in mmHg*s / l
        self.calc_resistance()

    def set_r_ext_factor(self, new_r_ext_factor):  # unitless
        self.r_ext_factor = new_r_ext_factor
        self.calc_resistance()

    def set_r_k(self, new_r_k):
        self.r_k = new_r_k

    def set_r_k_factor(self, new_r_k_factor):
        self.r_k_factor = new_r_k_factor

    def set_r_for(self, new_r_for):
        self.r_for = new_r_for

    def set_r_for_factor(self, new_r_for_factor):
        self.r_for_factor = new_r_for_factor

    def set_r_back(self, new_r_back):
        self.r_back = new_r_back

    def set_r_back_factor(self, new_r_back_factor):
        self.r_back_factor = new_r_back_factor

    def get_r_for(self) -> float:
        return self.r_for * self.r_scaling_factor

    def get_r_back(self) -> float:
        return self.r_back * self.r_scaling_factor

    def calc_resistance(self):
        # set the resistances by calculating the resistance from the diameter and length
        if self.diameter > 0.0 and self.length > 0.0:
            self.r_for = (
                calc_resistance_tube(self.diameter, self.length, self.viscosity)
                + self.r_ext * self.r_ext_factor
            )
            self.r_back = (
                calc_resistance_tube(self.diameter, self.length, self.viscosity)
                + self.r_ext * self.r_ext_factor
            )
            radius_meters: float = self.diameter / 2 / 1000.0
            self.area = math.pi * math.pow(radius_meters, 2.0)
