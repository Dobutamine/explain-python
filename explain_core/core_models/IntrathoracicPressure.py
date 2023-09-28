from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.Container import Container

class IntrathoracicPressure(BaseModel):

    # objects
    thorax: Container = {}


    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the thoracic container
        self.thorax = self._model.models["THORAX"]
