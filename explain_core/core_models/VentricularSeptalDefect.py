from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodResistor import BloodResistor


class VentricularSeptalDefect(BaseModel):
    # independent variables
    length: float = 0.01
    diameter: float = 0.002
    no_flow: bool = False

    # dependent variables
    res: float = 1800.0
    flow: float = 0.0

    # local variables
    _vsd: BloodResistor = {}

    def init_model(self, model: object) -> bool:
        # initialize the parent class
        super().init_model(model)

        # instantiate a ventricular septal defect as a blood resistor
        self._vsd = BloodResistor(**{
            "name": "VSD",
            "description": "ventricular septal defect",
            "model_type": "BloodResistor",
            "is_enabled": self.is_enabled,
            "no_flow": self.no_flow,
            "no_back_flow": False,
            "comp_from": "LV",
            "comp_to": "RV",
            "r_vsdr": 1800,
            "r_back": 1800,
            "r_k": 0
        })

        # initialize this blood resistor
        self._vsd.init_model(model)

    def calc_model(self) -> None:
        # calculate the current ventricular septal defect and other properties
        self.res = self.calc_resistance()
        self._vsd.r_vsdr = self.res
        self._vsd.r_back = self.res
        self._vsd.is_enabled = self.is_enabled
        self._vsd.no_flow = self.no_flow

        # calc the resistor
        self._vsd.calc_model()

        # get the state of the blood resistor
        self.flow = self._vsd.flow

    def calc_resistance(self) -> float:
        return 1800.0
