import math


class Circulation:
    # static properties
    model_type: str = "Circulation"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.blood_containing_components = []
        self.pulmonary_arteries = []
        self.pulmonary_veins = []
        self.systemic_arteries = []
        self.systemic_veins = []
        self.venpool_targets = []
        self.svr_targets = []
        self.pvr_targets = []
        self.pvr_change = 1.0
        self.svr_change = 1.0
        self.venpool_change = 1.0
        self.pulmartcomp_change = 1.0
        self.systartcomp_change = 1.0
        self.vencomp_change = 1.0
        self.svr_ans_factor = 1.0
        self.pvr_ans_factor = 1.0
        self.venpool_ans_factor = 1.0
        self.total_blood_volume = 0.0

        # dependent properties

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._ans_models = []
        self._svr_targets = []
        self._pvr_targets = []
        self._venpool_targets = []
        self._update_counter = 0.0
        self._update_window = 0.015

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # reference the ans models
        self._svr_targets = []
        for m in self.svr_targets:
            self._svr_targets.append(self._model_engine.models[m])

        self._pvr_targets = []
        for m in self.pvr_targets:
            self._pvr_targets.append(self._model_engine.models[m])

        self._venpool_targets = []
        for m in self.venpool_targets:
            self._venpool_targets.append(self._model_engine.models[m])

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        self._update_counter += self._t
        if self._update_counter > self._update_window:
            self._update_counter = 0.0

            # apply the ans factors
            for svrt in self._svr_targets:
                svrt.r_ans_factor = self.svr_ans_factor

            for pvrt in self._pvr_targets:
                pvrt.r_ans_factor = self.pvr_ans_factor

            for vpt in self._venpool_targets:
                vpt.u_vol_ans_factor = self.venpool_ans_factor
