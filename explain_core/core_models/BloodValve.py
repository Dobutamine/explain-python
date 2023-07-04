from explain_core.base_models.Valve import Valve
from explain_core.core_models.BloodCapacitance import BloodCapacitance


class BloodValve(Valve):

    model_comp_from: BloodCapacitance = {}
    model_comp_to: BloodCapacitance = {}

    def init_model(self, model: object) -> bool:
        # first init the parent classes
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        self.model_comp_from = self._model.Models[self.comp_from]
        self.model_comp_to = self._model.Models[self.comp_to]

        self._is_initialized = True
