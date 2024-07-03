import math


class ExampleCustomModel:
    # public model properties which are present in all model types
    name: str = ""
    model_type: str = ""
    description: str = ""
    is_enabled: bool = False
    dependencies: list = []

    # local properties
    _model_engine: object = None
    _is_initialized: bool = False
    _t: float = 0.0005

    def __init__(self, model_ref, name: str = "", type: str = ""):
        # model name
        self.name = name

        # model type
        self.model_type = type

        # reference to the model engine
        self._model_engine = model_ref

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # get the modeling step size
        self._t = model.modeling_stepsize

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        pass
