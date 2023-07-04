from explain_core.base_models.Capacitance import Capacitance


class Container(Capacitance):
    # independent variables
    vol_extra: float = 0.0

    # local variables
    _cps: list[Capacitance] = []

    def init_model(self, model: object) -> bool:
        # init the parent class
        super().init_model(model)

        # get a reference to all the model components this container contains
        for comp in self.contained_components:
            self._cps.append(self._model.models[comp])

        return self._is_initialized

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # get the current volume from all contained model components
        for c in self._cps:
            self.vol += c.vol

        # add the extra volume
        self.vol += self.vol_extra

        # do the capacitans actions -> calculate pressure
        super().calc_model()
