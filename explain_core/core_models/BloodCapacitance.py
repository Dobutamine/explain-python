from explain_core.base_models.Capacitance import Capacitance


class BloodCapacitance(Capacitance):

    # state variables
    systole: float = 0.0
    diastole: float = 0.0
    mean: float = 0.0
    vol_max: float = 0.0
    vol_min: float = 0.0
    stroke_volume: float = 0.0
    solutes: dict[str, float] = {}
    acidbase: dict[str, float] = {}
    oxy: dict[str, float] = {}

    # local variables
    _temp_max_pres: float = -1000.0
    _temp_min_pres: float = 1000.0
    _temp_max_vol: float = -1000.0
    _temp_min_vol: float = 1000.0

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # do the cap actions
        super().calc_model()

        # determine systole and diastole
        if self.pres > self._temp_max_pres:
            self._temp_max_pres = self.pres
        if self.pres < self._temp_min_pres:
            self._temp_min_pres = self.pres

        if self.vol > self._temp_max_vol:
            self._temp_max_vol = self.vol
        if self.vol < self._temp_min_vol:
            self._temp_min_vol = self.vol

        # store diastole and systole
        if self._model.models['Heart'].ncc_ventricular == 0:
            self.systole = self._temp_max_pres
            self.diastole = self._temp_min_pres
            self.mean = self.diastole + 1/3 * (self.systole - self.diastole)
            self._temp_min_pres = 1000.0
            self._temp_max_pres = -1000.0

            self.vol_max = self._temp_max_vol
            self.vol_min = self._temp_min_vol
            self.stroke_volume = self.vol_max - self.vol_min
            self._temp_max_vol = -1000
            self._temp_min_vol = 1000

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        super().volume_in(dvol)

        # process the to2 and tco2
        d_to2: float = (model_from.aboxy['to2'] - self.aboxy['to2']) * dvol
        self.aboxy['to2'] = (self.aboxy['to2'] * self.vol + d_to2) / self.vol

        d_tco2: float = (
            model_from.aboxy['tco2'] - self.aboxy['tco2']) * dvol
        self.aboxy['tco2'] = (
            self.aboxy['tco2'] * self.vol + d_tco2) / self.vol

        # process the solutes
        if self.vol > 0:
            for solute, conc in self.solutes.items():
                d_solute: float = (
                    model_from.solutes[solute] - conc) * dvol
                self.solutes[solute] = (
                    (conc * self.vol) + d_solute) / self.vol
