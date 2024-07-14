import math


class Ans:
    # static properties
    model_type: str = "Ans"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.ans_active = True
        # sensory inputs
        self.sensors = (
            [{"name": "cr pco2", "input": "CR_PCO2", "effector": "mv", "weight": 1.0}],
        )

        # effectors
        self.effectors = {
            "mv": {
                "target": "Breathing.mv_ans_factor",
                "cum_mxe_high": 10.0,
                "cum_mxe_low": 0.1,
                "tc": 5.0,
                "effector_change": 0.0,
            }
        }

        # dependent properties

        # local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False
        self._sensors = {}
        self._effectors = {}
        self._update_window = 0.015
        self._update_counter = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
        for key, value in args.items():
            setattr(self, key, value)

        # initialize the effectors with references to the necessary models
        for effector_name, effector in self.effectors.items():
            target = effector["target"].split(".")

            self._effectors[effector_name] = {
                "target_model": self._model_engine.models[target[0]],
                "target_prop": target[1],
                "cum_mxe_high": effector["cum_mxe_high"],
                "cum_mxe_low": effector["cum_mxe_low"],
                "cum_firing_rate": effector["cum_firing_rate"],
                "cum_weight": effector["cum_firing_rate"],
                "tc": effector["tc"],
                "effector_change": effector["effector_change"],
            }

        # initialize the sensors with references to the necessary models
        for sensor in self.sensors:
            self._sensors[sensor["name"]] = {
                "input": self._model_engine.models[sensor["input"]],
                "effector": sensor["effector"],
                "weight": sensor["weight"],
                "sensor_activity": 0.0,
            }

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        self._update_counter += self._t
        if self._update_counter >= self._update_window:
            self._update_counter = 0.0

        # Get the sensor values into the effectors
        for _sensor_name, _sensor in self._sensors.items():
            # Get the firing rate
            _firing_rate = _sensor["input"].firing_rate

            # Fetch the effector name and its weight once
            effector_name = _sensor["effector"]
            sensor_weight = _sensor["weight"]

            # Access the effector dictionary once
            _effector = self._effectors[effector_name]

            # Add the firing rate to the effector
            _effector["cum_firing_rate"] += _firing_rate * sensor_weight
            _effector["cum_weight"] += sensor_weight

        # calculate the effectors
        for _effector_name, _effector in self._effectors.items():
            cum_weight = _effector["cum_weight"]
            cum_firing_rate = _effector["cum_firing_rate"]
            cum_mxe_high = _effector["cum_mxe_high"]
            cum_mxe_low = _effector["cum_mxe_low"]
            effector_change_current = _effector["effector_change"]
            tc = _effector["tc"]

            # Determine the total average firing rate
            _firing_rate_avg = (
                50.0 if cum_weight == 0.0 else cum_firing_rate / cum_weight
            )

            # Translate the average firing rate to the effect factor
            if _firing_rate_avg >= 50.0:
                _effector_change = 1.0 + ((cum_mxe_high - 1.0) / 50.0) * (
                    _firing_rate_avg - 50.0
                )
            else:
                _effector_change = (
                    cum_mxe_low + (1.0 - cum_mxe_low) / 50.0 * _firing_rate_avg
                )

            # Incorporate the time constant for the effector change
            new_effector_change = (
                self._update_window
                * ((1.0 / tc) * (-effector_change_current + _effector_change))
                + effector_change_current
            )

            _effector["effector_change"] = new_effector_change

            # Transfer the effect factor to the target model
            setattr(
                _effector["target_model"], _effector["target_prop"], new_effector_change
            )

            # Reset the effect factor and number of effectors
            _effector["cum_firing_rate"] = 0.0
            _effector["cum_weight"] = 0.0
