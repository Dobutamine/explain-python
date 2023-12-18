from explain_core.base_models.BaseModel import BaseModel
from explain_core.functions.BloodComposition import set_blood_composition


class Blood(BaseModel):
    # independent variables
    solutes: dict[str, float] = {}
    aboxy: dict[str, float] = {}

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

    # implement the calc_model method as this derives from the BaseModel class
    def calc_model(self) -> None:
        pass

    # reset the total blood volume
    def set_total_blood_volume(self, new_blood_volume: float) -> None:
        current_blood_volume = self.get_total_blood_volume(output=False)
        new_blood_volume = new_blood_volume
        # divide the new blood volume over all blood holding capacitances
        # while abs(current_blood_volume - new_blood_volume) > 0.001:
        for model in self._model.models.values():
            if "BloodCapacitance" in model.model_type:
                if model.is_enabled:
                    try:
                        # calculate the current fraction of the blood volume in this blood containing capacitance
                        current_fraction = model.vol / current_blood_volume

                        v = model.vol
                        vu = model.u_vol
                        # calculate the new fraction
                        f = 0.0
                        if model.vol > 0.0:
                            f = model.u_vol / model.vol

                        # add the same fraction of the desired volume change to the blood containing capacitance
                        model.vol += current_fraction * (
                            new_blood_volume - current_blood_volume
                        )

                        # change the unstressed volume
                        model.u_vol = model.vol * f

                        # guard for negative volumes
                        if model.vol < 0.0:
                            model.vol = 0.0
                    except:
                        current_fraction = 0

            if "BloodTimeVaryingElastance" in model.model_type:
                if model.is_enabled:
                    try:
                        # calculate the current fraction of the blood volume in this blood containing capacitance
                        current_fraction = model.vol / current_blood_volume

                        v = model.vol
                        vu = model.u_vol
                        # calculate the new fraction
                        f = 0.0
                        if model.vol > 0.0:
                            f = model.u_vol / model.vol

                        # add the same fraction of the desired volume change to the blood containing capacitance
                        model.vol += current_fraction * (
                            new_blood_volume - current_blood_volume
                        )

                        # change the unstressed volume
                        model.u_vol = model.vol * f

                        # guard for negative volumes
                        if model.vol < 0.0:
                            model.vol = 0.0
                    except:
                        current_fraction = 0

    # return the total blood volume
    def get_total_blood_volume(self, output=True) -> float:
        total_blood_volume: float = 0.0

        for model in self._model.models.values():
            if "Blood" in model.model_type:
                if model.is_enabled:
                    try:
                        total_blood_volume += model.vol
                    except:
                        total_blood_volume += 0.0

            # if "Blood" in model.model_type and model.is_enabled:
            #     total_blood_volume += model.vol

        if output:
            print(
                f"Total blood volume = {total_blood_volume * 1000.0} ml ({total_blood_volume * 1000.0 / self._model.weight} ml/kg)"
            )

        return total_blood_volume

    # set the blood composition of a blood containing model
    def set_blood_composition(self, bc: dict) -> None:
        if "Blood" in bc.model_type:
            set_blood_composition(bc)

    # set the concentration of a solute in the blood
    def set_solute_concentration(self, solute_name: str, solute_conc: float) -> None:
        self.solutes[solute_name]: float = solute_conc

        for model in self._model.models.values():
            if (
                model.model_type == "BloodCapacitance"
                or model.model_type == "BloodTimeVaryingElastance"
            ):
                # fill the solutes
                model.solutes[solute_name] = solute_conc

    # set the concentration of a aboxy solute in the blood
    def set_aboxy_concentration(self, solute_name: str, solute_conc: float) -> None:
        self.aboxy[solute_name]: float = solute_conc

        for model in self._model.models.values():
            if (
                model.model_type == "BloodCapacitance"
                or model.model_type == "BloodTimeVaryingElastance"
            ):
                # fill the solutes
                model.aboxy[solute_name] = solute_conc
