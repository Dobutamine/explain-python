import math

from explain_core.helpers.BloodComposition import set_blood_composition


class Blood:
    # static properties
    model_type: str = "Blood"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.blood_containing_components = []
        self.acidbase_components = []
        self.solutes = None
        self.aboxy = None
        self.viscosity = 6.0

        # dependent properties

        # local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False
        self._update_window = 0.015
        self._update_counter = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
        for key, value in args.items():
            setattr(self, key, value)

        # set the aboxy and solutes if not set by the state which is loaded
        for model in self.blood_containing_components:
            if not hasattr(self._model_engine.models[model], "aboxy"):
                self._model_engine.models[model].aboxy = {**self.aboxy}
            if not hasattr(self._model_engine.models[model], "solutes"):
                self._model_engine.models[model].solutes = {**self.solutes}

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

            for m in self.acidbase_components:
                # update the blood composition
                set_blood_composition(self._model_engine.models[m])
