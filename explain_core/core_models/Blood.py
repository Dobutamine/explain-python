import math
from explain_core.base_models.BaseModel import BaseModel


class Blood(BaseModel):

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # find all models containing blood and set it's solutes
        for model in self._model.models.values():
            if model.model_type == "BloodCapacitance" or model.model_type == "BloodTimeVaryingElastance":
                # fill the solutes
                model.solutes = {**self.solutes}
                model.acidbase = {**self.acidbase}
                model.oxy = {**self.oxy}

        return self._is_initialized
