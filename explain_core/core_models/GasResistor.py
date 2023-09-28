from explain_core.base_models.Resistor import Resistor


class GasResistor(Resistor):

    def init_model(self, model: object,) -> bool:
        # first init the parent classes (Resistor)
        super().init_model(model)

        return self._is_initialized
