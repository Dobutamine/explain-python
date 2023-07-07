from explain_core.base_models.Capacitance import Capacitance


class Container(Capacitance):
    # independent variables
    vol_extra: float = 0.0

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # get the current volume from all contained model components
        self.vol = self.vol_extra

        for c in self.contained_components:
            self.vol += self._model.models[c].vol

        # do the capacitans actions -> calculate pressure
        super().calc_model()

        # transfer the pressures to the models the container contains
        for c in self.contained_components:
            self._model.models[c].pres_ext = self.pres
