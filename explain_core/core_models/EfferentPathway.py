class EfferentPathway:
    # Static properties
    model_type = "EfferentPathway"
    model_interface = [
        {
            "target": "is_enabled",
            "caption": "is enabled",
            "type": "boolean",
            "default": True,
        },
    ]

    def __init__(self, model_ref: object, name: str = ""):
        # Independent properties
        self.name = name
        self.description = ""
        self.is_enabled = False
        self.dependencies = []
        self.target = ""
        self.mxe_high = 0.0
        self.mxe_low = 0.0
        self.tc = 0.0

        # Dependent properties
        self.firing_rate = 0.5
        self.effector_change = 1.0

        # Local properties
        self._model_engine = model_ref
        self._is_initialized = False
        self._target_model = {}
        self._target_prop = ""
        self._t = model_ref.modeling_stepsize
        self._update_window = 0.015
        self._update_counter = 0.0
        self._avg_counter = 1.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # Find the target
        model, prop = self.target.split(".")
        self._target_model = self._model_engine.models[model]
        self._target_prop = prop

        # Flag that the model is initialized
        self._is_initialized = True

    # This method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # Actual model calculations are done here
    def calc_model(self):
        self._update_counter += self._t
        if self._update_counter >= self._update_window:
            self._update_counter = 0.0

            # Determine the total average firing rate
            firing_rate_avg = (
                self.firing_rate / self._avg_counter
                if self._avg_counter > 0.0
                else self.firing_rate
            )

            # Translate the average firing rate to the effect factor
            if firing_rate_avg >= 0.5:
                effector_change = 1.0 + ((self.mxe_high - 1.0) / 0.5) * (firing_rate_avg - 0.5)
            else:
                effector_change = self.mxe_low + ((1.0 - self.mxe_low) / 0.5) * firing_rate_avg

            # Incorporate the time constant for the effector change
            new_effector_change = (
                self._update_window
                * ((1.0 / self.tc) * (-self.effector_change + effector_change))
                + self.effector_change
            )

            self.effector_change = new_effector_change

            # Transfer the effect factor to the target model
            setattr(self._target_model, self._target_prop, new_effector_change)

            # Reset the effect factor and number of effectors
            self.firing_rate = 0.5
            self._avg_counter = 0.0

    # Set effector firing rate
    def update_effector(self, firing_rate, weight):
        self.firing_rate += (firing_rate - 0.5) * weight
        self._avg_counter += 1.0
