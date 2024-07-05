import math


class Heart:
    # static properties
    model_type: str = "Heart"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.left_atrium = ""
        self.right_atrium = ""
        self.left_ventricle = ""
        self.right_ventricle = ""
        self.coronaries = ""
        self.coronary_sinus = ""
        self.pericardium = ""
        self.mitral_valve = ""
        self.tricuspid_valve = ""
        self.pulmonary_valve = ""
        self.aortic_valve = ""
        self.heart_rate_ref = 110.0
        self.heart_rate_override = False
        self.heart_rate_forced = 110.0
        self.rhythm_type = 0.0
        self.pq_time = 0.1
        self.qrs_time = 0.075
        self.qt_time = 0.25
        self.av_delay = 0.0005
        self.cardiac_cycle_time = 0.353
        self.hr_ans_factor = 1.0
        self.hr_mob_factor = 1.0
        self.hr_temp_factor = 1.0
        self.hr_drug_factor = 1.0
        self.ans_activity_factor = 1.0

        # dependent properties
        self.heart_rate = 120.0
        self.ncc_ventricular = 0.0
        self.ncc_atrial = 0.0
        self.ncc_resus = 0.0
        self.cardiac_cycle_running = 0
        self.prev_cardiac_cycle_running = 0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._la = None
        self._mv = None
        self._lv = None
        self._av = None
        self._ra = None
        self._tv = None
        self._rv = None
        self._pv = None
        self._cor = None
        self._pc = None
        self._sa_node_interval = 0.0
        self._sa_node_timer = 0.0
        self._pq_running = False
        self._pq_timer = 0.0
        self._av_delay_running = False
        self._av_delay_timer = 0.0
        self._qrs_running = False
        self._qrs_timer = 0.0
        self._qt_running = False
        self._qt_timer = 0.0
        self._ventricle_is_refractory = False
        self._kn = 0.579
        self._prev_cardiac_cycle = False
        self._temp_cardiac_cycle_time = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to all the heart models
        self._la = self._model_engine.models[self.left_atrium]
        self._ra = self._model_engine.models[self.right_atrium]
        self._lv = self._model_engine.models[self.left_ventricle]
        self._rv = self._model_engine.models[self.right_ventricle]

        # get a reference to the heart valves
        self._av = self._model_engine.models[self.aortic_valve]
        self._mv = self._model_engine.models[self.mitral_valve]
        self._tv = self._model_engine.models[self.tricuspid_valve]
        self._pv = self._model_engine.models[self.pulmonary_valve]

        # get a reference to the pericardium
        self._pc = self._model_engine.models[self.pericardium]

        # get a reference to the coronaries model
        self._cor = self._model_engine.models[self.coronaries]

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # set the previous cardiac cycle flag
        self.prev_cardiac_cycle_running = self.cardiac_cycle_running

        # calculate the heartrate from the reference value and all other influences
        self.heart_rate = (
            self.heart_rate_ref
            + (self.hr_ans_factor - 1.0)
            * self.heart_rate_ref
            * self.ans_activity_factor
            + (self.hr_mob_factor - 1.0) * self.heart_rate_ref
            + (self.hr_temp_factor - 1.0) * self.heart_rate_ref
            + (self.hr_drug_factor - 1.0) * self.heart_rate_ref
        )

        # override the heart rate if switch is on
        if self.heart_rate_override:
            self.heart_rate = self.heart_rate_forced

        # calculate the qtc time depending on the heartrate
        self.cqt_time = self.calc_qtc(self.heart_rate)

        # calculate the sinus node interval in seconds depending on the heart rate
        self._sa_node_interval = 60.0 / self.heart_rate

        # has the sinus node period elapsed?
        if self._sa_node_timer > self._sa_node_interval:
            # reset the sinus node timer
            self._sa_node_timer = 0.0
            # signal that the pq-time starts running
            self._pq_running = True
            # reset the atrial activation curve counter
            self.ncc_atrial = -1
            # signal that the cardiac cycle is running and reset the timer
            self._temp_cardiac_cycle_time = 0.0
            self.cardiac_cycle_running = 1

        # has the pq time period elapsed?
        if self._pq_timer > self.pq_time:
            # reset the pq timer
            self._pq_timer = 0.0
            # signal that pq timer has stopped
            self._pq_running = False
            # signal that the av delay timer has started
            self._av_delay_running = True

        # has the av delay time elasped
        if self._av_delay_timer > self.av_delay:
            # reset the av delay timer
            self._av_delay_timer = 0.0
            # signal that the av delay has stopped
            self._av_delay_running = False
            # check whether the ventricles are in a refractory state
            if not self._ventricle_is_refractory:
                # signal that the qrs time starts running
                self._qrs_running = True
                # reset the ventricular activation curve
                self.ncc_ventricular = -1

        # has the qrs time period elapsed?
        if self._qrs_timer > self.qrs_time:
            # reset the qrs timer
            self._qrs_timer = 0.0
            # signal that the qrs timer has stopped
            self._qrs_running = False
            # signal that the at timer starts running
            self._qt_running = True
            # signal that the ventricles are now in a refractory state
            self._ventricle_is_refractory = True

        # has the qt time period elapsed?
        if self._qt_timer > self.cqt_time:
            # reset the qt timer
            self._qt_timer = 0.0
            # signal that the qt timer has stopped
            self._qt_running = False
            # signal that the ventricles are coming out of their refractory state
            self._ventricle_is_refractory = False
            # signal the end of the cardiac cycle
            self.cardiac_cycle_time = self._temp_cardiac_cycle_time
            self.cardiac_cycle_running = 0

        # increase the timers with the modeling stepsize as set by the model base class
        self._sa_node_timer += self._t

        if self._pq_running:
            self._pq_timer += self._t

        if self._av_delay_running:
            self._av_delay_timer += self._t

        if self._qrs_running:
            self._qrs_timer += self._t

        if self._qt_running:
            self._qt_timer += self._t

        # check the cardiac cycle
        if self.cardiac_cycle_running == 1:
            self._temp_cardiac_cycle_time += self._t

        # increase the heart activation function counters
        self.ncc_atrial += 1
        self.ncc_ventricular += 1

        # calculate the varying elastance factor
        self.calc_varying_elastance()

    def calc_varying_elastance(self):
        # calculate the atrial activation factor
        _atrial_duration = self.pq_time / self._t
        if self.ncc_atrial >= 0 and self.ncc_atrial < _atrial_duration:
            self.aaf = math.sin(math.pi * (self.ncc_atrial / _atrial_duration))
        else:
            self.aaf = 0.0

        # calculate the ventricular activation factor
        _ventricular_duration = (self.qrs_time + self.cqt_time) / self._t
        if self.ncc_ventricular >= 0 and self.ncc_ventricular < _ventricular_duration:
            self.vaf = (
                self.ncc_ventricular / (self._kn * _ventricular_duration)
            ) * math.sin(math.pi * (self.ncc_ventricular / _ventricular_duration))
        else:
            self.vaf = 0.0

        # transfer the activation factor to the heart components
        self._la.act_factor = self.aaf
        self._ra.act_factor = self.aaf
        self._lv.act_factor = self.vaf
        self._rv.act_factor = self.vaf

        if self._cor:
            # transfer the activation factor to the heart components
            self._cor.act_factor = self.vaf

    def calc_qtc(self, hr):
        if hr > 10.0:
            return self.qt_time * math.sqrt(60.0 / hr)
        else:
            return self.qt_time * 2.449
            # (sqrt(6))

    def set_ecg_timings(self, pq_time, qrs_time, qt_time):
        self.pq_time = pq_time
        self.qrs_time = qrs_time
        self.qt_time = qt_time

    def set_heartchamber_props_abs(self, chamber, el_min, el_max, u_vol, el_k):
        t = self._model_engine.models[chamber]
        t.el_min = el_min
        t.el_max = el_max
        t.u_vol = u_vol
        t.el_k = el_k

    def set_heartchamber_props_rel(
        self, chamber, el_min_factor, el_max_factor, el_k_factor, u_vol_factor
    ):
        t = self._model_engine.models[chamber]
        t.el_min_factor = el_min_factor
        t.el_max_factor = el_max_factor
        t.u_vol_factor = u_vol_factor
        t.el_k_factor = el_k_factor

    def set_heartvalve_props_abs(
        self, valve, r_for, r_back, r_k, no_flow, no_back_flow
    ):
        t = self._model_engine.models[valve]
        t.r_for = r_for
        t.r_back = r_back
        t.r_k = r_k
        t.no_flow = no_flow
        t.no_back_flow = no_back_flow

    def set_heartvalve_props_rel(
        valve, r_for_factor, r_back_factor, r_k_factor, no_flow, no_back_flow
    ):
        t = self._model_engine.models[valve]
        t.r_for_factor = r_for_factor
        t.r_back_factor = r_back_factor
        t.r_k_factor = r_k_factor
        t.no_flow = no_flow
        t.no_back_flow = no_back_flow
