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

            # translate the factors to change (10 = ref + 9xref  and 0.1 = ref - 0.9xref, 1 = ref + 0xref)
            effector["cum_mxe_high"] = effector["cum_mxe_high"] - 1.0
            effector["cum_mxe_low"] = effector["cum_mxe_low"] - 1.0

            print(effector["cum_mxe_high"], effector["cum_mxe_low"])

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

        # get the sensor values into the effectors
        for _sensor_name, _sensor in self._sensors.items():
            # get the firing rate
            _firing_rate = _sensor["input"].firing_rate

            # add the firing rate to the effector
            self._effectors[_sensor["effector"]]["cum_firing_rate"] += (
                _firing_rate * _sensor["weight"]
            )
            self._effectors[_sensor["effector"]]["cum_weight"] += _sensor["weight"]

        # calculate the effectors
        for _effector_name, _effector in self._effectors.items():
            # determine the total average firing rate
            _firing_rate_avg = _effector["cum_firing_rate"] / _effector["cum_weight"]

            # translate the average firing rate to the effect factor where 100 is the maximum, 0 is the minimum and 50 is the set value
            _effector_change = 0.0

            if _firing_rate_avg >= 50.0:
                # select the high
                _effector_change = (_effector["cum_mxe_high"] / 50.0) * (
                    _firing_rate_avg - 50.0
                )
            else:
                _effector_change = _effector["cum_mxe_low"] - (
                    _effector["cum_mxe_low"] / 50.0 * _firing_rate_avg
                )

            # transfer the effect factor to the target model
            setattr(
                _effector["target_model"], _effector["target_prop"], _effector_change
            )

            # reset the effect factor and number of effectors
            _effector["cum_firing_rate"] = 0.0
            _effector["cum_weight"] = 0.0
