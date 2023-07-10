import math
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
    tubing_length: float = 1.6
    tubing_volume: float = 0.13
    ettube_diameter: float = 0.0035
    ettube_length: float = 0.11
    ettube_volume: float = 0.0025
    ettube_elastance: float = 20000.0
    ypiece_volume: float = 0.011
    ypiece_elastance: float = 25000.0
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

    _vent_parts: list = []

    # local constant
    _gas_constant: float = 62.36367

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # build the ventilator
        self.build_ventilator(model)

    def build_ventilator(self, model):
        # clear the ventilator part list
        self._vent_parts = []

        # build the mechanical ventilator using the gas capacitance model
        self._ventin = GasCapacitance(**{
            "name": "VENTIN",
            "description": "ventilator inspiration reservoir",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": True,
            "vol": 5.2,
            "u_vol": 5.0,
            "el_base": 1000.0,
            "el_k": 0,
            "pres_atm": self.p_atm
        })
        self._ventin.init_model(model)
        self._ventin.calc_model()
        self.set_air_composition(
            self._ventin, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'])
        self._vent_parts.append(self._ventin)

        self._tubingin = GasCapacitance(**{
            "name": "TUBINGIN",
            "description": "inspiratory tubing of the mechanical ventilator",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": self.tubing_volume,
            "u_vol": self.tubing_volume,
            "el_base": self.tubing_elastance,
            "el_k": 0
        })
        self._tubingin.init_model(model)
        self._tubingin.calc_model()
        self.set_air_composition(
            self._tubingin, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'])
        self._vent_parts.append(self._tubingin)

        self._tubingout = GasCapacitance(**{
            "name": "TUBINGOUT",
            "description": "expiratory tubing of the mechanical ventilator",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": self.tubing_volume,
            "u_vol": self.tubing_volume,
            "el_base": self.tubing_elastance,
            "el_k": 0
        })
        self._tubingout.init_model(model)
        self._tubingout.calc_model()
        self.set_air_composition(
            self._tubingout, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'])
        self._vent_parts.append(self._tubingout)

        self._ypiece = GasCapacitance(**{
            "name": "YPIECE",
            "description": "ypiece of the mechanical ventilator",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": self.ypiece_volume,
            "u_vol": self.ypiece_volume,
            "el_base": self.ypiece_elastance,
            "el_k": 0
        })
        self._ypiece.init_model(model)
        self._ypiece.calc_model()
        self.set_air_composition(
            self._ypiece, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'])
        self._vent_parts.append(self._ypiece)

        self._ettube = GasCapacitance(**{
            "name": "ETTUBE",
            "description": "endotracheal tube",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": self.ettube_volume,
            "u_vol": self.ettube_volume,
            "el_base": self.ettube_elastance,
            "el_k": 0
        })
        self._ettube.init_model(model)
        self._ettube.calc_model()
        self.set_air_composition(
            self._ettube, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'])
        self._vent_parts.append(self._ettube)

        self._ventout = GasCapacitance(**{
            "name": "VENTOUT",
            "description": "ventilator expiration reservoir",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": True,
            "vol": 1000.0,
            "u_vol": 1000.0,
            "el_base": 1000,
            "el_k": 0
        })
        self._ventout.init_model(model)
        self._ventout.calc_model()
        self.set_air_composition(
            self._ventout, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'])
        self._vent_parts.append(self._ventout)

        # connect the parts using the gas resistor models
        self._insp_valve = GasResistor(**{
            "name": "INSPVALVE",
            "description": "inspiration valve of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": True,
            "comp_from": "VENTIN",
            "comp_to": "TUBINGIN",
            "r_for": 30000,
            "r_back": 1000000,
            "r_k": 0,
        })
        self._insp_valve.init_model(model, self._ventin, self._tubingin)
        self._vent_parts.append(self._insp_valve)

        self._tubingin_ypiece = GasResistor(**{
            "name": "TUBINGIN_YPIECE",
            "description": "connector between tubing in and ypiece of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": "TUBINGIN",
            "comp_to": "YPIECE",
            "r_for": 25,
            "r_back": 25,
            "r_k": 0,
        })
        self._tubingin_ypiece.init_model(model, self._tubingin, self._ypiece)
        self._vent_parts.append(self._tubingin_ypiece)

        self._ypiece_ettube = GasResistor(**{
            "name": "YPIECE_ETTUBE",
            "description": "connector between ypiece and ettube of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": "YPIECE",
            "comp_to": "ETTUBE",
            "r_for": 35,
            "r_back": 35,
            "r_k": 0,
        })
        self._ypiece_ettube.init_model(model, self._ypiece, self._ettube)
        self._vent_parts.append(self._ypiece_ettube)

        self._ettube_ds = GasResistor(**{
            "name": "ETTUBE_DS",
            "description": "connector between ettube and dead space",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": True,
            "no_back_flow": False,
            "comp_from": "ETTUBE",
            "comp_to": "DS",
            "r_for": 35,
            "r_back": 35,
            "r_k": 0,
        })
        self._ettube_ds.init_model(
            model, self._ettube, self._model.models['DS'])
        self._vent_parts.append(self._ettube_ds)

        self._ypiece_tubingout = GasResistor(**{
            "name": "YPIECE_TUBINGOUT",
            "description": "connector between the ypiece and the tubing out of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": "YPIECE",
            "comp_to": "TUBINGOUT",
            "r_for": 35,
            "r_back": 35,
            "r_k": 0,
        })
        self._ypiece_tubingout.init_model(model, self._ypiece, self._tubingout)
        self._vent_parts.append(self._ypiece_tubingout)

        self._exp_valve = GasResistor(**{
            "name": "EXPVALVE",
            "description": "expiration valve of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": True,
            "comp_from": "TUBINGOUT",
            "comp_to": "VENTOUT",
            "r_for": 300000,
            "r_back": 300000,
            "r_k": 0,
        })
        self._exp_valve.init_model(model, self._tubingout, self._ventout)
        self._vent_parts.append(self._exp_valve)

    def set_air_composition(self, comp, fo2_dry, fco2_dry, fn2_dry, fother_dry):
        # calculate the concentration at this pressure and temperature in mmol/l using the gas law
        comp.ctotal = (
            comp.pres / (self._gas_constant * (273.15 + self.temp))) * 1000.0

        # calculate the water vapour pressure, concentration and fraction for this temperature and humidity (0 - 1)
        comp.ph2o = math.pow(math.e, 20.386 - 5132 /
                             (self.temp + 273)) * self.humidity
        comp.fh2o = comp.ph2o / comp.pres
        comp.ch2o = comp.fh2o * comp.ctotal

        # calculate the o2 partial pressure, fraction and concentration
        comp.po2 = fo2_dry * (comp.pres - comp.ph2o)
        comp.fo2 = comp.po2 / comp.pres
        comp.co2 = comp.fo2 * comp.ctotal

        # calculate the co2 partial pressure, fraction and concentration
        comp.pco2 = fco2_dry * (comp.pres - comp.ph2o)
        comp.fco2 = comp.pco2 / comp.pres
        comp.cco2 = comp.fco2 * comp.ctotal

        # calculate the n2 partial pressure, fraction and concentration
        comp.pn2 = fn2_dry * (comp.pres - comp.ph2o)
        comp.fn2 = comp.pn2 / comp.pres
        comp.cn2 = comp.fn2 * comp.ctotal

        # calculate the other gas partial pressure, fraction and concentration
        comp.pother = fother_dry * (comp.pres - comp.ph2o)
        comp.fother = comp.pother / comp.pres
        comp.cother = comp.fother * comp.ctotal
