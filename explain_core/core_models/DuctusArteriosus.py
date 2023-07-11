from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodResistor import BloodResistor
from explain_core.helpers.TubeResistance import calc_resistance_tube


class DuctusArteriosus(BaseModel):
    # independent variables
    length: float = 10
    diameter: float = 2
    viscosity: float = 6.0
    nonlin: float = 0.0
    no_flow: bool = False

    # dependent variables
    res: float = 1800.0
    flow: float = 0.0

    # local variables
    _duct: BloodResistor = {}

    def init_model(self, model: object) -> bool:
        # initialize the parent class
        super().init_model(model)

        # instantiate a ductus arteriosus as a blood resistor
        self._duct = BloodResistor(**{
            "name": "DA",
            "description": "ductus arteriosus",
            "model_type": "BloodResistor",
            "is_enabled": self.is_enabled,
            "no_flow": self.no_flow,
            "no_back_flow": False,
            "comp_from": "AAR",
            "comp_to": "PA",
            "r_for": 40000.0,
            "r_back": 40000.0,
            "r_k": self.nonlin
        })

        # initialize this blood resistor
        self._duct.init_model(model)

    def calc_model(self) -> None:
        # calculate the current ductus resistance and other properties
        if self.diameter > 0:
            self.res = calc_resistance_tube(
                self.diameter, self.length, self.viscosity)
        else:
            self.res = 4000000
        self._duct.r_for = self.res
        self._duct.r_back = self.res
        self._duct.r_k = self.nonlin
        self._duct.is_enabled = self.is_enabled
        self._duct.no_flow = self.no_flow

        # calc the resistor
        self._duct.calc_model()

        # get the state of the blood resistor
        self.flow = self._duct.flow
