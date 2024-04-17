import math
from explain_core.base_models.Capacitance import Capacitance


class Pump(Capacitance):
    # do some custom model initialization
    # independent variable
    flow: float = 0.00025

    # dependent variable
    resistance: float = 0.0
    
    # define object which hold references to a BloodCapacitance or TimeVaryingElastance
    _model_comp_from: Capacitance = {}
    _model_comp_to: Capacitance = {}

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        if type(self.comp_from) is str:
            self._model_comp_from = self._model.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) is str:
            self._model_comp_to = self._model.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # do some cystom model work
        _p1 = self._model_comp_from.pres
        _p2 = self._model_comp_to.pres

        self.resistance = (_p1 - _p2)/self.flow

        # now update the volumes of the model components which are connected by this resistor
        if self.flow > 0:
            # flow is from comp_from to comp_to
            vol_not_removed: float = self._model_comp_from.volume_out(
                self.flow * self._t
            )

            self._model_comp_to.volume_in(
                (self.flow * self._t) - vol_not_removed
            )
            return

    def set_flow(self, new_flow):
        self.flow = new_flow # in mmHg

