from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasResistor import GasResistor


class MechanicalVentilator(BaseModel):
    # independent parameters
    p_atm: float = 760.0
    temp: float = 37.0
    humidity: float = 1.0
    fio2: float = 0.21
    tubing_elastance: float = 1160.0
    tubing_diameter: float = 0.0102
    tubing_length: float = 0.15
    ettube_diameter: float = 0.0035
    ettube_length: float = 0.11
    vent_mode: str = "PC"
    vent_rate: float = 40.0
    vent_sync: bool = True
    vent_trigger: float = 0.001
    insp_time: float = 0.4
    insp_flow: float = 10.0
    exp_flow: float = 3.0
    pip: float = 14.3
    pip_max: float = 20.0
    peep: float = 2.9
    tidal_volume: float = 0.015

    # ventilator parts
    _ventin: GasCapacitance = {}
    _tubingin: GasCapacitance = {}
    _ypiece: GasCapacitance = {}
    _ettube: GasCapacitance = {}
    _tubingout: GasCapacitance = {}
    _ventout: GasCapacitance = {}

    _insp_valve: GasResistor = {}
    _tubingin_ypiece: GasResistor = {}
    _ypiece_ettube: GasResistor = {}
    _ettube_ds: GasResistor = {}
    _ypiece_tubingout: GasResistor = {}
    _exp_valve: GasResistor = {}

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # build the mechanical ventilator using the gas capacitance model
        self._ventin = GasCapacitance({
            "name": "VENTIN",
            "description": "ventilator inspiration reservoir",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
        })
        self._tubingin = GasCapacitance({
            "name": "TUBINGIN",
            "description": "inspiratory tubing of the mechanical ventilator",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
        })
        self._ypiece = GasCapacitance({
            "name": "YPIECE",
            "description": "ypiece of the mechanical ventilator",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
        })
        self._ettube = GasCapacitance({
            "name": "ETTUBE",
            "description": "endotracheal tube",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
        })
        self._tubingout = GasCapacitance({
            "name": "TUBINGOUT",
            "description": "expiratory tubing of the mechanical ventilator",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
        })
        self._ventout = GasCapacitance({
            "name": "VENTOUT",
            "description": "ventilator expiration reservoir",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
        })

        # connect the parts using the gas resistor models
        self._insp_valve = GasResistor({
            "name": "INSPVALVE",
            "description": "inspiration valve of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
        })
        self._tubingin_ypiece = GasResistor({
            "name": "TUBINGIN_YPIECE",
            "description": "connector between tubing in and ypiece of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
        }
        )
        self._ypiece_ettube = GasResistor({
            "name": "YPIECE_ETTUBE",
            "description": "connector between ypiece and ettube of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
        })
        self._ettube_ds = GasResistor({
            "name": "ETTUBE_DS",
            "description": "connector between ettube and dead space",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
        })
        self._ypiece_tubingout = GasResistor({
            "name": "YPIECE_TUBINGOUT",
            "description": "connector between the ypiece and the tubing out of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
        })
        self._exp_valve = GasResistor({
            "name": "EXPVALVE",
            "description": "expiration valve of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
        })
