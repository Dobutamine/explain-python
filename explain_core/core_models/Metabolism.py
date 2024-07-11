import math


class Metabolism:
    # static properties
    model_type: str = "Metabolism"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.vo2 = 6.5
        self.vo2_factor = 1.0
        self.vo2_scaling_factor = 1.0
        self.resp_q = 0.8
        self.resp_q_scaling_factor = 1.0
        self.body_temp = 37
        self.metabolic_active_models = {
            "RLB": 0.15,
            "INT": 0.15,
            "LS": 0.1,
            "KID": 0.1,
            "RUB": 0.1,
            "AA": 0.005,
            "AD": 0.01,
            "BR": 0.453,
        }

        # dependent properties

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize

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
        # translate the VO2 in ml/kg/min to VO2 in mmol for this stepsize (assumption is 37 degrees and atmospheric pressure)
        vo2_step = (
            (
                0.039
                * self.vo2
                * self.vo2_factor
                * self.vo2_scaling_factor
                * self._model_engine.weight
            )
            / 60.0
        ) * self._t

        for model, fvo2 in self.metabolic_active_models.items():
            # get the vol, tco2 and to2 from the blood compartment
            vol = self._model_engine.models[model].vol
            to2 = self._model_engine.models[model].aboxy["to2"]
            tco2 = self._model_engine.models[model].aboxy["tco2"]

            # calculate the change in oxygen concentration in this step
            dto2 = vo2_step * fvo2

            # calculate the new oxygen concentration in blood
            new_to2 = (to2 * vol - dto2) / vol

            # guard against negative values
            if new_to2 < 0:
                new_to2 = 0

            # calculate the change in co2 concentration in this step
            dtco2 = vo2_step * fvo2 * self.resp_q * self.resp_q_scaling_factor

            # calculate the new co2 concentration in blood
            new_tco2 = (tco2 * vol + dtco2) / vol

            # guard against negative values
            if new_tco2 < 0:
                new_tco2 = 0

            # store the new to2 and tco2
            self._model_engine.models[model].aboxy["to2"] = new_to2
            self._model_engine.models[model].aboxy["tco2"] = new_tco2

    def set_body_temp(self, new_temp):
        self.body_temp = new_temp
        for model in self._model_engine.models:
            if (
                model.model_type == "BloodCompartment"
                or model.model_type == "BloodTimeVaryingElastance"
            ):
                model.temp = new_temp
