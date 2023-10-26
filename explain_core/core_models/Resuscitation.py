import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.Container import Container
from explain_core.core_models.Heart import Heart


class Resuscitation(BaseModel):
    # independent parameters
    chest_comp_freq: float = 100.0  # number of chest compressions per minute
    chest_comp_pres: float = 60.0  # pressure of the chest compressions in mmHg
    chest_comp_time: float = 1.0  # duration of chest compression
    chest_comp_targets: BaseModel = {}  # targets of the chest compressions with factor
    compressions: float = 15.0  # number of chest compressions per cycle
    ventilations: float = 2.0  # number of ventilations per cycle
    vent_freq: float = 30.0  # number of ventilations per minute during cycle
    vent_pres: float = 5.0  # pressure of the ventilations in mmHg
    vent_fio2: float = 0.21  # fio2 of the ventilations
    vent_insp_time: float = 1.0  # inspiration time of the ventilations
    async_ventilation: bool = (
        False  # flag whether the ventilation happen independent of the compressions
    )

    # dependent parameters
    cor_flow: float = 0.0  # coronary flow in l/min
    cor_o2_flow: float = 0.0  # coronary o2 flow in ml O2/min
    brain_flow: float = 0.0  # brain flow in l/min
    brain_o2_flow: float = 0.0  # brain o2 flow in l/min
    lvo: float = 0.0  # left ventricular output in l/min
    rvo: float = 0.0  # right ventricular output in l/min

    # local parameters
    _cpr_enabled: bool = False
    _comp_interval: float = 0.0
    _comp_duration: float = 0.0
    _comp_duration_counter: float = 0.0
    _comp_time_counter: float = 0.0
    _comp_pres: float = 0.0
    _comp_running: bool = False
    _comp_counter: int = 0
    _comp_pause_counter: float = 0.0
    _comp_pause_duration = 2.0
    _comp_paused: bool = False
    _comp_targets = {}
    _vent_counter: float = 0.0
    _vent_insp_counter: float = 0.0
    _vent_interval: float = 0.0
    _vent_running: bool = False

    _x: float = 0.0
    _x_step: float = 0.0
    _prev_el_max_factor: float = 0.0

    _flow_timer_counter: float = 0.0
    _flow_timer: float = 30.0
    _temp_brain_flow: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        for name, factor in self.chest_comp_targets.items():
            self._comp_targets[name] = {"m": self._model.models[name], "f": factor}

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        if not self._cpr_enabled:
            return

        # determine the interval between the breaths in seconds
        self._vent_interval = 60.0 / self.vent_freq
        self._comp_pause_duration = (
            self._vent_interval * self.ventilations + self.vent_insp_time
        )

        # is it time for a ventilation breath
        if self._vent_counter > self._vent_interval:
            self._vent_counter = 0.0
            self._vent_insp_counter = 0.0
            self._vent_running = True

        if self._comp_paused or self.async_ventilation:
            self._vent_counter += self._t

        if self._vent_running:
            self._model.models["MOUTH"].pres_ext = self.vent_pres
            self._vent_insp_counter += self._t

        if self._vent_insp_counter > self.vent_insp_time:
            self._vent_insp_counter = 0.0
            self._vent_running = False
            self._model.models["MOUTH"].pres_ext = 0.0

        # determine the interval between the compressions in seconds
        self._comp_interval = 60.0 / self.chest_comp_freq
        self._comp_duration = self.chest_comp_time
        if self._comp_duration > self._comp_interval:
            self._comp_duration = self._comp_interval
        self._x_step = math.pi / (self._comp_duration / self._t)
        self._comp_pres = 0

        # is it time for a compression?
        if self._comp_time_counter > self._comp_interval:
            # reset the timer
            self._comp_time_counter = 0.0
            # signal that the compression is starting
            self._comp_running = True
            # reset the compression duration counter
            self._comp_duration_counter = 0.0

        # start the compression
        if self._comp_running:
            # increase the compression timer
            self._comp_duration_counter += self._t
            # increase the compression pressure
            self._comp_pres = math.sin(self._x) * self.chest_comp_pres
            # self._model.models["CHEST_L"].pres_cc = self._comp_pres / 2.0
            # self._model.models["CHEST_R"].pres_cc = self._comp_pres / 2.0
            self._x += self._x_step

        # has the compression elapsed?
        if self._comp_duration_counter > self._comp_duration:
            # signal that the compression is not running anymore
            self._comp_running = False
            # reset the compression duration counter
            self._comp_duration_counter = 0.0
            # reset the compression pressure
            self._comp_pres = 0.0
            # reset the signal
            self._x = 0.0
            # increase the counter
            self._comp_counter += 1

        if self._comp_counter >= self.compressions and not self.async_ventilation:
            self._comp_counter = 0
            self._comp_paused = True
            self._vent_counter = self._vent_interval / 2.0

        if self._comp_paused:
            self._comp_pause_counter += self._t
            if self._comp_pause_counter > self._comp_pause_duration:
                self._comp_paused = False
                self._comp_pause_counter = 0.0
        else:
            self._comp_time_counter += self._t

        # apply the pressure to the targets
        for target in self._comp_targets.values():
            target["m"].pres_cc += target["f"] * self._comp_pres

        # calculate the flows
        self._temp_brain_flow += self._model.models["AAR_BR"].flow * self._t

        if self._flow_timer_counter > self._flow_timer:
            self._flow_timer_counter = 0.0
            self.brain_flow = (self._temp_brain_flow / self._flow_timer) * 60.0
            self._temp_brain_flow = 0.0

        self._flow_timer_counter += self._t

    def reset_counter(self):
        self._comp_counter = 0.0
        self._comp_duration_counter = 0.0
        self._vent_counter = 0.0
        self._vent_insp_counter = 0.0
        self._comp_pause_counter = 0.0
        self._comp_paused = False
        self._comp_running = False
        self._vent_running = False
        self._x = 0.0
        self._x_step = 0.0

    def set_heartrate(self, new_hr):
        if new_hr > 0:
            self._model.models["Heart"].heart_rate_override = True
            self._model.models["Heart"].heart_rate_forced = new_hr

    def release_heartrate(self):
        self._model.models["Heart"].heart_rate_override = False

    def start_cpr(self) -> None:
        self.cardiac_arrest(True)
        self.reset_counter()
        self._cpr_enabled = True

    def stop_cpr(self) -> None:
        self.cardiac_arrest(False)
        self._cpr_enabled = False

    def cardiac_arrest(self, state) -> None:
        if state:
            self.set_heartrate(0.1)
        else:
            self.release_heartrate()
