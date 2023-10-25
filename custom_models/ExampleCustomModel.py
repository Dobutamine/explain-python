import math
from explain_core.base_models.BaseModel import BaseModel


class ExampleCustomModel(BaseModel):
    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # do some custom model initialization

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # do some cystom model work
        pass
