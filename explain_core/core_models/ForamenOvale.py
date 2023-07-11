from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodResistor import BloodResistor


class ForamenOvale(BaseModel):
    # independent variables
    length: float = 0.01
    diameter: float = 0.002
    no_flow: bool = False

    # dependent variables
    res: float = 1800.0
    flow: float = 0.0

    # local variables
    _fo: BloodResistor = {}

    def init_model(self, model: object) -> bool:
        # initialize the parent class
        super().init_model(model)

        # configure a foramen ovale component
        _args = {
            "name": "FO",
            "description": "foramen ovale",
            "model_type": "BloodResistor",
            "is_enabled": self.is_enabled,
            "no_flow": self.no_flow,
            "no_back_flow": False,
            "comp_from": "LA",
            "comp_to": "RA",
            "r_for": 1500,
            "r_back": 1500,
            "r_k": 0
        }
        # instantiate a foramen ovale as a blood resistor
        self._fo = BloodResistor(**_args)

        # initialize this blood resistor
        self._fo.init_model(model)

    def calc_model(self) -> None:
        # calculate the current foramen ovale and other properties
        self.res = self.calc_resistance()
        self._fo.r_for = self.res
        self._fo.r_back = self.res
        self._fo.is_enabled = self.is_enabled
        self._fo.no_flow = self.no_flow

        # calc the resistor
        self._fo.calc_model()

        # get the state of the blood resistor
        self.flow = self._fo.flow

    def calc_resistance(self) -> float:
        return 1500.0
