import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodResistor import BloodResistor
from explain_core.core_models.BloodPump import BloodPump
from explain_core.core_models.GasExchanger import GasExchanger
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasResistor import GasResistor

class Ecls(BaseModel):
    # define the independent parameters
    mode: int = 0                   # 0 = centrifugal pump, 1 = roller
    drainage_site: str = "RA"       # site from where the blood is drained
    return_site: str = "AAR"        # site to which the blood is returned
    rpm: float = 0                  # pump no of rotations per minute
    fio2_lung: float = 0.40         # fraction of inspired air going into the ecls oxygenator
    co2_lung: float = 40            # amount of co2 in ml/min provided to the oxygenator
    sweep_gas: float = 8            # sweep gas of the oxygenator
    tubing_diameter: float = 0      # diameter of the ecls tubing in mm
    tubing_length: float = 0        # total length of the ecls tubing in meters
    oxy_volume: float = 0           # volume of the oxygenator in liters
    oxy_do2: float = 0              # diffusion constant for o2 of the oxygenator
    oxy_dco2: float = 0             # diffusion constant for co2 of the oxygenator

    # independent parameters
    flow: float = 0                 # resulting or desired (depending on mode) ecls flow in l/min
    pre_oxy_pres:float = 0          # pre oxygenator pressure
    post_oxy_pres: float = 0        # post oxygenator pressure
    oxy_flux_o2: float = 0          # o2 flux across the oxygenator
    oxy_flux_co2: float = 0         # co2 flux across the oxygenator

    # ecls parts
    _drainage_comp = {}             # reference to capacitance/time varying elastance from where the blood is drained
    _return_comp = {}               # reference to capacitance/time varying elastance to where to blood is returned
    _pump = {}                      # blood pump
    _ecls_tubing_in = {}            # blood resistor between drainage site and the pump
    _ecls_tubing_pump_oxy = {}      # blood resistor between the pump and the oxygenator
    _ecls_tubing_out = {}           # blood resistor between oxygenator and the return site
    _oxy_blood = {}                 # oxygenator blood capacitance
    _oxy_exchanger = {}             # exchanger between gas and blood of the oxygenator
    _oxy_gas = {}                   # oxygenator gas capacitance
    _oxy_gas_in = {}                # gas capacitance holding the air going into the oxygenator
    _oxy_gas_out = {}               # gas capacitance where the air is going into after the oxugenator
    _oxy_tubing_in = {}             # gas resistor between oxy_in and oxy
    _oxy_tubing_out = {}            # gas resistor between oxy and oxy_gas_out

    def init_model(self, model: object) -> bool:
        super().init_model(model)
        

    def calc_model(self) -> None:
        pass
