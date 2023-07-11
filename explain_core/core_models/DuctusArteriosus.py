from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodResistor import BloodResistor


class DuctusArteriosus(BaseModel):
    # independent variables
    length: float = 0.01
    diameter: float = 0.002
    no_flow: bool = False

    # dependent variables
    res: float = 1800.0
    flow: float = 0.0

    # local variables
    _duct: BloodResistor = {}

    def init_model(self, model: object) -> bool:
        # initialize the parent class
        super().init_model(model)

        # configure a ductus arteriosus component
        _args = {
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
            "r_k": 0
        }
        # instantiate a ductus arteriosus as a blood resistor
        self._duct = BloodResistor(**_args)

        # initialize this blood resistor
        self._duct.init_model(model)

    def calc_model(self) -> None:
        # calculate the current ductus resistance and other properties
        self.res = self.calc_resistance()
        self._duct.r_for = self.res
        self._duct.r_back = self.res
        self._duct.is_enabled = self.is_enabled
        self._duct.no_flow = self.no_flow

        # calc the resistor
        self._duct.calc_model()

        # get the state of the blood resistor
        self.flow = self._duct.flow

    def calc_resistance(self) -> float:
        return 40000.0
