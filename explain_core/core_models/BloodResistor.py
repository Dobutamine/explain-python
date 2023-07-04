from explain_core.base_models.Resistor import Resistor


class BloodResistor(Resistor):

    def init_model(self, model: object) -> bool:
        # first init the parent classes (Resistor)
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        self._model_comp_from = self._model.models[self.comp_from]
        self._model_comp_to = self._model.models[self.comp_to]

        return self._is_initialized
