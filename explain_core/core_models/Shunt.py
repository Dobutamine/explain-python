import math
from explain_core.base_models.Resistor import Resistor
from explain_core.functions.TubeResistance import calc_resistance_tube


class Shunt(Resistor):
    # independent parameters
    diameter: float = 2             # diameter in mm
    length: float = 10              # length in mm
    non_lin_factor: float = 0.0     # non linear flow factor
    viscosity: float = 6.0          # blood viscosity in cP

    # additional dependent parameters
    velocity: float = 0.0   # velocity in m/s

    def init_model(self, model: object) -> bool:
        # calculate the current resistance of the shunt
        self.r_for = calc_resistance_tube(self.diameter, self.length, self.viscosity)
        self.r_back = self.r_for
        self.r_k = self.non_lin_factor
        self.area = math.pi * self.diameter * self.diameter

        # initialize the parent class -> Resistor
        super().init_model(model)

        # signal that the model is initialized
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self):
        super().calc_model()

        # calculate the velocity = flow_rate (in mm^3/s) / (pi * radius^2) in m/s
        radius_meters: float = self.diameter / 2 / 1000.0
        self.velocity = self.flow / 1000.0 / (math.pi * math.pow(radius_meters, 2.0))

    def set_diameter(self, new_diameter: float):
        self.diameter = new_diameter
        self.r_for = calc_resistance_tube(
            self.diameter, self.length, self.viscosity)
        self.r_back = calc_resistance_tube(
            self.diameter, self.length, self.viscosity)

    def set_length(self, new_length: float):
        self.length = new_length
        self.r_for = calc_resistance_tube(
            self.diameter, self.length, self.viscosity)
        self.r_back = calc_resistance_tube(
            self.diameter, self.length, self.viscosity)

    def set_viscosity(self, new_viscosity: float):
        self.viscosity = new_viscosity
        self.r_for = calc_resistance_tube(
            self.diameter, self.length, self.viscosity)
        self.r_back = calc_resistance_tube(
            self.diameter, self.length, self.viscosity)
