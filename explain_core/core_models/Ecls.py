import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodResistor import BloodResistor
from explain_core.core_models.BloodPump import BloodPump
from explain_core.core_models.GasExchanger import GasExchanger
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasResistor import GasResistor
from explain_core.functions.TubeResistance import get_ettube_resistance
from explain_core.functions.GasComposition import set_gas_composition

class Ecls(BaseModel):
    # define the independent parameters
    mode: int = 0                   # 0 = centrifugal pump, 1 = roller
    p_atm: float = 760              # atmospheric pressure
    drainage_site: str = "RA"       # site from where the blood is drained
    return_site: str = "AAR"        # site to which the blood is returned
    rpm: float = 0                  # pump no of rotations per minute
    fio2_gas: float = 0.205         # fraction of inspired air going into the ecls oxygenator
    co2_flow_gas: float = 10        # amount of co2 in ml/min provided to the oxygenator
    temp_gas: float = 20.0          # temperature of the gas flow
    humidity_gas: float = 0.5       # humidity of the gas flow
    sweep_gas: float = 1.5          # sweep gas of the oxygenator
    bloodDensity = 1060             # kg * m-3
    gravity = 9.81                  # m * s-2
    viscosity = 5.5                 # cP

    
    drainage_cannula_diameter: float = 0.004
    drainage_cannula_length: float = 0.11
    return_cannula_diameter: float = 0.0033
    return_cannula_length: float = 0.11

    tubing_diameter: float = 0.00635    # diameter of the ecls tubing in meters
    tubing_elastance: float = 5160      # elastance of the ecls tubing
    drainage_tubing_length: float = 1   # total length of the ecls tubing in meters
    return_tubing_length: float = 1     # total length of the ecls tubing out meters
  
    oxy_volume: float = 0.081           # volume of the oxygenator in liters
    oxy_elastance:float = 25000
    oxy_do2: float = 0              # diffusion constant for o2 of the oxygenator
    oxy_dco2: float = 0             # diffusion constant for co2 of the oxygenator

    pump_volume: float = 0.014
    pump_elastance: float = 25000

    # independent parameters
    fico2_air: float = 0.000392     # fraction of co2 of the inspirered 
    fico2_gas: float = 0.000392     # fraction of co2 of the inspirered 
    flow: float = 0                 # resulting or desired (depending on mode) ecls flow in l/min
    pre_oxy_pres:float = 0          # pre oxygenator pressure
    post_oxy_pres: float = 0        # post oxygenator pressure
    oxy_flux_o2: float = 0          # o2 flux across the oxygenator
    oxy_flux_co2: float = 0         # co2 flux across the oxygenator
    gas_flow:float = 0.0            # monitored gas flow
    tubing_in_volume:float = 0.0    # tubing in volume
    tubing_out_volume:float = 0.0   # tubing out volume

    # ecls parts
    _ecls_parts = []                # define a list holding all ecls system parts

    _drainage_site = {}             # reference to the model blood capacitance from where the blood is drained
    _tubing_in = {}                 # blood containing ecls tubing between drainage site and the pump
    _oxy = {}                       # blood in the oxygenator
    _pump = {}                      # ecls pump
    _tubing_out = {}                     # blood containing ecls tubing between oxygenator and the return site
    _return_site = {}               # reference to the model blood capacitance to where the blood is pumped

    _drainage_site_tubing_in = {}   # resistor connecting the drainage site to the ecls tubing
    _tubing_in_pump = {}            # resistor connecting the ecls tubing to the pump
    _pump_oxy = {}                  # resistor connecting the pump to the oxygenator
    _oxy_tubing_out = {}            # resistor connecting the oxygenator to the tubing out
    _tubing_out_return_site = {}    # resistor connecting the return site to the ecls tubing
 
    _exchanger = {}                 # exchanger between gas and blood of the oxygenator

    _oxy_gas = {}                   # oxygenator gas capacitance
    _oxy_gas_in = {}                # gas capacitance holding the air going into the oxygenator
    _oxy_gas_out = {}               # gas capacitance where the air is going into after the oxugenator
    _oxy_gas_in_valve = {}          # gas resistor between oxy_in and oxy
    _oxy_gas_out_valve = {}         # gas resistor between oxy and oxy_gas_out    

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)
      
        # build the ecls system
        self.build_ecls(model)

        # print(self._ecls_parts)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def switch_ecls(self, state): 
        pass

    def calc_model(self) -> None:
        # calculate the gas valve controlling the sweep gas
        co2_ls = (self.co2_flow_gas / 1000.0 / 60.0)    # in l/s    = co2 flow
        sg_ls: float = (self.sweep_gas / 60.0) + co2_ls # in l/s    = sweep gas flow
        r:float = (self._oxy_gas_in.pres - self._oxy_gas_out.pres) / (sg_ls + co2_ls)

        # calculate the fico2 of the sweep gas source assuming dry gas
        fico2_sg = 0.000392 * (1.0 - self.fio2_gas) / (1.0 - 0.205)

        # calculate the total fico2 of the source gas (so with the co2 flow included)
        self.fico2_gas = (co2_ls / (sg_ls + co2_ls)) + fico2_sg

        # calculate the gas composition of gas source
        set_gas_composition(self._oxy_gas_in, self.fio2_gas, self.temp_gas, self.humidity_gas, self.fico2_gas)

        # set the resistance of the gasflow valve depending of the sweep gas
        self._oxy_gas_in_valve.r_for = r - 25.0
        self._oxy_gas_in_valve.no_back_flow = True

        # set the out valve resistance to low
        self._oxy_gas_out_valve.r_for = 25
        self._oxy_gas_out_valve.no_back_flow = True

        # monitor the sweep gas flow
        self.gas_flow = self._oxy_gas_in_valve.flow * 60.0

        # do the model step calculations of the ecls system
        for item in self._ecls_parts:
            item.step_model()

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
        set_gas_composition(self._oxy_gas_in, self.fio2_gas, self.temp_gas, self.humidity_gas, self.fico2_gas)
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
        set_gas_composition(self._oxy_gas, self.fio2_gas, self.temp_gas, self.humidity_gas, self.fico2_gas)
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
        set_gas_composition(self._oxy_gas_out, self.fio2_gas, self.temp_gas, self.humidity_gas, self.fico2_air)
        # add a reference the the ecls_parts object
        self._ecls_parts.append(self._oxy_gas_out)

        # gas connectors
        self._oxy_gas_in_valve = GasResistor(**{
            "name": "OXYGASINVALVE",
            "description": "valve between the gas source and the gas capacitance of the oxygenator",
            "model_type": "GasResistor",
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

        self._oxy_gas_out_valve = GasResistor(**{
            "name": "OXYGASOUTVALVE",
            "description": "valve between the gas outlet and the gas capacitance of the oxygenator",
            "model_type": "GasResistor",
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
        self._drainage_site = model.models[self.drainage_site]
        self._ecls_parts.append(self._drainage_site)
        
        # get a reference to the return site (= already initialized through main model)
        self._return_site = model.models[self.return_site]
        self._ecls_parts.append(self._return_site)

        # define the tubing in blood capacitance
        self.tubing_in_volume = math.pi * math.pow(self.tubing_diameter / 2, 2) * self.drainage_tubing_length * 1000
        self._tubing_in = BloodCapacitance(**{
            "name": "ECLSTUBINGIN",
            "description": "ecls tubing between drainage site and pump",
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
        self._tubing_in.aboxy = self._drainage_site.aboxy.copy()
        self._tubing_in.solutes = self._drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._tubing_in)

        # define the tubing out blood capacitance
        self.tubing_out_volume = math.pi * math.pow(self.tubing_diameter / 2, 2) * self.return_tubing_length * 1000
        self._tubing_out = BloodCapacitance(**{
            "name": "ECLSTUBINGOUT",
            "description": "ecls tubing between return site and oxygenator",
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
        self._tubing_out.aboxy = self._drainage_site.aboxy.copy()
        self._tubing_out.solutes = self._drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._tubing_out)

        # define the oxygenator
        self._oxy = BloodCapacitance(**{
            "name": "ECLSOXY",
            "description": "ecls oxygenator",
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
        self._oxy.aboxy = self._drainage_site.aboxy.copy()
        self._oxy.solutes = self._drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._oxy)

        # drainage cannula resistance


        # # return cannula resistance



        # define the blood pump
        self._pump = BloodPump(**{
            "name": "ECLSPUMP",
            "description": "ecls pump",
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
        # initialize component
        self._pump.init_model(model)
        # copy the blood composition of the drainage site as starting point
        self._pump.aboxy = self._drainage_site.aboxy.copy()
        self._pump.solutes = self._drainage_site.solutes.copy()
        # add to the components
        self._ecls_parts.append(self._pump)
