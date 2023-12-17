from abc import ABC, abstractmethod


class BaseModel(ABC):
    # public model properties which are present in all model types
    name: str = ""
    description: str = ""
    is_enabled: bool = False
    model_type: str = ""
    dependencies: list = []

    # local properties
    _is_initialized: bool = False
    _model: object = {}  # reference to the current model
    _t: float = 0.0005  # model stepsize
    _mmhg_kpa = 1.0  # no converison

    def __init__(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

    def enable(self) -> None:
        # switch model on
        self.is_enabled = True

    def disable(self) -> None:
        # switch model off
        self.is_enabled = False

    def init_model(self, model: object) -> bool:
        # get a reference to the general model
        self._model = model

        # set the mmHg to kPa conversion factor
        self._mmhg_kpa = model.mmhg_kpa

        # get the modeling step size
        self._t = model.modeling_stepsize

        # flag that the model is initialized and return true
        self._is_initialized = True

        return self._is_initialized

    # this method is called during every model step by the model engine
    def step_model(self) -> None:
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # this abstract method has to be implemented in all children of the base class and contains the model logic
    @abstractmethod
    def calc_model(self) -> None:
        pass
