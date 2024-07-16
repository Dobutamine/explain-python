import math

from explain_core.helpers.GasComposition import set_gas_composition


class Ventilator:
    # static properties
    model_type: str = "Ventilator"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.p_atm = 760.0
        self.fio2 = 0.205
        self.temp = 37.0
        self.humidity = 1.0
        self.vent_running = False
        self.ettube_diameter = 3.5
        # in mm
        self.ettube_length = 110
        # in mm
        self.ettube_length_ref = 110
        self.vent_mode = "PRVC"
        self.vent_rate = 40.0
        self.insp_time = 0.4
        self.insp_flow = 10.0
        self.hfo_map_cmh2o = 10.0
        self.hfo_bias_flow = 10.0
        self.hfo_freq = 12
        self.hfo_amplitude_cmh2o = 10.0
        self.exp_flow = 3.0
        self.pip_cmh2o = 10.3
        self.pip_cmh2o_max = 10.3
        self.peep_cmh2o = 3.65
        self.tidal_volume = 0.0165
        self.trigger_volume_perc = 6
        self.synchronized = False

        # dependent properties
        self.pres = 0.0
        self.pres_cmh2o = 0.0
        self.flow = 0.0
        self.vol = 0.0
        self.compliance = 0.0
        self.elastance = 0.0
        self.resistance = 0.0
        self.co2 = 0.0
        self.etco2 = 0.0
        self.exp_time = 0.8
        self.insp_tidal_volume = 0.0
        self.exp_tidal_volume = 0.0
        self.minute_volume = 0.0
        self.trigger_volume = 0.0
        self.tv_kg = 0.0
        self.vc_po2 = 0.0
        self.vc_pco2 = 0.0
        self.et_tube_resistance = 60.0
        self.hfo_pres = 0.0
        self.hfo_tv = 0.0
        self.hfo_dco2 = 0.0
        self.hfo_insp_tv = 0.0
        self.hfo_exp_tv = 0.0
        self.hfo_mv = 0.0
        self.synchronized = False
        self.vent_sync = False

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._vent_in = None
        self._insp_valve = None
        self._vent_circuit = None
        self._et_tube = None
        self._exp_valve = None
        self._vent_out = None
        self._vent_parts = []
        self._insp_time_counter = 0.0
        self._exp_time_counter = 0.0
        self._inspiration = True
        self._expiration = False
        self._insp_tidal_volume_counter = 0.0
        self._exp_tidal_volume_counter = 0.0
        self._trigger_volume_counter = 0.0
        self._tube_resistance = 25.0
        self._max_flow = 0.0
        self._pres_reached = False
        self._vol_reached = False
        self._pip = 0.0
        self._pip_max = 0.0
        self._peep = 0.0
        self._hfo_map = 0.0
        self._hfo_amplitude = 0.0
        self._tv_tolerance = 0.0005

        # tidal volume tolerance for volume control in l
        self._triggered_breath = False
        self._block_trigger_counter = 0.0
        self._block_trigger = False
        self._prev_et_tube_flow = 0.0
        self._prev_et_tube_flow_delta = 0.0
        self._peak_flow = 0.0
        self._peak_flow_temp = 0.0
        self._end_insp = False
        self._a = 0.0
        self._b = 0.0
        self._hfo_time_counter = 0
        self._hfo_insp_tv_counter = 0
        self._hfo_exp_tv_counter = 0
        self._hfo_state = 0
        self._prev_hfo_state = 0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # build the ventilator
        self.build_ventilator()

        # flag that the model is initialized
        self._is_initialized = True

    # self method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # make sure eveything is running
        self._model_engine.models["MOUTH_DS"].no_flow = self.vent_running
        self._model_engine.models["Breathing"].is_intubated = self.vent_running

        self._vent_in.is_enabled = self.vent_running
        self._vent_circuit.is_enabled = self.vent_running
        self._vent_out.is_enabled = self.vent_running
        self._insp_valve.is_enabled = self.vent_running
        self._exp_valve.is_enabled = self.vent_running
        self._et_tube.is_enabled = self.vent_running
        self._et_tube.no_flow = not self.vent_running

        # convert settings to mmHg from cmH2o
        self._pip = self.pip_cmh2o / 1.35951
        self._pip_max = self.pip_cmh2o_max / 1.35951
        self._peep = self.peep_cmh2o / 1.35951
        self._hfo_map = self.hfo_map_cmh2o / 1.35951
        self._hfo_amplitude = (self.hfo_amplitude_cmh2o / 1.35951) * 0.5

        # determine the trigger volume
        self.trigger_volume = (self.tidal_volume / 100.0) * self.trigger_volume_perc

        # check whether the trigger volume is reached
        if self.vent_sync:
            if (
                self._trigger_volume_counter > self.trigger_volume
                and not self._triggered_breath
            ):
                # we have a triggered breath
                self._triggered_breath = True
                # reset the trigger volume counter
                self._trigger_volume_counter = 0.0

        # update the triggered volume
        if (
            not self._triggered_breath
            and not self._inspiration
            and not self._block_trigger
            and self._et_tube.flow > 0.0
        ):
            self._trigger_volume_counter += self._et_tube.flow * self._t

        self._triggered_breath = False

        # call the correct ventilation mode
        if self.vent_mode == "VC":
            self.time_cycling()
            self.volume_control()

        if self.vent_mode == "PC":
            self.time_cycling()
            self.pressure_control()

        if self.vent_mode == "PRVC":
            self.time_cycling()
            self.pressure_control()

        if self.vent_mode == "PS":
            self.flow_cycling()
            self.pressure_support()

        if self.vent_mode == "HFOV":
            self.hfov()

        # store the values
        self.pres = (self._vent_circuit.pres - self.p_atm) * 1.35951
        # in cmH2O
        self.flow = self._et_tube.flow * 60.0
        # in l/min
        self.vol += self._et_tube.flow * 1000 * self._t
        # in ml
        self.co2 = self._model_engine.models["DS"].pco2
        # in mmHg
        self.vc_po2 = self._vent_circuit.po2
        self.vc_pco2 = self._vent_circuit.pco2
        self.minute_volume = self.exp_tidal_volume * self.vent_rate

        # set the flow dependent endotracheal tube resistance
        self.et_tube_resistance = self.calc_ettube_resistance(self.flow)
        self._et_tube.r_for = self.et_tube_resistance
        self._et_tube.r_back = self.et_tube_resistance

        # # do the model step of the ventilator parts
        # for vent_part in self._vent_parts:
        #     vent_part.step_model()

    def build_ventilator(self):
        # clear the ventilator parts list
        self._vent_parts = []

        # ventilator gas reservoir
        self._vent_in = self._model_engine.models["VENT_GASIN"]
        self._vent_in.is_enabled = False
        self._vent_in.fixed_composition = True
        self._vent_in.vol = 5.4
        self._vent_in.u_vol = 5.0
        self._vent_in.el_base = 1000.0
        self._vent_in.el_k = 0.0
        self._vent_in.pres_atm = self.p_atm

        # calculate the current pressure
        self._vent_in.calc_model()

        # set the gas composition
        set_gas_composition(self._vent_in, self.fio2, self.temp, self.humidity)

        # add to the vent parts array
        self._vent_parts.append(self._vent_in)

        # ventilator circuit
        self._vent_circuit = self._model_engine.models["VENT_GASCIRCUIT"]
        self._vent_circuit.is_enabled = False
        self._vent_circuit.fixed_composition = False
        self._vent_circuit.vol = 0.262
        self._vent_circuit.u_vol = 0.262
        self._vent_circuit.el_base = 1130.0
        self._vent_circuit.el_k = 0.0
        self._vent_circuit.pres_atm = self.p_atm

        # calculate the current pressure
        self._vent_circuit.calc_model()

        # set the gas composition
        set_gas_composition(self._vent_circuit, self.fio2, self.temp, self.humidity)

        # add to the vent parts array
        self._vent_parts.append(self._vent_circuit)

        # ventilator out reservoir
        self._vent_out = self._model_engine.models["VENT_GASOUT"]
        self._vent_out.is_enabled = False
        self._vent_out.fixed_composition = True
        self._vent_out.vol = 5.0
        self._vent_out.u_vol = 5.0
        self._vent_out.el_base = 1000.0
        self._vent_out.el_k = 0.0
        self._vent_out.pres_atm = self.p_atm

        # calculate the current pressure
        self._vent_out.calc_model()

        # set the gas composition
        set_gas_composition(self._vent_out, self.fio2, self.temp, self.humidity)

        # add to the vent parts array
        self._vent_parts.append(self._vent_out)

        # connect the parts
        self._insp_valve = self._model_engine.models["VENT_INSP_VALVE"]
        self._insp_valve.is_enabled = False
        self._insp_valve.no_flow = True
        self._insp_valve.no_back_flow = False
        self._insp_valve.comp_from = self._vent_in
        self._insp_valve.comp_to = self._vent_circuit
        self._insp_valve.r_for = 2000.0
        self._insp_valve.r_back = 2000.0
        self._insp_valve.r_k = 0.0

        # add to the vent parts array
        self._vent_parts.append(self._insp_valve)

        # calculate the tube resistance
        self.set_ettube_diameter(self.ettube_diameter)
        self.et_tube_resistance = self.calc_ettube_resistance(self.insp_flow)

        self._et_tube = self._model_engine.models["VENT_ETTUBE"]
        self._et_tube.is_enabled = False
        self._et_tube.no_flow = True
        self._et_tube.no_back_flow = False
        self._et_tube.comp_from = self._vent_circuit
        self._et_tube.comp_to = self._model_engine.models["DS"]
        self._et_tube.r_for = self.et_tube_resistance
        self._et_tube.r_back = self.et_tube_resistance
        self._et_tube.r_k = 0.0

        # add to the vent parts array
        self._vent_parts.append(self._et_tube)

        self._exp_valve = self._model_engine.models["VENT_EXP_VALVE"]
        self._exp_valve.is_enabled = False
        self._exp_valve.no_flow = True
        self._exp_valve.no_back_flow = True
        self._exp_valve.comp_from = self._vent_circuit
        self._exp_valve.comp_to = self._vent_out
        self._exp_valve.r_for = 2000.0
        self._exp_valve.r_back = 2000.0
        self._exp_valve.r_k = 0.0
        # add to the vent parts array
        self._vent_parts.append(self._exp_valve)

    def set_ettube_length(self, new_length):
        if new_length >= 50:
            self.ettube_length = new_length

    def set_ettube_diameter(self, new_diameter):
        # diameter in mm
        if new_diameter > 1.5:
            self.ettube_diameter = new_diameter
            # set the flow dependent parameters
            self._a = -2.375 * new_diameter + 11.9375
            self._b = -14.375 * new_diameter + 65.9374

    def calc_ettube_resistance(self, flow):
        res = (self._a * flow + self._b) * (self.ettube_length / self.ettube_length_ref)
        if res < 15.0:
            res = 15
        return res

    def set_tubing_length(self, new_length):
        pass

    def set_fio2(self, new_fio2):
        self.fio2 = new_fio2 / 100.0
        set_gas_composition(self._vent_in, self.fio2, self.temp, self.humidity)

    def set_temp(self, new_temp):
        if new_temp > 0 and new_temp < 60:
            self.temp = new_temp
            set_gas_composition(self._vent_in, self.fio2, self.temp, self.humidity)
            set_gas_composition(self._vent_circuit, self.fio2, self.temp, self.humidity)

    def set_humidity(self, new_hum):
        if new_hum > 0 and new_hum <= 1.0:
            self.humidity = new_hum
            set_gas_composition(self._vent_in, self.fio2, self.temp, self.humidity)
            set_gas_composition(self._vent_circuit, self.fio2, self.temp, self.humidity)

    def set_ventilator_cpap(self, peep=4.0, rate=1.0, t_in=0.4, insp_flow=10.0):
        self.pip_cmh2o = peep + 0.5
        self.pip_cmh2o_max = peep + 0.5
        self.peep_cmh2o = peep
        self.vent_rate = 0.01
        self.insp_time = t_in
        self.insp_flow = insp_flow
        self.synchronized = False
        self.vent_mode = "CPAP"

    def set_ventilator_hfov(self, map=10.0, freq=12.0, amplitude=25, bias_flow=10.0):
        self.hfo_map_cmh2o = map
        self.hfo_freq = freq
        self.hfo_amplitude_cmh2o = amplitude
        self.hfo_bias_flow = bias_flow
        self.synchronized = False
        self.vent_mode = "HFOV"

        # reset others
        self.exp_tidal_volume = 0.0
        self.insp_tidal_volume = 0.0
        self.minute_volume = 0.0
        self.pip_cmh2o = 0.0
        self.peep_cmh2o = 0.0
        self.vent_rate = 0.0
        self.compliance = 0.0
        self.resistance = 0.0
        self.etco2 = 0.0

    def set_trigger_perc(self, new_perc):
        if new_perc > 1.0 and new_perc < 50.0:
            self.trigger_volume_perc = new_perc

    def set_ventilator_ps(
        self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0
    ):
        self.pip_cmh2o = pip
        self.pip_cmh2o_max = pip
        self.peep_cmh2o = peep
        self.vent_rate = rate
        self.insp_time = t_in
        self.insp_flow = insp_flow
        self.vent_mode = "PS"

    def set_ventilator_pc(
        self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0
    ):
        self.pip_cmh2o = pip
        self.pip_cmh2o_max = pip
        self.peep_cmh2o = peep
        self.vent_rate = rate
        self.insp_time = t_in
        self.insp_flow = insp_flow
        self.vent_mode = "PC"

    def set_ventilator_prvc(
        self, pip_max=18.0, peep=4.0, rate=40.0, tv=15.0, t_in=0.4, insp_flow=10.0
    ):
        # self.pip_cmh2o = pip_max;
        self.pip_cmh2o_max = pip_max
        self.peep_cmh2o = peep
        self.vent_rate = rate
        self.insp_time = t_in
        self.tidal_volume = tv / 1000.0
        self.insp_flow = insp_flow
        self.vent_mode = "PRVC"

    def set_ventilator_vc(
        self, pip_max=18.0, peep=4.0, rate=40.0, tv=15.0, t_in=0.4, insp_flow=10.0
    ):
        # self.pip_cmh2o = pip_max;
        self.pip_cmh2o_max = pip_max
        self.peep_cmh2o = peep
        self.vent_rate = rate
        self.insp_time = t_in
        self.tidal_volume = tv / 1000.0
        self.insp_flow = insp_flow
        self.vent_mode = "VC"

    def switch_ventilator(self, state):
        self._model_engine.models["MOUTH_DS"].no_flow = state
        self._model_engine.models["Breathing"].is_intubated = state
        self._et_tube.no_flow = not state
        self.vent_running = state
        self.is_enabled = state
        self._vent_in.is_enabled = state
        self._vent_circuit.is_enabled = state
        self._vent_out.is_enabled = state
        self._insp_valve.is_enabled = state
        self._exp_valve.is_enabled = state
        self._et_tube.is_enabled = state

    def trigger_breath(self):
        # we have a triggered breath
        self._triggered_breath = True
        # reset the trigger volume counter
        self._trigger_volume_counter = 0.0

    def time_cycling(self):
        # calculate the expiration time
        self.exp_time = 60.0 / self.vent_rate - self.insp_time

        # has the inspiration time elapsed?
        if self._insp_time_counter > self.insp_time:
            # reset the inspiration time counter
            self._insp_time_counter = 0.0
            # reset the inspiratory tidal volume counter
            self._insp_tidal_volume_counter = 0.0
            # flag the inspiration and expiration
            self._inspiration = False
            self._expiration = True
            # reset the triggered breath flag
            self._triggered_breath = False
            # reset the block trigger counter
            self._block_trigger_counter = 0.0
            # as the inspiration is just finished block the triggered breath for a while
            self._block_trigger = True

        # release the triggered breath block over 1.5 times the inspiration time
        if self._block_trigger_counter > self.insp_time * 0.25:
            # reset the block trigger counter
            self._block_trigger_counter = 0.0
            # release the blocked trigger lock
            self._block_trigger = False

        # has the expiration time elapsed or is the expiration phase ended by a triggered breath
        if self._exp_time_counter > self.exp_time or self._triggered_breath:
            # reset the expiration time counter
            self._exp_time_counter = 0.0
            # flag the inspiration and expiration
            self._inspiration = True
            self._expiration = False
            # reset the triggered breath flag
            self._triggered_breath = False
            # reset the volume counter
            self.vol = 0.0
            # reset the volume counters
            self.exp_tidal_volume = -self._exp_tidal_volume_counter
            # store the end tidal co2
            self.etco2 = self._model_engine.models["DS"].pco2
            # calculate the tidal volume per kg
            self.tv_kg = (self.exp_tidal_volume * 1000.0) / self._model_engine.weight
            # calculate the compliance of the lung
            if self.exp_tidal_volume > 0:
                self.compliance = 1 / (
                    ((self._pip - self._peep) * 1.35951)
                    / (self.exp_tidal_volume * 1000.0)
                )
                # in ml/cmH2O

            # reset the expiratory tidal volume counter
            self._exp_tidal_volume_counter = 0.0
            # check whether the ventilator is in PRVC mode because we need to adjust the pressure depending on the tidal volume
            if self.vent_mode == "PRVC":
                self.pressure_regulated_volume_control()

        # if the trigger volume is blocked increase the timer for the blokkade duration
        if self._block_trigger:
            self._block_trigger_counter += self._t

        # if in inspiration increase the timer
        if self._inspiration:
            self._insp_time_counter += self._t

        # if in expiration increase the timer
        if self._expiration:
            self._exp_time_counter += self._t

    def flow_cycling(self):
        print("t")
        # is there flow moving to the lungs and the breath is triggered
        if self._et_tube.flow > 0.0 and self._triggered_breath:
            # check whether the flow is increasing
            if self._et_tube.flow > self._prev_et_tube_flow:
                # if increasing then keep inspiration going
                self._inspiration = True
                self._expiration = False
                # determine the peak flow
                if self._et_tube.flow > self._peak_flow:
                    self._peak_flow = self._et_tube.flow

                # store the current exhaled tidal volume
                self.exp_tidal_volume = -self._exp_tidal_volume_counter
            else:
                # if decreasing wait until it is 70% of the peak flow
                if self._et_tube.flow < 0.7 * self._peak_flow:
                    # go into expiration
                    self._inspiration = False
                    self._expiration = True
                    # reset the tidal volume counter
                    self._exp_tidal_volume_counter = 0.0
                    # reset the triggered breath flag
                    self._triggered_breath = False
            self._prev_et_tube_flow = self._et_tube.flow

        if self._et_tube.flow < 0.0 and not self._triggered_breath:
            self._peak_flow = 0.0
            self._prev_et_tube_flow = 0.0
            self._inspiration = False
            self._expiration = True
            # calculate the expiratory tidal volume
            self._exp_tidal_volume_counter += self._et_tube.flow * self._t

    def volume_control(self):
        if self._inspiration:
            # close the expiration valve and open the inspiration valve
            self._exp_valve.no_flow = True
            self._insp_valve.no_flow = False

            # prevent back flow to the ventilator
            self._insp_valve.no_back_flow = True

            # set the resistance of the inspiration valve
            self._insp_valve.r_for = 1000.0

            # guard the inspiratory flow
            if self._et_tube.flow > self.insp_flow / 60.0:
                self._insp_valve.no_flow = True

            # guard the inspiratory volume
            if self._insp_tidal_volume_counter > self.tidal_volume:
                self._insp_valve.no_flow = True
                self._insp_valve.r_for_factor = 1.0
                if self._insp_valve.flow > 0 and not self._vol_reached:
                    self.resistance = (
                        self._vent_circuit.pres - self.p_atm
                    ) / self._insp_valve.flow
                    self._vol_reached = True

            # calculate the expiratory tidal volume
            if self._insp_valve.flow > 0:
                self._insp_tidal_volume_counter += self._insp_valve.flow * self._t

        if self._expiration:
            self._vol_reached = False
            # close the inspiration valve and open the expiration valve
            self._insp_valve.no_flow = True

            self._exp_valve.no_flow = False
            self._exp_valve.no_back_flow = True

            # set the resistance of the expiration valve to and calculate the pressure in the expiration block
            self._exp_valve.r_for = 10
            self._vent_out.vol = (
                self._peep / self._vent_out.el_base + self._vent_out.u_vol
            )

            # calculate the expiratory tidal volume
            if self._et_tube.flow < 0:
                self._exp_tidal_volume_counter += self._et_tube.flow * self._t

    def pressure_control(self):
        if self._inspiration:
            # close the expiration valve and open the inspiration valve
            self._exp_valve.no_flow = True
            self._insp_valve.no_flow = False

            # prevent back flow to the ventilator
            self._insp_valve.no_back_flow = True

            # set the resistance of the inspiration valve
            self._insp_valve.r_for = (
                self._vent_in.pres + self._pip - self.p_atm - self._peep
            ) / (self.insp_flow / 60.0)

            # guard the inspiratory pressure
            if self._vent_circuit.pres > self._pip + self.p_atm:
                self._insp_valve.no_flow = True
                self._insp_valve.r_for_factor = 1.0
                if self._insp_valve.flow > 0 and not self._pres_reached:
                    self.resistance = (
                        self._vent_circuit.pres - self.p_atm
                    ) / self._insp_valve.flow
                    self._pres_reached = True

        if self._expiration:
            self._pres_reached = False
            # close the inspiration valve and open the expiration valve
            self._insp_valve.no_flow = True

            self._exp_valve.no_flow = False
            self._exp_valve.no_back_flow = True

            # set the resistance of the expiration valve to and calculate the pressure in the expiration block
            self._exp_valve.r_for = 10
            self._vent_out.vol = (
                self._peep / self._vent_out.el_base + self._vent_out.u_vol
            )

            # calculate the expiratory tidal volume
            if self._et_tube.flow < 0:
                self._exp_tidal_volume_counter += self._et_tube.flow * self._t

    def pressure_support(self):
        if self._inspiration:
            # close the expiration valve and open the inspiration valve
            self._exp_valve.no_flow = True
            self._insp_valve.no_flow = False

            # prevent back flow to the ventilator
            self._insp_valve.no_back_flow = True

            # set the resistance of the inspiration valve
            self._insp_valve.r_for = (
                self._vent_in.pres + self._pip - self.p_atm - self._peep
            ) / (self.insp_flow / 60.0)

            # guard the inspiratory pressure
            if self._vent_circuit.pres > self._pip + self.p_atm:
                self._insp_valve.no_flow = True
                self._insp_valve.r_for_factor = 1.0
                if self._insp_valve.flow > 0 and not self._pres_reached:
                    self.resistance = (
                        self._vent_circuit.pres - self.p_atm
                    ) / self._insp_valve.flow
                    self._pres_reached = True

        if self._expiration:
            self._pres_reached = False
            # close the inspiration valve and open the expiration valve
            self._insp_valve.no_flow = True

            self._exp_valve.no_flow = False
            self._exp_valve.no_back_flow = True

            # set the resistance of the expiration valve to and calculate the pressure in the expiration block
            self._exp_valve.r_for = 10
            self._vent_out.vol = (
                self._peep / self._vent_out.el_base + self._vent_out.u_vol
            )

            # calculate the expiratory tidal volume
            if self._et_tube.flow < 0:
                self._exp_tidal_volume_counter += self._et_tube.flow * self._t

    def pressure_regulated_volume_control(self):
        if self.exp_tidal_volume < self.tidal_volume - self._tv_tolerance:
            self.pip_cmh2o += 1.0
            if self.pip_cmh2o > self.pip_cmh2o_max:
                self.pip_cmh2o = self.pip_cmh2o_max

        if self.exp_tidal_volume > self.tidal_volume + self._tv_tolerance:
            self.pip_cmh2o -= 1.0
            if self.pip_cmh2o < self.peep_cmh2o + 2.0:
                self.pip_cmh2o = self.peep_cmh2o + 2.0

    def hfov(self):
        # shut down flow to patient
        self._et_tube.no_flow = False

        # open the inspiration valve
        self._insp_valve.no_flow = False

        # open the expiration valve
        self._exp_valve.no_flow = False

        # back flow to the ventilator
        self._insp_valve.no_back_flow = False

        # back flow to the ventilator
        self._exp_valve.no_back_flow = False

        # set the resistance of the inspiration valve to supply the bias flow
        self._insp_valve.r_for = (self._vent_in.pres - self.p_atm - self._hfo_map) / (
            self.hfo_bias_flow / 60.0
        )

        # set the expiration valve
        self._exp_valve.r_for = 10
        self._vent_out.vol = (
            self._hfo_map / self._vent_out.el_base + self._vent_out.u_vol
        )

        hfo_p = self._hfo_amplitude * math.sin(
            2 * math.pi * self.hfo_freq * self._hfo_time_counter
        )
        self._hfo_time_counter += self._t

        self.hfo_pres = hfo_p

        # guard the inspiratory pressure
        if self._vent_circuit.pres > self._hfo_map + self.p_atm + hfo_p:
            self._insp_valve.no_flow = True

        # find the state
        if self._et_tube.flow > 0:
            self._hfo_state = 0
            self._hfo_insp_tv_counter += self._et_tube.flow * self._t
        else:
            self._hfo_state = 1
            self._hfo_exp_tv_counter += self._et_tube.flow * self._t

        # store the tidal volume
        if self._hfo_state == 0 and self._prev_hfo_state == 1:
            self.hfo_exp_tv = -self._hfo_exp_tv_counter
            self._hfo_exp_tv_counter = 0

        if self._hfo_state == 1 and self._prev_hfo_state == 0:
            self.hfo_insp_tv = self._hfo_insp_tv_counter
            self._hfo_insp_tv_counter = 0

        self.hfo_tv = ((self.hfo_insp_tv + self.hfo_exp_tv) / 2.0) * 1000.0
        self.hfo_dco2 = self.hfo_tv * self.hfo_tv * self.hfo_freq
        self.hfo_mv = self.hfo_tv * self.hfo_freq * 60.0

        self._vent_out.pres_ext += hfo_p
        self._prev_hfo_state = self._hfo_state
