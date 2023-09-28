import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.Resistor import Resistor
from explain_core.core_models.BloodPump import BloodPump
from explain_core.core_models.BloodDiffusor import BloodDiffusor
from explain_core.functions.TubeResistance import calc_resistance_tube


class Placenta(BaseModel):
    # independent parameters
    placenta_running: bool = False
    # normal fetal placenta blood flow 110-125 ml/min/kg

    fetal_umb_art_diameter: float =  4.0
    fetal_umb_art_length: float = 400.0

    fetal_umb_ven_diameter: float = 8.0
    fetal_umb_ven_length: float = 400.0

    fetal_pla_resistance: float = 20000
    fetal_pla_vol:float = 0.08
    fetal_pla_u_vol: float = 0.08
    fetal_pla_el_base: float = 5000

    fetal_umb_art_origin: str = "AD"
    fetal_umb_ven_target: str = "IVCE"

    mat_pla_flow: float = 0.65
    mat_to2: float = 7.0
    mat_tco2: float = 27.0

    mat_ut_art_vol: float = 1.02
    mat_ut_art_u_vol: float = 1.0
    mat_ut_art_el_base: float = 5000.0

    mat_ut_ven_vol: float = 4.008
    mat_ut_ven_u_vol: float = 4.0
    mat_ut_ven_el_base: float = 500.0

    mat_pla_vol:float = 0.5
    mat_pla_u_vol: float = 0.5
    mat_pla_el_base: float = 1000.0

    plac_do2: float = 0.1
    plac_dco2: float = 0.1

    # dependent parameters
    fetal_umb_art_resistance: float = 2000.0
    fetal_umb_ven_resistance: float = 500.0

    mat_placenta_flow: float = 0.0
    mat_placenta_volume: float = 0.0
    mat_placenta_pressure: float = 0.0

    fetal_placenta_flow: float = 0.0
    fetal_placenta_volume: float = 0.0
    fetal_placenta_pressure: float = 0.0
    fetal_umb_art_velocity: float = 0.0
    fetal_umb_ven_velocity: float = 0.0

    # objects
    _plac_parts = []
    _fetal_umb_art: Resistor = {}
    _fetal_umb_ven: Resistor = {}
    _fetal_pla: BloodCapacitance = {}
    _pla_exchanger: BloodDiffusor = {}
    _mat_ut_art: BloodCapacitance = {}
    _mat_pla: BloodCapacitance = {}
    _mat_ut_ven: BloodCapacitance = {}
    _mat_ut_art_pla: Resistor = {}
    _mat_pla_ut_uv: Resistor = {}
    _mat_ut_art_res: float = 1000.0
    _mat_ut_ven_res:float = 1000.0

    def switch_placenta(self, state):
        self.placenta_running = state

    def set_placenta_resistance(self, new_res):
        self.fetal_pla_resistance = new_res
        self._fetal_umb_art.set_r_ext(self.fetal_pla_resistance)
    
    def set_placenta_elastance(self, new_elastance):
        self.fetal_pla_el_base = new_elastance
        self._fetal_pla.el_base = self.fetal_pla_el_base

    def set_umb_arteries_diameter(self, new_diameter):
        self.fetal_umb_art_diameter = new_diameter
        self._fetal_umb_art.set_diameter(new_diameter)

    def set_umb_arteries_length(self, new_length):
        self.fetal_umb_art_length = new_length
        self._fetal_umb_art.set_length(new_length)
    
    def set_umb_arteries_nonlin_factor(self, new_factor):
        self._fetal_umb_art.set_non_lin_factor(new_factor)
    
    def set_umb_vein_nonlin_factor(self, new_factor):
        self._fetal_umb_ven.set_non_lin_factor(new_factor)

    def set_umb_vein_diameter(self, new_diameter):
        self.fetal_umb_ven_diameter = new_diameter
        self._fetal_umb_ven.set_diameter(new_diameter)

    def set_umb_vein_length(self, new_length):
        self.fetal_umb_ven_length = new_length
        self._fetal_umb_ven.set_length(new_length)

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # build the ecls system
        self.build_placenta(model)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self):
        if self.placenta_running:
            # calculate the settings for the maternal placental flow which is given in l/min
            res_mat: float = ((self._mat_ut_art.pres - self._mat_ut_ven.pres) / (self.mat_pla_flow / 60.0)) - 25.0
            self._mat_ut_art_pla.r_for = res_mat
            self._mat_ut_art_pla.r_back = res_mat
            self._mat_pla_ut_uv.r_for = 25.0
            self._mat_pla_ut_uv.r_back = 25.0
            self._mat_ut_art.aboxy['to2'] = self.mat_to2
            self._mat_ut_art.aboxy['tco2'] = self.mat_tco2

            # store the dependent variables
            self.mat_placenta_flow = self._mat_ut_art_pla.flow * 60.0
            self.mat_placenta_volume = self._mat_pla.vol
            self.mat_placenta_pressure = self._mat_pla.pres

            self.fetal_placenta_flow = self._fetal_umb_art.flow * 60.0
            self.fetal_placenta_volume = self._fetal_pla.vol
            self.fetal_placenta_pressure = self._fetal_pla.pres
            self.fetal_umb_art_velocity = self._fetal_umb_art.velocity
            self.fetal_umb_ven_velocity = self._fetal_umb_ven.velocity

            # do the model step calculations of the ecls system
            for item in self._plac_parts:
                item.step_model()


    def build_placenta(self, model):
        self._plac_parts = []

        # define the fetal placenta as a blood capacitance
        self._fetal_pla = BloodCapacitance(**{
            "name": "FETALPLA",
            "description": "fetal placenta",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.fetal_pla_vol,
            "u_vol": self.fetal_pla_u_vol,
            "el_base": self.fetal_pla_el_base,
            "el_k": 0
        })
        # initialize component
        self._fetal_pla.init_model(model)
        # copy the blood composition of the umbilical origin site as starting point
        self._fetal_pla.aboxy = self._model.models[self.fetal_umb_art_origin].aboxy.copy()
        self._fetal_pla.solutes = self._model.models[self.fetal_umb_art_origin].solutes.copy()
        # add to the components
        self._plac_parts.append(self._fetal_pla)
   
        # build the connectors
        self._fetal_umb_art = Resistor(**{
            "name": "FETALUMBART",
            "description": "connector between descending aorta and umbilical arteries",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "comp_from": self._model.models[self.fetal_umb_art_origin],
            "comp_to": self._fetal_pla,
            "length": self.fetal_umb_art_length,
            "diameter": self.fetal_umb_art_diameter,
            "r_k": 0.0,
            "no_flow": False,
            "no_back_flow": False
        })
        self._fetal_umb_art.init_model(model)
        # set the placental resistance
        self._fetal_umb_art.set_r_ext(self.fetal_pla_resistance)
        self._plac_parts.append(self._fetal_umb_art)

        self._fetal_umb_ven = Resistor(**{
            "name": "FETALUMBVEN",
            "description": "connector between placenta and umbilical veins",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "comp_from": self._fetal_pla,
            "comp_to": self._model.models[self.fetal_umb_ven_target],
            "length": self.fetal_umb_ven_length,
            "diameter": self.fetal_umb_ven_diameter,
            "r_k": 0.0,
            "no_flow": False,
            "no_back_flow": False
        })
        self._fetal_umb_ven.init_model(model)
        self._plac_parts.append(self._fetal_umb_ven)



        # build the maternal part
        self._mat_ut_art = BloodCapacitance(**{
            "name": "MATUTART",
            "description": "maternal uterine arteries",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.mat_ut_art_vol,
            "u_vol": self.mat_ut_art_u_vol,
            "el_base": self.mat_ut_art_el_base,
            "el_k": 0,
            "fixed_composition": True
        })
        # initialize component
        self._mat_ut_art.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._mat_ut_art.aboxy = self._model.models[self.fetal_umb_art_origin].aboxy.copy()
        self._mat_ut_art.solutes = self._model.models[self.fetal_umb_art_origin].solutes.copy()
        # add to the components
        self._plac_parts.append(self._mat_ut_art)

        self._mat_pla = BloodCapacitance(**{
            "name": "MATPLA",
            "description": "maternal placenta",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.mat_pla_vol,
            "u_vol": self.mat_pla_u_vol,
            "el_base": self.mat_pla_el_base,
            "el_k": 0,
            "fixed_composition": False
        })
        # initialize component
        self._mat_pla.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._mat_pla.aboxy = self._model.models[self.fetal_umb_art_origin].aboxy.copy()
        self._mat_pla.solutes = self._model.models[self.fetal_umb_art_origin].solutes.copy()
        # add to the components
        self._plac_parts.append(self._mat_pla)

        self._mat_ut_ven = BloodCapacitance(**{
            "name": "MATUTVEN",
            "description": "maternal uterine veins",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.mat_ut_ven_vol,
            "u_vol": self.mat_ut_ven_u_vol,
            "el_base": self.mat_ut_ven_el_base,
            "el_k": 0,
            "fixed_composition": True
        })
        # initialize component
        self._mat_ut_ven.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._mat_ut_ven.aboxy = self._model.models[self.fetal_umb_art_origin].aboxy.copy()
        self._mat_ut_ven.solutes = self._model.models[self.fetal_umb_art_origin].solutes.copy()
        # add to the components
        self._plac_parts.append(self._mat_ut_ven)

        # connectors of the maternal part
        self._mat_ut_art_pla = Resistor(**{
            "name": "MATUTARTPLA",
            "description": "connector between maternal uterine arteries and placenta",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._mat_ut_art,
            "comp_to": self._mat_pla,
            "r_for": self._mat_ut_art_res / 2.0,
            "r_back": self._mat_ut_art_res / 2.0,
            "r_k": 0,
        })
        self._mat_ut_art_pla.init_model(model)
        self._plac_parts.append(self._mat_ut_art_pla)

        self._mat_pla_ut_uv = Resistor(**{
            "name": "MATPLAUTVEN",
            "description": "connector between maternal placenta and uterine veins",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._mat_pla,
            "comp_to": self._mat_ut_ven,
            "r_for": self._mat_ut_ven_res / 2.0,
            "r_back": self._mat_ut_ven_res / 2.0,
            "r_k": 0,
        })
        self._mat_pla_ut_uv.init_model(model)
        self._plac_parts.append(self._mat_pla_ut_uv)

        self._pla_exchanger = BloodDiffusor(**{
            "name": "PLAGEX",
            "description": "placenta gas exchanger",
            "model_type": "placenta gas exchanger",
            "is_enabled": True,
            "dependencies": [],
            "comp_blood1": self._mat_pla,
            "comp_blood2":self._fetal_pla,
            "dif_co2": self.plac_dco2,
            "dif_o2": self.plac_do2
        })
        self._pla_exchanger.init_model(model)
        self._plac_parts.append(self._pla_exchanger)


    


    

