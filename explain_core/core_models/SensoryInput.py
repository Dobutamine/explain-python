import math


class SensoryInput:
    # static properties
    model_type: str = "SensoryInput"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.receptor_type = ""
        self.input_site = ""
        self.input_parameter = ""
        self.min_value = self.set_value = self.max_value = 0.0
        self.max_firing_rate = 100.0
        self.set_firing_rate = 50.0
        self.min_firing_rate = 0.0
        self.time_constant = 1.0

        # dependent properties
        self.input_value = self.firing_rate = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._update_window = 0.015
        self._update_counter = 0.0
        self._t: float = model_ref.modeling_stepsize
        self._input_site = None
        self._gain = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the input site
        self._input_site = self._model_engine.models[self.input_site]

        # set the initial values
        self.current_value = getattr(self._input_site, self.input_parameter)
        self.firing_rate = self.set_firing_rate

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # for performance reasons the update is done only every 15 ms instead of every step
        self._update_counter += self._t
        if self._update_counter >= self._update_window:
            self._update_counter = 0.0

            # get the input value
            self.input_value = getattr(self._input_site, self.input_parameter)

            # calculate the activation value
            _activation = 0.0
            if self.input_value > self.max_value:
                _activation = self.max_value - self.set_value
            elif self.input_value < self.min_value:
                _activation = self.min_value - self.set_value
            else:
                _activation = self.input_value - self.set_value

            # calculate the gain
            if _activation > 0:
                # calculate the gain
                self._gain = (self.max_firing_rate - self.set_firing_rate) / (
                    self.max_value - self.set_value
                )
            else:
                # calculate the gain
                self._gain = (self.set_firing_rate - self.min_firing_rate) / (
                    self.set_value - self.min_value
                )

            # calculate the firing rate of the receptor
            _new_firing_rate = self.set_firing_rate + self._gain * _activation

            # incorporate the time constant to calculate the firing rate
            self.firing_rate = (
                self._update_window
                * ((1.0 / self.time_constant) * (-self.firing_rate + _new_firing_rate))
                + self.firing_rate
            )
