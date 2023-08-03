import math
import numpy as np
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasResistor import GasResistor


class Ventilator(BaseModel):
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
    exp_tidal_volume: float = 0.0
    insp_tidal_volume: float = 0.0
    ivr: float = 2200
    hfo_map: float = 10.0
    hfo_freq: float = 10.0
    hfo_amplitude: float = 10.0
    hfo_pres: float = 0.0

    # dependent parameters
    vent_flow: float = 0.0
    vent_pres: float = 0.0
    vent_vol: float = 0.0
    co2: float = 0.0
    etco2: float = 0.0
    exp_time: float = 0.15
    compliance: float = 0.0
    compliance_converted: float = 0.0
    ventin_pres: float = 0.0
    tubingin_pres: float = 0.0
    ettube_pres: float = 0.0
    ds_pres: float = 0.0
    all_pres: float = 0.0
    alr_pres: float = 0.0
    tubingout_pres: float = 0.0
    ventout_pres: float = 0.0
    hfo_module_pres: float = 0.0
    ventout_high_pres: float = 0.0
    ventout_low_pres: float = 0.0
    ventout_mean_pres: float = 0.0

    maw: float = 0.0

    # ventilator parts
    _vent_parts: list = []
    _ventin: GasCapacitance = {}
    _tubingin: GasCapacitance = {}
    _ettube: GasCapacitance = {}
    _tubingout: GasCapacitance = {}
    _ventout: GasCapacitance = {}
    _hfo_module: GasCapacitance = {}
    _insp_valve: GasResistor = {}
    _tubingin_ettube: GasResistor = {}
    _ettube_ds: GasResistor = {}
    _ettube_tubingout: GasResistor = {}
    _exp_valve: GasResistor = {}
    _hfo_valve: GasResistor = {}

    # local parameters
    _gas_constant: float = 62.36367
    _insp_counter: float = 0.0
    _exp_counter: float = 0.0
    _inspiration: bool = True
    _expiration: bool = False
    _exp_volume_counter: float = 0.0
    _insp_volume_counter: float = 0.0
    _peep_reached = False
    _hfo_vol_delta: float = 0.0
    _hfo_mod_vol_delta: float = 0.0
    _hfo_amp_delta: float = 0.0
    _hfo_amp_factor: float = 1.0

    _hfo_timer: float = 0.0
    _maw_counter: float = 0.0
    _tubout_pres: float = []
    _hfo_high_pres: float = 0.0
    _hfo_mean_pres: float = 0.0
    _hfo_low_pres: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # build the ventilator
        self.build_ventilator(model)

    def switch_ventilator(self, state):
        if state:
            self._model.models['Breathing'].breathing_enabled = False
            self._model.models['MOUTH_DS'].no_flow = True
            self._model.models['MOUTH_DS'].is_enabled = False
            self._ettube_ds.no_flow = False
            self._model.update_log("Ventilator on.")
        else:
            self._model.models['Breathing'].breathing_enabled = True
            self._model.models['MOUTH_DS'].no_flow = False
            self._model.models['MOUTH_DS'].is_enabled = True
            self._ettube_ds.no_flow = True
            self._model.update_log("Ventilator off.")

    def set_ventilator_pc(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0):
        self.switch_ventilator(True)
        self.vent_mode = "PC"
        self._hfo_valve.no_flow = True
        self.pip_max = pip * 0.735559
        self.pip = pip * 0.735559
        self.peep = peep * 0.735559
        self.vent_rate = rate
        self.insp_time = t_in
        self.insp_flow = insp_flow

    def set_ventilator_prvc(self, pip_max=18.0, peep=4.0, rate=40.0, tv=15.0, t_in=0.4, insp_flow=10.0):
        self.switch_ventilator(True)
        self.vent_mode = "PRVC"
        self._hfo_valve.no_flow = True
        self.pip_max = pip_max * 0.735559
        self.pip = pip_max * 0.735559
        self.peep = peep * 0.735559
        self.vent_rate = rate
        self.tidal_volume = tv / 1000.0
        self.insp_time = t_in
        self.insp_flow = insp_flow

    def set_ventilator_hfo(self, _map=10.0, freq=10.0, amplitude=10.0, base_flow=7.0):
        self.switch_ventilator(True)
        self._hfo_valve.no_flow = False
        self.vent_mode = "HFO"
        self.hfo_map = _map * 0.735559
        self.hfo_freq = freq
        self.hfo_amplitude = amplitude * 0.735559
        self.hfo_base_flow = base_flow

    def calc_model(self):
        # select the ventilator mode
        if (self.vent_mode == "PC" or self.vent_mode == "PRVC"):
            self.conventional_ventilation()

        if (self.vent_mode == "HFO"):
            self.high_frequency_oscillation()

        # calculate the models
        for mp in self._vent_parts:
            mp.calc_model()

        self.vent_pres = (self._tubingout.pres - 760) * 1.35951

        self.ventin_pres = (self._tubingout.pres - 760) * 1.35951
        self.tubingin_pres = (self._tubingout.pres - 760) * 1.35951
        self.tubingout_pres = (self._tubingout.pres - 760) * 1.35951
        self.ventout_pres = (self._tubingout.pres - 760) * 1.35951
        self.ettube_pres = (self._ettube.pres - 760) * 1.35951
        self.ds_pres = (self._model.models['DS'].pres - 760) * 1.35951
        self.all_pres = (self._model.models['ALL'].pres - 760) * 1.35951
        self.alr_pres = (self._model.models['ALR'].pres - 760) * 1.35951

        if (self._inspiration):
            self.vent_flow = self._tubingin_ettube.flow * 60.0

        if (self._expiration):
            self.vent_flow = -self._ettube_tubingout.flow * 60.0

        self.vent_vol += self._ettube_tubingout.flow * self._t * 1000.0

        self.co2 = self._model.models['DS'].pco2

    def high_frequency_oscillation(self):
        # first we must apply the base flow and the mean airway pressure

        # configure the expiration valve
        self._ventout.vol = ((self.hfo_map / self._ventout.el_base) +
                             self._hfo_vol_delta) + self._ventout.u_vol
        self._exp_valve.no_flow = False
        self._exp_valve.no_back_flow = True
        self._exp_valve.r_for = 15.0

        # configure the inspiration valve
        self._insp_valve.no_flow = False
        self._insp_valve.r_for = (
            self._ventin.pres - self._ventout.pres) / (self.hfo_base_flow / 60.0)
        self._insp_valve.no_back_flow = True

        if (self._hfo_timer < (1.0 / self.hfo_freq) * 0.5):
            self._inspiration = True
            self._expiration = False
            self.hfo_pres = (self.hfo_amplitude + self._hfo_amp_delta) * 0.5 * \
                math.sin(2 * math.pi * self._hfo_timer *
                         self.hfo_freq)

        if (self._hfo_timer >= (1.0 / self.hfo_freq) * 0.5):
            self._inspiration = False
            self._expiration = True
            self.hfo_pres = (self.hfo_amplitude + self._hfo_amp_delta) * 0.5 * \
                math.sin(2 * math.pi * self._hfo_timer *
                         self.hfo_freq)

        # configure the hfo module
        self._hfo_module.vol = (
            ((self.hfo_map + self.hfo_pres) / self._hfo_module.el_base) + self._hfo_mod_vol_delta) + self._hfo_module.u_vol

        # analyze 1 hfo cycle
        if (self._hfo_timer > 1.0 / self.hfo_freq):
            self._hfo_timer = 0.0
            self._hfo_high_pres = np.max(self._tubout_pres)
            self.ventout_high_pres = self._hfo_high_pres * 1.35951
            self._hfo_low_pres = np.min(self._tubout_pres)
            self.ventout_low_pres = self._hfo_low_pres * 1.35951
            self._hfo_mean_pres = np.mean(self._tubout_pres)
            self.ventout_mean_pres = self._hfo_mean_pres * 1.35951
            self.vent_vol = 0.0
            # adjust the expiratory valve settings to hold the mean airway pressure
            if self._hfo_mean_pres > self.hfo_map:
                self._hfo_vol_delta -= 0.0001

            if self._hfo_mean_pres < self.hfo_map:
                self._hfo_vol_delta += 0.0001

            # adjust the amplitude settings to reach the desired amplitude
            if self._hfo_high_pres > (self.hfo_map + (self.hfo_amplitude * 0.5)):
                self._hfo_amp_delta -= 0.5

            if self._hfo_high_pres < (self.hfo_map + (self.hfo_amplitude * 0.5)):
                self._hfo_amp_delta += 0.5

            if self._hfo_low_pres > (self.hfo_map - (self.hfo_amplitude * 0.5)):
                self._hfo_amp_delta += 0.5

            if self._hfo_low_pres < (self.hfo_map - (self.hfo_amplitude * 0.5)):
                self._hfo_amp_delta -= 0.5

            # reset the data for the cycle
            self._tubout_pres = []

        # append the pressure data
        self._tubout_pres.append(self._tubingout.pres - 760.0)

        # increase the hfo timer
        self._hfo_timer += self._t

    def conventional_ventilation(self):
        # calculate the expiration time
        self.exp_time = (60.0 / self.vent_rate) - self.insp_time
        # do the time cycling
        if self._insp_counter > self.insp_time:
            self._inspiration = False
            self._expiration = True
            self._exp_counter = 0
            self._insp_counter = 0
            # report the inspiratory volume
            self.insp_tidal_volume = self._insp_volume_counter
            self._insp_volume_counter = 0.0

        if self._exp_counter > self.exp_time:
            self._expiration = False
            self._inspiration = True
            self._insp_counter = 0
            self._exp_counter = 0
            self.etco2 = self._ettube.co2
            # report the inspiratory volume
            self.exp_tidal_volume = self._exp_volume_counter
            self._exp_volume_counter = 0.0
            self.compliance = self.exp_tidal_volume / \
                (self.pip - self.peep)
            self.compliance_converted = self.compliance * 1000 * 0.73555
            # if PRVC check volume
            if self.vent_mode == "PRVC":
                self.pressure_regulated_volume_control()

        # increase the timers
        if self._inspiration:
            self._insp_counter += self._t

        if self._expiration:
            self._exp_counter += self._t

        self.pressure_control()

    def pressure_regulated_volume_control(self):
        if self.exp_tidal_volume < self.tidal_volume - 0.001:
            self.pip += 0.74
            if (self.pip > self.pip_max):
                self.pip = self.pip_max

        if self.exp_tidal_volume > self.tidal_volume + 0.001:
            self.pip -= 0.74
            if (self.pip < self.peep + 1.5):
                self.pip = self.peep + 1.5

    def pressure_control(self):
        if self._inspiration:
            # open the inspiration valve and calculate the inspiratory valve position depending on the desired flow
            self._insp_valve.no_flow = False
            self._insp_valve.r_for = (
                (self._ventin.pres - 760) / (self.insp_flow / 60.0)) + 500
            self.ivr = self._insp_valve.r_for
            # self._insp_valve.r_for = self.ivr
            self._insp_valve.no_back_flow = True

            # # guard the inspiration pressures as this is pressure control
            if self._tubingin.pres > self.pip + self.p_atm:
                self._insp_valve.no_flow = True

            # close the expiration valve
            self._exp_valve.no_flow = True

            # increase the inspiratory volume
            self._insp_volume_counter += self._tubingin_ettube.flow * self._t

        if self._expiration:
            # increase the expiratory volume
            self._exp_volume_counter += self._ettube_tubingout.flow * self._t

            # close the inspiratory valve
            self._insp_valve.r_for = (
                (self._ventin.pres - 760) / (3.0 / 60.0)) - 200
            self._insp_valve.no_flow = True

            # open the expiration valve and calculate the expiration valve position depending on the desired peep and flow
            self._exp_valve.no_flow = False
            self._exp_valve.r_for = 15.0
            # self._ventout.vol = (
            #     (self.peep) / self._ventout.el_base) + self._ventout.u_vol
            # # guard the inspiration pressures as this is pressure control
            if self._tubingin.pres < self.peep + self.p_atm:
                self._ventout.vol = (
                    (self.peep) / self._ventout.el_base) + self._ventout.u_vol
            # else:
            #     self._ventout.vol = self._ventout.u_vol

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
        self._ventin.init_model(model)
        self._ventin.calc_model()
        self.set_air_composition(
            self._ventin, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'], self.temp, self.humidity)
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
            self._tubingin, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'], self.temp, self.humidity)
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
            self._tubingout, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'], self.temp, self.humidity)
        self._vent_parts.append(self._tubingout)

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
            self._ettube, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'], self.temp, self.humidity)
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
            self._ventout, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'], 0, 0)
        self._vent_parts.append(self._ventout)

        self._hfo_module = GasCapacitance(**{
            "name": "HFOMOD",
            "description": "hfo module",
            "model_type": "GasCapacitance",
            "is_enabled": True,
            "dependencies": [],
            "fixed_composition": False,
            "vol": 0.1,
            "u_vol": 0.1,
            "el_base": 10000,
            "el_k": 0
        })
        self._hfo_module.init_model(model)
        self._hfo_module.calc_model()
        self.set_air_composition(
            self._hfo_module, self.vent_air_dry['fo2'],  self.vent_air_dry['fco2'],  self.vent_air_dry['fn2'],  self.vent_air_dry['fother'], 0, 0)
        self._vent_parts.append(self._hfo_module)

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
            "comp_to": self._tubingin,
            "r_for": 30000,
            "r_back": 1000000,
            "r_k": 0,
        })
        self._insp_valve.init_model(model)
        self._vent_parts.append(self._insp_valve)

        self._tubingin_ettube = GasResistor(**{
            "name": "TUBINGIN_ETTUBE",
            "description": "connector between tubing in and et tube of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._tubingin,
            "comp_to": self._ettube,
            "r_for": 25,
            "r_back": 25,
            "r_k": 0,
        })
        self._tubingin_ettube.init_model(model)
        self._vent_parts.append(self._tubingin_ettube)

        self._ettube_ds = GasResistor(**{
            "name": "ETTUBE_DS",
            "description": "connector between ettube and dead space",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": True,
            "no_back_flow": False,
            "comp_from": self._ettube,
            "comp_to": self._model.models['DS'],
            "r_for": 50,
            "r_back": 50,
            "r_k": 0,
        })
        self._ettube_ds.init_model(model)
        self._vent_parts.append(self._ettube_ds)

        self._ettube_tubingout = GasResistor(**{
            "name": "ETTUBE_TUBINGOUT",
            "description": "connector between the et tube and the tubing out of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._ettube,
            "comp_to": self._tubingout,
            "r_for": 25,
            "r_back": 25,
            "r_k": 0,
        })
        self._ettube_tubingout.init_model(model)
        self._vent_parts.append(self._ettube_tubingout)

        self._exp_valve = GasResistor(**{
            "name": "EXPVALVE",
            "description": "expiration valve of the mechanical ventilator",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": False,
            "no_back_flow": False,
            "comp_from": self._tubingout,
            "comp_to": self._ventout,
            "r_for": 300000,
            "r_back": 300000,
            "r_k": 0,
        })
        self._exp_valve.init_model(model)
        self._vent_parts.append(self._exp_valve)

        self._hfo_valve = GasResistor(**{
            "name": "HFOVALVE",
            "description": "hfo filter connector",
            "model_type": "GasResistor",
            "is_enabled": True,
            "dependencies": [],
            "no_flow": True,
            "no_back_flow": False,
            "comp_from": self._tubingout,
            "comp_to": self._hfo_module,
            "r_for": 15,
            "r_back": 15,
            "r_k": 0,
        })
        self._hfo_valve.init_model(model)
        self._vent_parts.append(self._hfo_valve)

    def set_air_composition(self, comp, fo2_dry, fco2_dry, fn2_dry, fother_dry, temp, humidity):
        comp.temp = temp
        comp.target_temp = temp
        comp.humidity = humidity
        # calculate the concentration at this pressure and temperature in mmol/l using the gas law
        comp.ctotal = (
            comp.pres / (self._gas_constant * (273.15 + temp))) * 1000.0

        # calculate the water vapour pressure, concentration and fraction for this temperature and humidity (0 - 1)
        comp.ph2o = math.pow(math.e, 20.386 - 5132 /
                             (temp + 273)) * humidity
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
