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
        pass

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
            self._model_engine.models["Ventilator"].set_ventilator_pc(
                16.0, 5.0, 50, 0.4, 10.0
            )
        self._model_engine.models["Ventilator"].vent_sync = True
        # for (let [comp_target, force] of Object.entries(
        #   self.chest_comp_targets
        # )) {
        #   self._model_engine.models[comp_target].pres_cc = 0.0;
        # }
