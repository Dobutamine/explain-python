class BaseModel:
    # public model properties which are present in all model types
    name: str = ""
    description: str = ""
    is_enabled: bool = False
    model_type: str = ""
    dependencies: list = []

    # non public properties
    _is_initialized: bool = False

    # reference to all models
    _model: object = {}
    _t: float = 0.0005

    def __init__(self, **args: dict[str, any]):
        # set the values of the independent properties as arguments of the model
        for key, value in args.items():
            setattr(self, key, value)

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False

    def init_model(self, model: object) -> bool:
        # get a reference to the model
        self._model = model

        # get the modeling step size
        self._t = model.modeling_stepsize

        # flag that the model is initialized
        self._is_initialized = True

        # return whether or not successful
        return self._is_initialized

    def step_model(self) -> None:
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # this method should be implemented in all children of the base class
    def calc_model(self) -> None:
        pass
