import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasResistor import GasResistor
from explain_core.functions.TubeResistance import get_ettube_resistance
from explain_core.functions.GasComposition import set_gas_composition

class Ventilator(BaseModel):
    # independent parameters
    p_atm: float = 760
    humidity: float = 1.0
    temp:float = 37.0
    fio2: float = 0.205
    ettube_diameter: float = 0.0035
    ettube_length: float = 0.11
    vent_mode: str = "PRVC"
    vent_rate: float =  40.0
    insp_time: float = 0.4
    insp_flow: float = 10.0
    exp_flow: float = 3.0
    pip_cmh2o: float = 10.3
    pip_cmh2o_max: float = 20.0
    peep_cmh2o: float = 3.65
    tidal_volume: float = 0.0165
    trigger_volume_perc: float = 6

    # dependent parameters
    pres: float = 0.0
    flow: float = 0.0
    vol: float = 0.0
    compliance: float = 0.0
    elastance: float = 0.0
    resistance: float = 0.0
    co2:float = 0.0
    etco2: float = 0.0
    exp_time: float = 0.8
    insp_tidal_volume: float = 0.0
    exp_tidal_volume: float = 0.0
    minute_volume: float = 0.0
    trigger_volume: float = 0.0


    # ventilator parts
    _vent_parts = []
    _ventin: GasCapacitance = {}
    _ventout: GasCapacitance = {}
    _insp_valve: GasResistor = {}
    _ventcircuit: GasCapacitance = {}
    _exp_valve: GasResistor = {}
    _ettube: GasResistor = {}

    # local parameters
    _insp_time_counter: float = 0.0
    _exp_time_counter: float = 0.0
    _inspiration: bool = True
    _expiration: bool = False
    _insp_tidal_volume_counter: float = 0.0
    _exp_tidal_volume_counter: float = 0.0
    _trigger_volume_counter: float = 0.0
    _tube_resistance: float = 25.0
    _max_flow: float = 0.0
    _pres_reached: bool = False
    _pip: float = 0.0
    _pip_max:float = 0.0
    _peep: float = 0.0
    _tv_tolerance: float = 0.0005       # tidal volume tolerance for volume control in l
    _triggered_breath: bool = False

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # build the ventilator
        self.build_ventilator(model)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized
       
    def switch_ventilator(self, state):
        if state:
            self._model.models["MOUTH_DS"].no_flow = True
            self._model.models["Breathing"].is_intubated = True
            self._ettube.no_flow = False
            self.is_enabled = True
        else:
            self._model.models["MOUTH_DS"].no_flow = False
            self._model.models["Breathing"].is_intubated = False
            self._ettube.no_flow = True
            self.is_enabled = False

    def set_ventilator_pc(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0):
        pass

    def set_ventilator_prvc(self, pip_max=18.0, peep=4.0, rate=40.0, tv=15.0, t_in=0.4, insp_flow=10.0):
        pass

    def calc_model(self):

        # convert settings to from cmH2o
        self._pip = self.pip_cmh2o / 1.35951
        self._pip_max = self.pip_cmh2o_max / 1.35951
        self._peep = self.peep_cmh2o / 1.35951

        # check for triggered breath
        self.trigger_volume = (self.tidal_volume / 100) * self.trigger_volume_perc
        if self._trigger_volume_counter > self.trigger_volume and not self._triggered_breath:
            self._triggered_breath = True
            # reset the trigger volume counter
            self._trigger_volume_counter = 0.0

        if not self._triggered_breath and not self._inspiration and self._ettube.flow > 0.0:
            self._trigger_volume_counter += self._ettube.flow * self._t

        # calculate the expiration time
        self.exp_time = (60.0 / self.vent_rate) - self.insp_time

        # has the inspiration time elapsed?
        if self._insp_time_counter > self.insp_time:
            self._insp_time_counter = 0.0
            self._inspiration = False
            self._expiration = True
            self.vol = 0.0
            self._triggered_breath = False
           
        # has the expiration time elapsed?
        if self._exp_time_counter > self.exp_time:
            self._exp_time_counter = 0.0
            self._inspiration = True
            self._expiration = False
            # reset the volume counters
            self.exp_tidal_volume = -self._exp_tidal_volume_counter
            print(self.exp_tidal_volume)
            if self.exp_tidal_volume > 0:
                self.elastance = (self._pip - self._peep) / self.exp_tidal_volume     # in mmHg/l
                self.compliance = 1 / (((self._pip - self._peep) * 1.35951) / (self.exp_tidal_volume * 1000.0)) # in ml/cmH2O
            self._exp_tidal_volume_counter = 0.0
            # check whether the ventilator is in PRVC mode
            if self.vent_mode == "PRVC":
                self.pressure_regulated_volume_control()
            
        
        # inspiration
        if self._inspiration:
            self._insp_time_counter += self._t

        if self._expiration:
            self._exp_time_counter += self._t

        # call the correct ventilation mode
        self.pressure_control()
        

        # store the values
        self.pres = (self._ventcircuit.pres - self.p_atm) * 1.35951     # in cmH2O
        self.flow = self._ettube.flow * 60.0                            # in l/min
        self.vol += -self._ettube.flow * 1000 * self._t                 # in ml
        self.co2 = self._model.models["DS"].pco2                        # in mmHg

        for item in self._vent_parts:
            item.step_model()


    def pressure_control(self):
        if self._inspiration:
            # close the expiration valve and open the inspiration valve
            self._exp_valve.no_flow = True
            self._insp_valve.no_flow = False

            # prevent back flow to the ventilator
            self._insp_valve.no_back_flow = True

            # set the resistance of the inspiration valve
            self._insp_valve.r_for = (self._ventin.pres + self._pip - self.p_atm - self._peep) / (self.insp_flow / 60.0)

            # guard the inspiratory pressure
            if self._ventcircuit.pres > self._pip + self.p_atm:
                self._insp_valve.no_flow = True   
                self._insp_valve.r_for_factor = 1.0 
                if self._insp_valve.flow > 0 and not self._pres_reached:
                    self.resistance = (self._ventcircuit.pres - self.p_atm) / self._insp_valve.flow
                    self._pres_reached = True
    
        if self._expiration:
            self._pres_reached = False
            # close the inspiration valve and open the expiration valve
            self._insp_valve.no_flow = True

            self._exp_valve.no_flow = False
            self._exp_valve.no_back_flow = True

            # set the resistance of the expiration valve to and calculate the pressure in the expiration block
            self._exp_valve.r_for = 10
            self._ventout.vol = (self._peep / self._ventout.el_base + self._ventout.u_vol)

            # calculate the expiratory tidal volume
            if (self._ettube.flow < 0):
                self._exp_tidal_volume_counter += self._ettube.flow * self._t


    def pressure_regulated_volume_control(self) -> None:
        if self.exp_tidal_volume < self.tidal_volume - self._tv_tolerance:
            self.pip_cmh2o += 0.5
            if self.pip_cmh2o > self.pip_cmh2o_max:
                self.pip_cmh2o = self.pip_cmh2o_max
        
        if self.exp_tidal_volume > self.tidal_volume + self._tv_tolerance:
            self.pip_cmh2o -= 0.5
            if self.pip_cmh2o < self.peep_cmh2o + 2.0:
                self.pip_cmh2o = self.peep_cmh2o + 2.0


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
            "vol": 5.4,
            "u_vol": 5.0,
            "el_base": 1000.0,
            "el_k": 0,
            "pres_atm": self.p_atm
        })
       
        # initialize the internal reservoir of the ventilator
        self._ventin.init_model(model)
        
        # calculate the pressure 
        self._ventin.calc_model()
        
        # set the gas composition of the reservoir
        set_gas_composition(self._ventin, self.fio2, self.temp, self.humidity)
        
        # add a reference the the vent_parts object
        self._vent_parts.append(self._ventin)
        
        # 1.6 m inspiratory -> volume 0.131 l -> elastance = 565 mmHg/l
        # 1.6 m expiratory  -> volume 0.131 l -> elastance = 565 mmHg/l
        self._ventcircuit = GasCapacitance(**{
            "name": "VENTCIRCUIT",
            "description": "ventilator circuit",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": 0.262,
            "u_vol": 0.262,
            "el_base": 565 * 2.0,
            "el_k": 0
        })
        # initialize the internal reservoir of the ventilator
        self._ventcircuit.init_model(model)
        # calculate the pressure 
        self._ventcircuit.calc_model()
        # set the gas composition of the reservoir
        set_gas_composition(self._ventcircuit, self.fio2, self.temp, self.humidity)
        # add a reference the the vent_parts object
        self._vent_parts.append(self._ventcircuit)

        # build the mechanical ventilator using the gas capacitance model
        self._ventout = GasCapacitance(**{
            "name": "VENTOUT",
            "description": "ventilator expiration reservoir",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": True,
            "vol": 5.0,
            "u_vol": 5.0,
            "el_base": 1000.0,
            "el_k": 0,
            "pres_atm": self.p_atm
        })
        # initialize the internal reservoir of the ventilator
        self._ventout.init_model(model)
        # calculate the pressure 
        self._ventout.calc_model()
         # set the gas composition of the reservoir
        set_gas_composition(self._ventout, self.fio2, self.temp, self.humidity)
        # add a reference the the vent_parts object
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
            "comp_from": self._ventin,
            "comp_to": self._ventcircuit,
            "r_for": 30000,
            "r_back": 1000000,
            "r_k": 0,
        })
        self._insp_valve.init_model(model)
        self._vent_parts.append(self._insp_valve)

        # calculate the en tracheal tube resistance
        self._tube_resistance = get_ettube_resistance(self.ettube_diameter, self.insp_flow)

        self._ettube = GasResistor(**{
            "name": "ETTUBE",
            "description": "endotracheal tube",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": True,
            "no_back_flow": False,
            "comp_from": self._ventcircuit,
            "comp_to": self._model.models['DS'],
            "r_for": self._tube_resistance,
            "r_back": self._tube_resistance,
            "r_k": 0,
        })
        self._ettube.init_model(model)
        self._vent_parts.append(self._ettube)

        self._exp_valve = GasResistor(**{
            "name": "EXPVALVE",
            "description": "expiration valve of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._ventcircuit,
            "comp_to": self._ventout,
            "r_for": 300000,
            "r_back": 300000,
            "r_k": 0,
        })
        self._exp_valve.init_model(model)
        self._vent_parts.append(self._exp_valve)