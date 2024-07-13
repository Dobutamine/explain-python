import math


class Breathing:
    # static properties
    model_type: str = "Breathing"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.targets = []
        self.breathing_enabled = True
        self.minute_volume_ref = 0.64  # in L/min/kg
        self.minute_volume_ref_factor = 1.0
        self.minute_volume_ref_scaling_factor = 1.0
        self.vt_rr_ratio = 0.03
        # in L/bpm/kg
        self.vt_rr_ratio_factor = 1.0
        self.vt_rr_ratio_scaling_factor = 1.0
        self.rmp_gain_max = 12.0
        self.ie_ratio = 0.3
        self.is_intubated = False
        self.tv_source = "MOUTH_DS"
        self.mv_ans_factor = 1.0
        self.ans_activity_factor = 1.0
        self.target_minute_volume = 0.4
        self.target_tidal_volume = 16.0

        # dependent properties
        self.resp_rate = 40.0
        self.resp_signal = 0.0
        self.minute_volume = 0.0
        self.exp_tidal_volume = 0.0
        self.insp_tidal_volume = 0.0
        self.resp_muscle_pressure = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._eMin4 = math.pow(math.e, -4)
        self._ti = 0.4
        self._te = 1.0
        self._breath_timer = 0.0
        self._breath_interval = 60.0
        self._insp_running = False
        self._insp_timer = 0.0
        self._ncc_insp = 0
        self._temp_insp_volume = 0.0
        self._exp_running = False
        self._exp_timer = 0.0
        self._ncc_exp = 0
        self._temp_exp_volume = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # get the current model weight
        _weight = self._model_engine.weight

        # if the patient is intubated, the minute volume is calculated differently
        if self.is_intubated:
            self.exp_tidal_volume = self._model_engine.models[
                "Ventilator"
            ].exp_tidal_volume

        # calculate the target minute volume
        _minute_volume_ref = (
            self.minute_volume_ref
            * self.minute_volume_ref_factor
            * self.minute_volume_ref_scaling_factor
            * _weight
        )

        self.target_minute_volume = (
            _minute_volume_ref + (self.mv_ans_factor - 1.0) * _minute_volume_ref
        ) * self.ans_activity_factor

        if self.target_minute_volume < 0.01:
            self.target_minute_volume = 0.01

        # calculate the respiratory rate and target tidal volume from the target minute volume
        self.vt_rr_controller(_weight)

        # calculate the inspiratory and expiratory time
        self._breath_interval = 60.0
        if self.resp_rate > 0:
            self._breath_interval = 60.0 / self.resp_rate
            self._ti = self.ie_ratio * self._breath_interval
            # in seconds
            self._te = self._breath_interval - self._ti
            # in seconds

        # is it time to start a breath?
        if self._breath_timer > self._breath_interval:
            self._breath_timer = 0.0
            self._insp_running = True
            self._insp_timer = 0.0
            self._ncc_insp = 0.0

        # has the inspiration time elapsed?
        if self._insp_timer > self._ti:
            self._insp_timer = 0.0
            self._insp_running = False
            self._exp_running = True
            self._ncc_exp = 0.0
            self._temp_exp_volume = 0.0
            self.insp_tidal_volume = -self._temp_insp_volume

        # has the expiration time elapsed?
        if self._exp_timer > self._te:
            self._exp_timer = 0.0
            self._exp_running = False
            self._temp_insp_volume = 0.0
            if self.is_intubated:
                self.exp_tidal_volume = self._model_engine.models[
                    "Ventilator"
                ].exp_tidal_volume
            else:
                self.exp_tidal_volume = -self._temp_exp_volume

            # calculate the rmp gain
            if self.breathing_enabled:
                if abs(self.exp_tidal_volume) < self.target_tidal_volume:
                    self.rmp_gain += 0.1
                if abs(self.exp_tidal_volume) > self.target_tidal_volume:
                    self.rmp_gain -= 0.1
                if self.rmp_gain < 0.0:
                    self.rmp_gain = 0.0
                if self.rmp_gain > self.rmp_gain_max:
                    self.rmp_gain = self.rmp_gain_max
            self.minute_volume = self.exp_tidal_volume * self.resp_rate

        # increase the timers
        self._breath_timer += self._t

        if self._insp_running:
            self._insp_timer += self._t
            self._ncc_insp += 1
            if self._model_engine.models["MOUTH_DS"].flow > 0:
                self._temp_insp_volume += (
                    self._model_engine.models["MOUTH_DS"].flow * self._t
                )

        if self._exp_running:
            self._exp_timer += self._t
            self._ncc_exp += 1
            if self._model_engine.models["MOUTH_DS"].flow < 0:
                self._temp_exp_volume += (
                    self._model_engine.models["MOUTH_DS"].flow * self._t
                )

        # reset the respiratory muscle pressure
        self.resp_muscle_pressure = 0.0

        # calculate the new respiratory muscle pressure
        if self.breathing_enabled:
            self.resp_muscle_pressure = self.calc_resp_muscle_pressure()
        else:
            self.resp_rate = 0.0
            self.target_tidal_volume = 0.0
            self.resp_muscle_pressure = 0.0

        # transfer the respiratory muscle pressure to the targets
        if type(self.targets) == str:
            self.targets = [self.targets]

        for target in self.targets:
            self._model_engine.models[target].act_factor = (
                self.resp_muscle_pressure * 100.0
            )

    def vt_rr_controller(self, _weight):
        # calculate the spontaneous resp rate depending on the target minute volume (from ANS) and the set vt-rr ratio
        self.resp_rate = math.sqrt(
            self.target_minute_volume
            / (
                self.vt_rr_ratio
                * self.vt_rr_ratio_factor
                * self.vt_rr_ratio_scaling_factor
                * _weight
            )
        )

        # calculate the target tidal volume depending on the target resp rate and target minute volume (from ANS)
        if self.resp_rate > 0:
            self.target_tidal_volume = self.target_minute_volume / self.resp_rate

    def calc_resp_muscle_pressure(self):
        mp = 0.0
        # inspiration
        if self._insp_running:
            mp = (self._ncc_insp / (self._ti / self._t)) * self.rmp_gain

        # expiration
        if self._exp_running:
            mp = (
                (
                    math.pow(math.e, -4.0 * (self._ncc_exp / (self._te / self._t)))
                    - self._eMin4
                )
                / (1.0 - self._eMin4)
            ) * self.rmp_gain

        return mp

    def switch_breathing(state):
        self.breathing_enabled = state

    def set_resp_rate(resp_rate):
        self.resp_rate = resp_rate

    def set_mv_ref(mv_ref):
        self.minute_volume_ref = mv_ref

    def set_vt_rr_ratio(self, vt_rr_ratio):
        self.vt_rr_ratio = vt_rr_ratio
