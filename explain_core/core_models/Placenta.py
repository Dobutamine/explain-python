import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodResistor import BloodResistor
from explain_core.core_models.Diffusor import Diffusor


class Placenta(BaseModel):

    # placenta parts
    _placenta_parts: list = []
    _ua: BloodResistor = {}
    _uv: BloodResistor = {}
    _fpl: BloodCapacitance = {}
    _mpl: BloodCapacitance = {}
    _pl_diff: Diffusor = {}

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # build the ventilator
        self.build_placenta(model)

    def switch_placenta(self, state):
        # enable of disable the placenta
        self.is_enabled = state
        # turn off the connectors connecting the placenta to the base model
        if state:
            self._ua.no_flow = False
            self._uv.no_flow = False
        else:
            self._ua.no_flow = True
            self._uv.no_flow = True

    def calc_model(self) -> None:
        for placenta_part in self._placenta_parts:
            placenta_part.calc_model()

    def build_placenta(self, model):
        # clear the part list
        self._placenta_parts = []

        # define the individual parts
        self._fpl = BloodCapacitance(**{
            "name": "FPL",
            "description": "fetal placenta part",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "u_vol": 0.003,
            "vol": 0.005,
            "el_base": 23000,
            "el_k": 0
        })
        self._fpl.init_model(model)
        self._placenta_parts.append(self._fpl)

        self._mpl = BloodCapacitance(**{
            "name": "MPL",
            "description": "materna; placenta part",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "u_vol": 0.003,
            "vol": 0.005,
            "el_base": 23000,
            "el_k": 0
        })
        self._mpl.init_model(model)
        self._placenta_parts.append(self._mpl)

        self._pl_diff = Diffusor(**{
            "name": "PLDIFF",
            "description": "diffusor between fetal and maternal placenta",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": ["MPL", "FPL"],
            "comp_blood1": self._mpl,
            "comp_blood2": self._fpl,
            "dif_o2": 0.00001,
            "dif_co2": 0.00001,

        })
        self._pl_diff.init_model(model)
        self._placenta_parts.append(self._pl_diff)

        self._ua = BloodResistor(**{
            "name": "UA",
            "description": "umbilical arteries",
            "model_type": "BloodResistor",
            "is_enabled": True,
            "dependencies": ["AD"],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._model.models["AD"],
            "comp_to": self._fpl,
            "r_for": 2500,
            "r_back": 2500,
            "r_k": 0,
        })
        self._ua.init_model(model)
        self._placenta_parts.append(self._ua)

        self._uv = BloodResistor(**{
            "name": "UV",
            "description": "umbilical veins",
            "model_type": "BloodResistor",
            "is_enabled": True,
            "dependencies": ["IVCE"],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._fpl,
            "comp_to": self._model.models["IVCE"],
            "r_for": 2500,
            "r_back": 2500,
            "r_k": 0,
        })
        self._uv.init_model(model)
        self._placenta_parts.append(self._uv)
