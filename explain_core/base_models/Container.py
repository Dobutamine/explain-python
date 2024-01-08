import math
from explain_core.base_models.Capacitance import Capacitance


# the container class is a child of the capacitance class
class Container(Capacitance):
    # independent variables unique for the container class
    vol_extra: float = 0.0

    # implement the calc_model method (overriding the method from the parent class)
    def calc_model(self) -> None:
        # set the volume
        self.vol = self.vol_extra

        # get the current volume from all contained models
        for c in self.contained_components:
            self.vol += self._model.models[c].vol

        # calculate the elastance, unstressed volume and non-linear elastance factor and pressure
        super().calc_model()

        # transfer the pressures to the models the container contains
        for c in self.contained_components:
            self._model.models[c].pres_ext += self.pres
