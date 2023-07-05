from explain_core.base_models.Valve import Valve
from explain_core.core_models.BloodCapacitance import BloodCapacitance


class BloodValve(Valve):

    def init_model(self, model: object) -> bool:
        # first init the parent classes
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        self._model_comp_from = self._model.models[self.comp_from]
        self._model_comp_to = self._model.models[self.comp_to]

        # flag that the valve is initialized
        self._is_initialized = True

        return self._is_initialized
