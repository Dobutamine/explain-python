from explain_core.base_models.BaseModel import BaseModel


class Lymph(BaseModel):
    # local variables which determine how often the acidbase and oxygenation is calculated. For performance reasons this is less often.
    _update_counter = 0.0
    _update_interval = 0.015

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # find all models containing lymph and set it's solutes, acidbase and oxygenation variables
        for model in self._model.models.values():
            if (
                model.model_type == "LymphCapacitance"
            ):
                # fill the solutes
                model.solutes = {**self.solutes}
                model.aboxy = {**self.aboxy}

        return self._is_initialized

    def set_solute_concentration(self, solute_name: str, solute_conc):
        self.solutes[solute_name]: float = solute_conc

        for model in self._model.models.values():
            if (
                model.model_type == "LymphCapacitance"
            ):
                # fill the solutes
                model.solutes[solute_name] = solute_conc

    def set_aboxy_concentration(self, solute_name: str, solute_conc):
        self.aboxy[solute_name]: float = solute_conc

        for model in self._model.models.values():
            if (
                model.model_type == "LymphCapacitance"
            ):
                # fill the solutes
                model.aboxy[solute_name] = solute_conc
