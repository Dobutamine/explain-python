from explain_core.base_models.BaseModel import BaseModel
from explain_core.functions.Acidbase import calc_acidbase_from_tco2
from explain_core.functions.Oxygenation import calc_oxygenation_from_to2


class Blood(BaseModel):

    # local variables which determine how often the acidbase and oxygenation is calculated. For performance reasons this is less often.
    _update_counter = 0.0
    _update_interval = 0.015

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # find all models containing blood and set it's solutes, acidbase and oxygenation variables
        for model in self._model.models.values():
            if model.model_type == "BloodCapacitance" or model.model_type == "BloodTimeVaryingElastance":
                # fill the solutes
                model.solutes = {**self.solutes}
                model.aboxy = {**self.aboxy}
                # calculate the to2 from the spo2 and hemoglobin
                model.aboxy['to2'] = ((1.36 * (model.aboxy['hemoglobin'] / 0.6206)
                                       * model.aboxy['so2'] / 100.0) * 10.0) / 25.5

        return self._is_initialized

    def calc_model(self) -> None:
        if self._update_counter > self._update_interval:
            self._update_counter = 0.0
            for c in self.aboxy['comps']:
                calc_acidbase_from_tco2(self._model.models[c])
                # calculate the po2 and pco2 in the blood compartments
                result_ab = calc_acidbase_from_tco2(self._model.models[c])
                if result_ab is not None:
                    self._model.models[c].aboxy['ph'] = result_ab['ph']
                    self._model.models[c].aboxy['pco2'] = result_ab['pco2']
                    self._model.models[c].aboxy['hco3'] = result_ab['hco3']
                    self._model.models[c].aboxy['be'] = result_ab['be']
                    self._model.models[c].aboxy['sid_app'] = result_ab['sid_app']

                result_oxy = calc_oxygenation_from_to2(self._model.models[c])
                if result_oxy is not None:
                    self._model.models[c].aboxy['po2'] = result_oxy['po2']
                    self._model.models[c].aboxy['so2'] = result_oxy['so2']

        self._update_counter += self._t
