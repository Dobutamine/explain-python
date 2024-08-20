import math


class Resuscitation:
    # static properties
    model_type: str = "Resuscitation"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.ventilator = []
        self.breathing = []
        self.compressions = 15.0
        self.chest_comp_enabled = True
        self.chest_comp_freq = 100.0
        self.chest_comp_pres = 10.0
        self.chest_comp_time = 1.0
        self.chest_comp_targets = {"THORAX": 0.1}
        self.chest_comp_cont = False

        self.ventilations = 2.0
        self.vent_freq = 30.0
        self.vent_pres_pip = 16.0
        self.vent_pres_peep = 5.0
        self.vent_insp_time = 1.0
        self.vent_fio2 = 0.21
        self.async_ventilation = False
        self.forced_hr = False

        # dependent properties
        self.chest_comp_force = 0.0
        self.overriden_hr = 30.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._comp_timer = 0.0
        self._comp_counter = 0.0
        self._comp_pause = False
        self._comp_pause_timer = 0.0
        self._vent_timer = 0.0
        self._analytics_timer = 0.0

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
        # // y(t) = A sin(2PIft+o)
        # A = amplitude, f = frequency in Hz, t is time, o = phase shift
        self._model_engine.models["Heart"].heart_rate_override = self.forced_hr
        if (self.forced_hr):
            self._model_engine.models["Heart"].heart_rate_forced = float(self.overriden_hr)

        if (self.cpr_enabled):
            f = self.chest_comp_freq / 60.0
            a = self.chest_comp_pres / 2.0
            if (self.chest_comp_cont):
                self._comp_pause = False
                self._vent_timer += self._t
                if (self._vent_timer > self.vent_insp_time * 2.1):
                    self._vent_timer = 0.0
                    self._model_engine.models["Ventilator"].trigger_breath()


            if not self._comp_pause:
                self.chest_comp_force = a * math.sin(2 * math.pi * f * self._comp_timer - 0.5 * math.pi) + a
                self._comp_timer += self._t
                self._model_engine.models["Heart"].ncc_resus += 1.0


            if (self._comp_timer > 60.0 / self.chest_comp_freq):
                self._comp_timer = 0.0
                self._comp_counter += 1
                self._model_engine.models["Heart"].ncc_resus = 0.0


            if (self._comp_counter == self.compressions and not self.chest_comp_cont):
                self._model_engine.models["Ventilator"].trigger_breath()
                self._vent_timer = 0.0
                self._comp_counter = 0
                self._comp_pause_timer = 0.0
                self._comp_pause = True


            if (self._comp_pause and not self.chest_comp_cont):
                self._comp_pause_timer += self._t
                self._vent_timer += self._t
                if (self._vent_timer > self.vent_insp_time * 2.1):
                    self._vent_timer = 0.0
                    self._model_engine.models["Ventilator"].trigger_breath()

            if (self._comp_pause_timer > self.ventilations * self.vent_insp_time * 2.0):
                self._comp_pause = False
                self._vent_timer = 0.0


            for key, value in self.chest_comp_targets.items():
                self._model_engine.models[key].pres_cc = float(self.chest_comp_force * value)

    def switch_cpr(self, state):
        if state:
            self._model_engine.models["Ventilator"].set_ventilator_pc(
                self.vent_pres_pip,
                self.vent_pres_peep,
                self.vent_freq,
                self.vent_insp_time,
                10.0,
            )
            self._model_engine.models["Ventilator"].switch_ventilator(True)
            self._model_engine.models["Ventilator"].vent_sync = False
            self._model_engine.models["Breathing"].switch_breathing(False)
            self.cpr_enabled = True
        else:
            self.cpr_enabled = False
            self._model_engine.models["Ventilator"].set_ventilator_pc(16.0, 5.0, 50, 0.4, 10.0)

        self._model_engine.models["Ventilator"].vent_sync = True

