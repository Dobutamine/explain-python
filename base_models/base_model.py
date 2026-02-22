from abc import ABC, abstractmethod


class BaseModel(ABC):
    # define class-level properties that are common to all models
    model_type = "base"

    def __init__(self, model_ref = {}, name=None):
        # initialization of the base model properties
        self.name = name # unique name of the component, which can be used to reference it in the model
        self.description = "" # optional description of the component
        self.is_enabled = False # flag to indicate whether the component is active in the model, default is False. This can be used to enable or disable components without removing them from the model.
        self.model_ref = model_ref # reference to the overall model, which can be used to access other components and global properties

    def init_model(self, args=None):
        # model property initialization from args dictonary
        if args is None:
            return
        if not isinstance(args, dict):
            raise TypeError("args must be a dict")

        for key, value in args.items():
            if not hasattr(self, key):
                raise AttributeError(f"Unknown property: {key}")
            setattr(self, key, value)

    def step_model(self):
        # default step_model implementation that can be overridden by subclasses
        if not self.is_enabled:
            return
        
        self.calc_model()

    @abstractmethod
    def calc_model(self):
        raise NotImplementedError("calc_model must be implemented by subclasses")
