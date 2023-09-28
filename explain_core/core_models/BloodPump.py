import math
from explain_core.base_models.Resistor import Resistor
from explain_core.core_models.BloodCapacitance import BloodCapacitance



class BloodPump(BloodCapacitance):
    # independent parameters
    pump_mode: int = 0              # 0 = centrifugal, 1 = roller pump
    pump_pressure: float = 0.0
    pump_rpm: float = 0.0
    inlet: str = ""
    outlet: str = ""

    # dependent parameters
    pres_inlet: float = 0.0
    pres_outlet: float = 0.0

    # local parameters
    _inlet_res: Resistor = {}
    _outlet_res: Resistor = {}

    def connect_pump(self, _in: Resistor, _out: Resistor):
        self._inlet_res = _in
        self._outlet_res = _out

    def calc_model(self) -> None:
        # calculate the parent class
        super().calc_model()

        # create a pressure gradient across the pump
        self.pump_pressure = -self.pump_rpm / 25.0
        if self.pump_mode == 0:
            self._inlet_res.set_p1_ext(0.0)
            self._inlet_res.set_p2_ext(self.pump_pressure)
        else:
            self._outlet_res.set_p1_ext(self.pump_pressure)
            self._outlet_res.set_p2_ext(0.0)
