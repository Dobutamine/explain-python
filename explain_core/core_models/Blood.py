from explain_core.base_models.BaseModel import BaseModel
from explain_core.functions.BloodComposition import set_blood_composition


class Blood(BaseModel):
    # local variables which determine how often the acidbase and oxygenation is calculated. For performance reasons this is less often.
    _update_counter = 0.0
    _update_interval = 0.015

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # find all models containing blood and set it's solutes, acidbase and oxygenation variables
        for model in self._model.models.values():
            if (
                model.model_type == "BloodCapacitance"
                or model.model_type == "BloodTimeVaryingElastance"
            ):
                # fill the solutes
                model.solutes = {**self.solutes}
                model.aboxy = {**self.aboxy}
                # calculate the to2 from the spo2 and hemoglobin
                model.aboxy["to2"] = (
                    (
                        1.36
                        * (model.aboxy["hemoglobin"] / 0.6206)
                        * model.aboxy["so2"]
                        / 100.0
                    )
                    * 10.0
                ) / 25.5

        return self._is_initialized

    def set_blood_composition(self, bc) -> bool:
        if "Blood" in bc.model_type:
            set_blood_composition(bc)
            return True

        return False

    def set_solute_concentration(self, solute_name: str, solute_conc):
        self.solutes[solute_name]: float = solute_conc

        for model in self._model.models.values():
            if (
                model.model_type == "BloodCapacitance"
                or model.model_type == "BloodTimeVaryingElastance"
            ):
                # fill the solutes
                model.solutes[solute_name] = solute_conc

    def set_aboxy_concentration(self, solute_name: str, solute_conc):
        self.aboxy[solute_name]: float = solute_conc

        for model in self._model.models.values():
            if (
                model.model_type == "BloodCapacitance"
                or model.model_type == "BloodTimeVaryingElastance"
            ):
                # fill the solutes
                model.aboxy[solute_name] = solute_conc
