from explain_core.base_models.Capacitance import Capacitance


class BloodCapacitance(Capacitance):

    # state variables
    systole: float = 0.0
    diastole: float = 0.0
    mean: float = 0.0

    # local variables
    _temp_max_pres: float = -1000.0
    _temp_min_pres: float = 1000.0

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # do the cap actions
        super().calc_model()

        # determine systole and diastole
        if self.pres > self._temp_max_pres:
            self._temp_max_pres = self.pres
        if self.pres < self._temp_min_pres:
            self._temp_min_pres = self.pres

        # store diastole and systole
        if self._model.models['Heart'].ncc_ventricular == 0:
            self.systole = self._temp_max_pres
            self.diastole = self._temp_min_pres
            self.mean = self.diastole + 1/3 * (self.systole - self.diastole)
            self._temp_min_pres = 1000.0
            self._temp_max_pres = -1000.0

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        super().volume_in(dvol)
