class BaseModel:
    # public model properties which are present in all model types
    name = ""
    description = ""
    is_enabled = False
    model_type = ""
    dependencies = []

    # non public properties
    _is_initialized = False

    # reference to all models
    _model = {}

    def __init__(self, **args):
        # set the values of the independent properties as arguments of the model
        for key, value in args.items():
            setattr(self, key, value)

    def init_model(self, model):
        # get a reference to the model
        self._model = model

        # flag that the model is initialized
        self._is_initialized = True

    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    def calc_model(self):
        pass
