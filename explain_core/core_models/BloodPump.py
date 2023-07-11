import math
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodResistor import BloodResistor


class Pump(BloodCapacitance):
    # independent parameters
    pump_mode: int = 0              # 0 = centrifugal, 1 = roller pump
    pump_pressure: float = 0.0
    pump_rpm: float = 0.0

    # dependent parameters
    pres_inlet: float = 0.0
    pres_outlet: float = 0.0

    # local parameters
    _inlet_res: BloodResistor = {}
    _outlet_res: BloodResistor = {}

    def init_model(self, model: object) -> bool:
        # initialize the parent class
        super().init_model(model)

        # find the connected connectors
        self._inlet_res = self._model.models[self.inlet]
        self._outlet_res = self._model.models[self.outlet]

    def calc_model(self) -> None:
        # calculate the parent class
        super().calc_model()

        # do the blood pump specific actions
        self.pump_pressure = -self.pump_rpm / 25.0

        # determine the inlet and outlet pressures and transfer them to the connected bloodresistors
        if self.pump_mode == 0:
            self._inlet_res.p1_ext = 0.0
            self._inlet_res.p2_ext = self.pump_pressure
        else:
            self._outlet_res.p1_ext = self.pump_pressure
            self._outlet_res.p2_ext = 0.0
