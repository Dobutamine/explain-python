from explain_core.base_models.Resistor import Resistor


class GasResistor(Resistor):

    def init_model(self, model: object, comp_from=None, comp_to=None) -> bool:
        # first init the parent classes (Resistor)
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        if (comp_from is None or comp_to is None):
            self._model_comp_from = self._model.models[self.comp_from]
            self._model_comp_to = self._model.models[self.comp_to]
        else:
            self._model_comp_from = comp_from
            self._model_comp_to = comp_to

        return self._is_initialized
