class BloodValve:
    # static properties
    model_type: str = "BloodValve"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # initialize independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.no_flow: bool = True
        self.no_back_flow: bool = True
        self.comp_from: str = ""
        self.comp_to: str = ""
        self.r_for = self.r_for_factor = 1.0
        self.r_back = self.r_back_factor = 1.0
        self.r_k = self.r_k_factor = 1.0
        self.r_scaling_factor = 1.0
        self.p1_ext = self.p2_ext = 0.0
        self.p1_ext_factor = self.p2_ext_factor = 0.0

        # initialize dependent properties
        self.flow = self.flow_lmin = self.flow_lmin_avg = 0.0
        self.flow_forward_lmin = self.flow_backward_lmin = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False
        self._heart = None
        self._model_comp_from = None
        self._model_comp_to = None
        self._cum_forward_flow = 0.0
        self._cum_backward_flow = 0.0
        self._flow_counter = 0.0
        self._flow_mov_avg_counter = 0.0
        self._alpha = 0.05
        self._analytics_timer = 0.0
        self._analytics_window = 2.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the connected components
        if type(self.comp_from) == str:
            self._model_comp_from = self._model_engine.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) == str:
            self._model_comp_to = self._model_engine.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to

        # reference to the heart
        self._heart = self._model_engine.models["Heart"]

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        #  get the pressures of the connected model components
        _p1 = self._model_comp_from.pres + self.p1_ext * self.p1_ext_factor
        _p2 = self._model_comp_to.pres + self.p2_ext * self.p2_ext_factor

        # reset the external pressures
        self.p1_ext = 0
        self.p2_ext = 0

        # calculate the resistances
        _r_for_base = self.r_for * self.r_scaling_factor
        _r_back_base = self.r_back * self.r_scaling_factor
        _r_k_base = self.r_k * self.r_scaling_factor

        _r_for = _r_for_base + (self.r_for_factor - 1) * _r_for_base
        _r_back = _r_back_base + (self.r_back_factor - 1) * _r_back_base
        _r_k = _r_k_base + (self.r_k_factor - 1) * _r_k_base

        # make the resistances flow dependent
        _r_for += _r_k * self.flow * self.flow
        _r_back += _r_k * self.flow * self.flow

        # guard for too small resistances
        _r_for = max(_r_for, 20.0)
        _r_back = max(_r_back, 20.0)

        # calculate flow
        if self.no_flow or (_p1 <= _p2 and self.no_back_flow):
            self.flow = 0.0
        elif _p1 > _p2:
            # forward flow
            self.flow = (_p1 - _p2) / _r_for
            self._cum_forward_flow += self.flow * self._t
        else:
            # back flow
            self.flow = (_p1 - _p2) / _r_back
            self._cum_backward_flow += self.flow * self._t

        # analyze current state
        self.analyze()

        # Update the volumes of the model components connected by this resistor
        vol_not_removed = 0.0
        if self.flow > 0:
            # Flow is from comp_from to comp_to
            vol_not_removed = self._model_comp_from.volume_out(self.flow * self._t)
            # If not all volume can be removed from the model component, transfer the remaining volume to the other model component
            # This is undesirable but it is better than having a negative volume
            self._model_comp_to.volume_in(
                self.flow * self._t - vol_not_removed, self._model_comp_from
            )
        elif self.flow < 0:
            # Flow is from comp_to to comp_from
            vol_not_removed = self._model_comp_to.volume_out(-self.flow * self._t)
            # If not all volume can be removed from the model component, transfer the remaining volume to the other model component
            # This is undesirable but it is better than having a negative volume
            self._model_comp_from.volume_in(
                -self.flow * self._t - vol_not_removed, self._model_comp_to
            )

    def reconnect(self, comp_from, comp_to):
        # store the connectors
        self.comp_from = comp_from
        self.comp_to = comp_to

        # get a reference to the connected components
        if type(self.comp_from) == str:
            self._model_comp_from = self._model_engine.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) == str:
            self._model_comp_to = self._model_engine.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to

    def analyze(self):
        self._flow_counter += self._t
        self._analytics_timer += self._t

        if (
            self._heart.ncc_ventricular == 1
            or self._analytics_timer > self._analytics_window
        ):
            self._analytics_timer = 0.0
            self.flow_forward_lmin = (
                self._cum_forward_flow / self._flow_counter
            ) * 60.0
            self.flow_backward_lmin = (
                self._cum_backward_flow / self._flow_counter
            ) * 60.0
            self.flow_lmin = self.flow_forward_lmin + self.flow_backward_lmin
            self._cum_forward_flow = 0.0
            self._cum_backward_flow = 0.0
            self._flow_counter = 0.0

            # Prevent startup averaging problems
            self._flow_mov_avg_counter += 1
            if self._flow_mov_avg_counter > 5:
                self._flow_mov_avg_counter = 5
                self.flow_lmin_avg = (
                    self._alpha * self.flow_lmin
                    + (1 - self._alpha) * self.flow_lmin_avg
                )
