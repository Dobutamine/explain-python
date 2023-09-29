import math
from explain_core.base_models.BaseModel import BaseModel


class Breathing(BaseModel):
    # independent variables
    breathing_enabled: bool = True
    target_minute_volume: float = 0.4
    vt_rr_ratio: float = 0.03
    rmp_gain_max: float = 12.0
    ie_ratio: float = 0.3
    targets: list = []
    is_intubated: bool = False
    tv_source: str = "MOUTH_DS"

    # dependent variables
    resp_rate: float = 40.0
    resp_signal: float = 0.0
    minute_volume: float = 0.0
    target_tidal_volume: float = 16.0
    exp_tidal_volume: float = 0.0
    insp_tidal_volume: float = 0.0
    resp_muscle_pressure = 0.0

    # local variables
    _eMin4 = math.pow(math.e, -4)
    _rmp_gain: float = 2.0
    _ti: float = 0.4
    _te: float = 1.0
    _breath_timer: float = 0.0
    _breath_interval: float = 60.0
    _insp_running: bool = False
    _insp_timer: float = 0.0
    _ncc_insp: int = 0
    _temp_insp_volume: float = 0.0
    _exp_running: bool = False
    _exp_timer: float = 0.0
    _ncc_exp: float = 0
    _temp_exp_volume: float = 0.0


    def switch_breathing(self, state):
        self.breathing_enabled = state
        
    def calc_model(self) -> None:
        if self.is_intubated:
            self.exp_tidal_volume = self._model.models["Ventilator"].exp_tidal_volume


        # calculate the respiratory rate and target tidal volume from the target minute volume
        self.vt_rr_controller()

        # calculate the inspiratory and expiratory time
        self._breath_interval = 60.0
        if self.resp_rate > 0:
            self._breath_interval = 60.0 / self.resp_rate
            self._ti = self.ie_ratio * self._breath_interval  # in seconds
            self._te = self._breath_interval - self._ti      # in seconds

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
                self.exp_tidal_volume = self._model.models["Ventilator"].exp_tidal_volume
            else:
                self.exp_tidal_volume = -self._temp_exp_volume
               

             # calculate the rmp gain
            if self.breathing_enabled:
                if abs(self.exp_tidal_volume) < self.target_tidal_volume:
                    self._rmp_gain += 0.1
                if abs(self.exp_tidal_volume) > self.target_tidal_volume:
                    self._rmp_gain -= 0.1
                if self._rmp_gain < 0:
                    self._rmp_gain = 0
                if self._rmp_gain > self.rmp_gain_max:
                    self._rmp_gain = self.rmp_gain_max

            self.minute_volume = self.exp_tidal_volume * self.resp_rate

        # increase the timers
        self._breath_timer += self._t

        if self._insp_running:
            self._insp_timer += self._t
            self._ncc_insp += 1
            if self._model.models['MOUTH_DS'].flow > 0:
                self._temp_insp_volume += self._model.models['MOUTH_DS'].flow * self._t

        if self._exp_running:
            self._exp_timer += self._t
            self._ncc_exp += 1
            if self._model.models['MOUTH_DS'].flow < 0:
                self._temp_exp_volume += self._model.models['MOUTH_DS'].flow * self._t

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
        for target in self.targets:
            self._model.models[target].act_factor = self.resp_muscle_pressure * 100.0
            #self._model.models[target].pres_ext = -self.resp_muscle_pressure

    def calc_resp_muscle_pressure(self) -> float:
        mp: float = 0.0
        # inspiration
        if self._insp_running:
            mp = (
                self._ncc_insp / (self._ti / self._t)) * self._rmp_gain

        # expiration
        if self._exp_running:
            mp = ((math.pow(math.e, -4.0 * (self._ncc_exp / (
                self._te / self._t))) - self._eMin4) / (1.0 - self._eMin4)) * self._rmp_gain

        return mp

    def vt_rr_controller(self) -> None:
        # calculate the spontaneous resp rate depending on the target minute volume (from ANS) and the set vt-rr ratio
        self.resp_rate = math.sqrt(
            self.target_minute_volume / self.vt_rr_ratio)

        # calculate the target tidal volume depending on the target resp rate and target minute volume (from ANS)
        if self.resp_rate > 0:
            self.target_tidal_volume = self.target_minute_volume / self.resp_rate
