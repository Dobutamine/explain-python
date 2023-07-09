from explain_core.base_models.BaseModel import BaseModel


class Metabolism(BaseModel):
    # independent variables
    vo2_factor: float = 1.0

    def calc_model(self) -> None:
        super().calc_model()

        # translate the VO2 in ml/kg/min to VO2 in mmol for this stepsize (assumption is 37 degrees and atmospheric pressure)
        vo2_step: float = (
            (0.039 * self.vo2 * self.vo2_factor * self._model.weight) / 60.0) * self._t

        for model, fvo2 in self.metabolic_active_models.items():
            # get the vol, tco2 and to2 from the blood compartment
            vol: float = self._model.models[model].vol
            to2: float = self._model.models[model].solutes['to2']
            tco2: float = self._model.models[model].solutes['tco2']

            # calculate the change in oxygen concentration in this step
            dto2: float = vo2_step * fvo2

            # calculate the new oxygen concentration in blood
            new_to2: float = (
                to2 * vol - dto2) / vol
            # guard against negative values
            if new_to2 < 0:
                new_to2 = 0

            # calculate the change in co2 concentration in this step
            dtco2 = vo2_step * fvo2 * self.resp_q

            # calculate the new co2 concentration in blood
            new_tco2: float = (
                tco2 * vol + dtco2) / vol
            # guard against negative values
            if new_tco2 < 0:
                new_tco2 = 0

            # store the new to2 and tco2
            self._model.models[model].solutes['to2'] = new_to2
            self._model.models[model].solutes['tco2'] = new_tco2
