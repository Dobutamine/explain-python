import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Resistor import Resistor
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodPump import BloodPump
from explain_core.core_models.GasExchanger import GasExchanger
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.functions.GasComposition import set_gas_composition
from explain_core.functions.BloodComposition import set_blood_composition

class Ecls(BaseModel):
    # define the independent parameters
    ecls_running: bool = False                # determines whether the artificial whomb is running or not
    mode: int = 0                           # 0 = centrifugal pump, 1 = roller
    p_atm: float = 760                      # atmospheric pressure
    drainage_site: str = "RA"               # site from where the blood is drained
    return_site: str = "AAR"               # site to which the blood is returned
    pump_rpm: float = 0                     # pump no of rotations per minute
    fico2_air: float = 0.000392             # fraction of co2 of the outside air
    oxy_fio2: float = 0.205                 # fraction of inspired air going into the ecls oxygenator
    oxy_co2_flow: float = 10                # amount of co2 in ml/min provided to the oxygenator
    oxy_temp_gas: float = 20.0              # temperature of the gas flow
    oxy_humidity_gas: float = 0.5           # humidity of the gas flow
    oxy_sweep_gas: float = 1.5              # sweep gas of the oxygenator
    blood_viscosity = 5.5                   # viscosity of the blood in cP
    drainage_cannula_diameter: float = 4    # diameter of the drainage cannula in mm
    drainage_cannula_length: float = 10.0   # length of the drainage cannula in mm
    return_cannula_diameter: float = 3.3    # diameter of the return cannula in mm
    return_cannula_length: float = 10.0     # length of the return cannula in mm
    clamp: bool = True                      # is there a clamp on the tubing?

    tubing_diameter: float = 6.35           # diameter of the ecls tubing in meters
    tubing_elastance: float = 5160          # elastance of the ecls tubing
    drainage_tubing_length: float = 100     # total length of the ecls drainage tubing in mm
    return_tubing_length: float = 100       # total length of the ecls return tubing out mm
    oxy_volume: float = 0.081               # volume of the oxygenator in liters
    oxy_elastance:float = 25000             # elastance of the oxygenator mmhg / l
    oxy_do2: float = 0.001                  # diffusion constant for o2 of the oxygenator
    oxy_dco2: float = 0.001                 # diffusion constant for co2 of the oxygenator
    pump_volume: float = 0.014              # volume of the ecls pump
    pump_elastance: float = 25000           # elastance of the ecls pump

    # dependent parameters
    fico2_gas: float = 0.000392             # fraction of co2 of the inspired air
    blood_flow: float = 0                   # resulting or desired (depending on mode) ecls flow in l/min
    ven_pres: float = 0.0                   # venous inlet pressure
    pre_oxy_pres:float = 0                  # pre oxygenator pressure
    post_oxy_pres: float = 0                # post oxygenator pressure
    oxy_flux_o2: float = 0                  # o2 flux across the oxygenator
    oxy_flux_co2: float = 0                 # co2 flux across the oxygenator
    gas_flow:float = 0.0                    # monitored gas flow
    tubing_in_volume:float = 0.0            # tubing in volume
    tubing_out_volume:float = 0.0           # tubing out volume
    ph_pre:float = 0.0                      # pre-oxy ph
    so2_pre:float = 0.0                     # pre-oxy o2 saturation
    po2_pre:float = 0.0                     # pre-oxy po2 
    pco2_pre:float = 0.0                    # pre-oxy pco2
    hco3_pre:float = 0.0                    # pre-oxy hco3
    be_pre:float = 0.0                      # pre-oxy be
    ph_post:float = 0.0                     # post-oxy ph
    so2_post:float = 0.0                    # post-oxy o2 saturation
    po2_post:float = 0.0                    # post-oxy po2 
    pco2_post:float = 0.0                   # post-oxy pco2
    hco3_post:float = 0.0                   # post-oxy hco3
    be_post:float = 0.0                     # post-oxy be
    hemoglobin:float = 0.0                  # ecls hemoglobin level in mmol/l

    # ecls parts
    _ecls_parts = []                          # define a list holding all ecls system parts
    _tubing_in: BloodCapacitance = {}       # blood containing ecls tubing between drainage site and the pump
    _oxy: BloodCapacitance = {}             # blood in the oxygenator
    _pump: BloodPump = {}                   # ecls pump
    _tubing_out: BloodCapacitance = {}      # blood containing ecls tubing between oxygenator and the return site

    _drainage_tubing_in: Resistor = {}      # resistor connecting the umbilical arteries to the ecls tubing
    _tubing_in_pump: Resistor = {}          # resistor connecting the ecls tubing to the pump
    _pump_oxy: Resistor = {}                # resistor connecting the pump to the oxygenator
    _oxy_tubing_out: Resistor = {}          # resistor connecting the oxygenator to the ecls tubing
    _tubing_out_return: Resistor = {}           # resistor connecting the ecls tubing to the umbilical veins
    _exchanger: GasExchanger = {}           # exchanger between gas and blood of the oxygenator

    _oxy_gas: GasCapacitance = {}           # oxygenator gas capacitance
    _oxy_gas_in: GasCapacitance = {}        # gas capacitance holding the air going into the oxygenator
    _oxy_gas_out: GasCapacitance = {}       # gas capacitance where the air is going into after the oxugenator
    _oxy_gas_in_valve: Resistor = {}        # gas resistor between oxy_in and oxy
    _oxy_gas_out_valve: Resistor = {}       # gas resistor between oxy and oxy_gas_out

    _bg_eval_interval: float = 1.0          # interval at which the bloodgas composition is calculated
    _bg_eval_counter:float = 0.0            # counter for the bloodgas composition 

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)
      
        # build the ecls system
        self.build_ecls(model)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def switch_ecls(self, state): 
        self.ecls_running = state

    def set_fio2(self, new_fio2):
        self.oxy_fio2 = new_fio2

    def set_sweepgas(self, new_sweep):
        self.oxy_sweep_gas = new_sweep
    
    def set_co2_flow(self, new_co2_flow):
        self.oxy_co2_flow = new_co2_flow

    def set_pump_rpm(self, new_rpm):
        self.pump_rpm = new_rpm

    def set_clamp(self, state):
        if state:
            self._drainage_tubing_in.close()
            self._tubing_out_return.close()
        else:
            self._drainage_tubing_in.open()
            self._tubing_out_return.open()

    def calc_model(self) -> None:
        if self.ecls_running:
            # calculate the gas valve controlling the sweep gas
            co2_ls = (self.oxy_co2_flow / 1000.0 / 60.0)    # in l/s    = co2 flow
            sg_ls: float = (self.oxy_sweep_gas / 60.0) + co2_ls # in l/s    = sweep gas flow
            r:float = (self._oxy_gas_in.pres - self._oxy_gas_out.pres) / (sg_ls + co2_ls)

            # calculate the fico2 of the sweep gas source assuming dry gas
            fico2_sg = 0.000392 * (1.0 - self.oxy_fio2) / (1.0 - 0.205)
        
            # calculate the total fico2 of the source gas (so with the co2 flow included)
            self.fico2_gas = (co2_ls / (sg_ls + co2_ls)) + fico2_sg

            # calculate the gas composition of gas source
            set_gas_composition(self._oxy_gas_in, self.oxy_fio2, self.oxy_temp_gas, self.oxy_humidity_gas, self.fico2_gas)

            # set the resistance of the gasflow valve depending of the sweep gas
            self._oxy_gas_in_valve.r_for = r - 25.0
            self._oxy_gas_in_valve.no_back_flow = True

            # set the rpm
            self._pump.pump_rpm = self.pump_rpm

            # set the out valve resistance to low
            self._oxy_gas_out_valve.r_for = 25
            self._oxy_gas_out_valve.no_back_flow = True

            # monitor the sweep gas flow
            self.gas_flow = self._oxy_gas_in_valve.flow * 60.0
            self.blood_flow = self._tubing_out_return.flow * 60.0

            # get the pressures
            self.ven_pres = self._tubing_in.pres
            self.pre_oxy_pres = self._pump.pres
            self.post_oxy_pres = self._tubing_out.pres

            # get the volumes
            self.tubing_in_volume = self._tubing_in.vol + self._tubing_in.u_vol
            self.tubing_out_volume = self._tubing_out.vol + self._tubing_out.u_vol

            # other measurements
            self.hemoglobin = self._tubing_in.aboxy['hemoglobin']

            # do the model step calculations of the ecls system
            for item in self._ecls_parts:
                item.step_model()

            # evaluate the bloodgasses at lower intervals for performance reasons
            if self._bg_eval_counter > self._bg_eval_interval:
                self._bg_eval_counter = 0.0
                # calculate the bloodgasses of the pre and oxy
                set_blood_composition(self._tubing_in)

                self.ph_pre = self._tubing_in.aboxy['ph']
                self.so2_pre = self._tubing_in.aboxy['so2']
                self.po2_pre = self._tubing_in.aboxy['po2']
                self.pco2_pre = self._tubing_in.aboxy['pco2']
                self.hco3_pre = self._tubing_in.aboxy['hco3']
                self.be_pre = self._tubing_in.aboxy['be']

                self.ph_post = self._oxy.aboxy['ph']
                self.so2_post = self._oxy.aboxy['so2']
                self.po2_post = self._oxy.aboxy['po2']
                self.pco2_post = self._oxy.aboxy['pco2']
                self.hco3_post = self._oxy.aboxy['hco3']
                self.be_post = self._oxy.aboxy['be']
            
            self._bg_eval_counter += self._t

    def build_ecls(self, model) -> None:
        # clear the ecls system parts
        self._ecls_parts = []

        # build the ecls system using the gas capacitance model

        # gas source
        self._oxy_gas_in = GasCapacitance(**{
            "name": "OXYGASIN",
            "description": "oxygenator gas source",
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
        # initialize the oxygenator gas source
        self._oxy_gas_in.init_model(model)
        # calculate the pressure 
        self._oxy_gas_in.calc_model()
        # set the gas composition of the reservoir
        set_gas_composition(self._oxy_gas_in, self.oxy_fio2, self.oxy_temp_gas, self.oxy_humidity_gas, self.fico2_gas)
        # # add a reference the the ecls_parts object
        self._ecls_parts.append(self._oxy_gas_in)

        # gas part of the oxygenator
        self._oxy_gas = GasCapacitance(**{
            "name": "OXYGAS",
            "description": "oxygenator gas reservoir",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": 0.5,
            "u_vol": 0.5,
            "el_base": 25000.0,
            "el_k": 0,
            "pres_atm": self.p_atm
        })
        # initialize the gas part of the oxygenator
        self._oxy_gas.init_model(model)
        # calculate the pressure 
        self._oxy_gas.calc_model()
        # set the gas composition of the gas part of the oxygenator
        set_gas_composition(self._oxy_gas, self.oxy_fio2, self.oxy_temp_gas, self.oxy_humidity_gas, self.fico2_gas)
        # add a reference the the ecls_parts object
        self._ecls_parts.append(self._oxy_gas)

        # gas out
        self._oxy_gas_out = GasCapacitance(**{
            "name": "OXYGASOUT",
            "description": "oxygenator gas outlet",
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
        # initialize the oxygenator gas out
        self._oxy_gas_out.init_model(model)
        # calculate the pressure 
        self._oxy_gas_out.calc_model()
        # set the gas composition of the gas out
        set_gas_composition(self._oxy_gas_out, self.oxy_fio2, self.oxy_temp_gas, self.oxy_humidity_gas, self.fico2_air)
        # add a reference the the ecls_parts object
        self._ecls_parts.append(self._oxy_gas_out)

        # gas connectors
        self._oxy_gas_in_valve = Resistor(**{
            "name": "OXYGASINVALVE",
            "description": "valve between the gas source and the gas capacitance of the oxygenator",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": True,
            "comp_from": self._oxy_gas_in,
            "comp_to": self._oxy_gas,
            "r_for": 30000,
            "r_back": 1000000,
            "r_k": 0,
        })
        self._oxy_gas_in_valve.init_model(model)
        self._ecls_parts.append(self._oxy_gas_in_valve)

        self._oxy_gas_out_valve = Resistor(**{
            "name": "OXYGASOUTVALVE",
            "description": "valve between the gas outlet and the gas capacitance of the oxygenator",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": True,
            "comp_from": self._oxy_gas,
            "comp_to": self._oxy_gas_out,
            "r_for": 25,
            "r_back": 25,
            "r_k": 0,
        })
        self._oxy_gas_out_valve.init_model(model)
        self._ecls_parts.append(self._oxy_gas_out_valve)

        # get a reference to the drainage site (= already initialized though main model)
        _drainage_site = model.models[self.drainage_site]
        
        # get a reference to the return site (= already initialized through main model)
        _return_site = model.models[self.return_site]

        # define the tubing in blood capacitance
        self.tubing_in_volume = math.pi * math.pow(self.tubing_diameter / 2, 2) * self.drainage_tubing_length * 1000
        self._tubing_in = BloodCapacitance(**{
            "name": "ECLS_TUBINGIN",
            "description": "ecls tubing in",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.tubing_in_volume,
            "u_vol": self.tubing_in_volume,
            "el_base": self.tubing_elastance,
            "el_k": 0
        })
        # initialize component
        self._tubing_in.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._tubing_in.aboxy = _drainage_site.aboxy.copy()
        self._tubing_in.solutes = _drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._tubing_in)

        # define the tubing out blood capacitance
        self.tubing_out_volume = math.pi * math.pow(self.tubing_diameter / 2, 2) * self.return_tubing_length * 1000
        self._tubing_out = BloodCapacitance(**{
            "name": "ECLS_TUBINGOUT",
            "description": "ecls tubing out",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.tubing_out_volume,
            "u_vol": self.tubing_out_volume,
            "el_base": self.tubing_elastance,
            "el_k": 0
        })
        # initialize component
        self._tubing_out.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._tubing_out.aboxy = _drainage_site.aboxy.copy()
        self._tubing_out.solutes = _drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._tubing_out)

        # define the oxygenator
        self._oxy = BloodCapacitance(**{
            "name": "ECLS_OXY_BLOOD",
            "description": "ecls blood oxygenator",
            "model_type": "BloodCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.oxy_volume,
            "u_vol": self.oxy_volume,
            "el_base": self.oxy_elastance,
            "el_k": 0
        })
        # initialize component
        self._oxy.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._oxy.aboxy = _drainage_site.aboxy.copy()
        self._oxy.solutes = _drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._oxy)

        # define the blood pump
        self._pump = BloodPump(**{
            "name": "ECLS_PUMP",
            "description": "ecls blood pump",
            "model_type": "BloodPump",
            "is_enabled": True,
            "dependencies": [],
            "vol": self.pump_volume,
            "u_vol": self.pump_volume,
            "el_base": self.pump_elastance,
            "el_k": 0,
            "pump_mode": 0,
            "pump_rpm": 0,
            "inlet": "",
            "outlet": ""
        })
        # we cannot intialized the pump yet as it depends on the other components
    
        # drainage cannula resistance
        self._drainage_tubing_in = Resistor(**{
            "name": "ECLS_DRAINAGE_TUBINGIN",
            "description": "connector between drainage site and tubing in",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": _drainage_site,
            "comp_to": self._tubing_in,
            "diameter": self.drainage_cannula_diameter,
            "length": self.drainage_cannula_length,
            "r_k": 0,
        })
        self._drainage_tubing_in.init_model(model)
        self._ecls_parts.append(self._drainage_tubing_in)

        self._tubing_in_pump = Resistor(**{
            "name": "ECLS_TUBINGIN_PUMP",
            "description": "connector tubing in and the pump",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._tubing_in,
            "comp_to": self._pump,
            "diameter":self.tubing_diameter,
            "length":self.drainage_tubing_length,
            "r_k": 0,
        })
        self._tubing_in_pump.init_model(model)
        self._ecls_parts.append(self._tubing_in_pump)

        self._pump_oxy = Resistor(**{
            "name": "ECLS_PUMP_OXY",
            "description": "connector between pump and oxygenator",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._pump,
            "comp_to": self._oxy,
            "r_for": 15,
            "r_back": 15,
            "r_k": 0,
        })
        self._pump_oxy.init_model(model)
        self._ecls_parts.append(self._pump_oxy)

        self._oxy_tubing_out = Resistor(**{
            "name": "ECLS_OXY_TUBINGOUT",
            "description": "connector between oxygenator and tubing out",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._oxy,
            "comp_to": self._tubing_out,
            "diameter": self.tubing_diameter,
            "length": self.return_tubing_length,
            "r_k": 0,
        })
        self._oxy_tubing_out.init_model(model)
        self._ecls_parts.append(self._oxy_tubing_out)

        self._tubing_out_return = Resistor(**{
            "name": "ECLS_TUBINGOUT_RETURN",
            "description": "connector between tubing out and return site",
            "model_type": "Resistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._tubing_out,
            "comp_to": _return_site,
            "diameter": self.return_cannula_diameter,
            "length": self.return_cannula_length,
            "r_k": 0,
        })
        self._tubing_out_return.init_model(model)
        self._ecls_parts.append(self._tubing_out_return)


        self._exchanger = GasExchanger(**{
            "name": "ECLS_GASEX",
            "description": "gasexchanger",
            "model_type": "GasExchanger",
            "is_enabled": True,
            "dependencies": [],
            "comp_blood": self._oxy,
            "comp_gas":self._oxy_gas,
            "dif_co2": self.oxy_dco2,
            "dif_o2": self.oxy_do2
        })
        self._exchanger.init_model(model)
        self._ecls_parts.append(self._exchanger)

        # initialize the pump component
        self._pump.init_model(model)
        # connect the pump
        self._pump.connect_pump(self._tubing_in_pump, self._pump_oxy)
        # copy the blood composition of the drainage site as starting point
        self._pump.aboxy = _drainage_site.aboxy.copy()
        self._pump.solutes = _drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._pump)

        # clamp the tubing
        self.set_clamp(True)