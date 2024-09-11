class AfferentPathway:
    # static properties
    model_type: str = "AfferentPathway"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # Independent properties
        self.name = name
        self.description = ""
        self.is_enabled = False
        self.dependencies = []

        self.input = ""
        self.min_value = 0.0
        self.set_value = 0.0
        self.max_value = 0.0
        self.time_constant = 1.0

        # Dependent properties
        self.input_value = 0.0
        self.firing_rate = 0.0

        # Local properties
        self._model_engine = model_ref
        self._is_initialized = False
        self._update_window = 0.015
        self._update_counter = 0.0
        self._max_firing_rate = 1.0
        self._set_firing_rate = 0.5
        self._min_firing_rate = 0.0
        self._t = model_ref.modeling_stepsize
        self._input_site = None
        self._input_prop = ""
        self._gain = 0.0


    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # Get a reference to the input site
        model, prop = self.input.split(".")
        self._input_site = self._model_engine.models[model]
        self._input_prop = prop

        # Set the initial values
        self.current_value = getattr(self._input_site, self._input_prop)
        self.firing_rate = self._set_firing_rate

        # Flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # For performance reasons, the update is done only every 15 ms instead of every step
        self._update_counter += self._t
        if self._update_counter >= self._update_window:
            self._update_counter = 0.0

            # Get the input value
            self.input_value = getattr(self._input_site, self._input_prop)

            # Calculate the activation value
            if self.input_value > self.max_value:
                _activation = self.max_value - self.set_value
            elif self.input_value < self.min_value:
                _activation = self.min_value - self.set_value
            else:
                _activation = self.input_value - self.set_value

            # Calculate the gain
            if _activation > 0:
                # Calculate the gain for positive activation
                self._gain = (self._max_firing_rate - self._set_firing_rate) / (self.max_value - self.set_value)
            else:
                # Calculate the gain for negative activation
                self._gain = (self._set_firing_rate - self._min_firing_rate) / (self.set_value - self.min_value)

            # Calculate the firing rate of the receptor
            _new_firing_rate = self._set_firing_rate + self._gain * _activation

            # Incorporate the time constant to calculate the firing rate
            self.firing_rate = self._update_window * ((1.0 / self.time_constant) * (-self.firing_rate + _new_firing_rate)) + self.firing_rate
