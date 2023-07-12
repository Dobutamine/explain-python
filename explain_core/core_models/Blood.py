import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.helpers.BrentRootFinding import brent_root_finding
from explain_core.helpers.Acidbase import calc_acidbase_from_tco2
from explain_core.helpers.Oxygenation import calc_oxygenation_from_to2


class Blood(BaseModel):

    # local variables
    _update_counter = 0.0
    _update_interval = 0.015

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # find all models containing blood and set it's solutes
        for model in self._model.models.values():
            if model.model_type == "BloodCapacitance" or model.model_type == "BloodTimeVaryingElastance":
                # fill the solutes
                model.solutes = {**self.solutes}
                model.aboxy = {**self.aboxy}

        return self._is_initialized

    def calc_model(self) -> None:
        if self._update_counter > self._update_interval:
            self._update_counter = 0.0
            for c in self.aboxy['comps']:
                calc_acidbase_from_tco2(self._model.models[c])
                calc_oxygenation_from_to2(self._model.models[c])
        self._update_counter += self._t
