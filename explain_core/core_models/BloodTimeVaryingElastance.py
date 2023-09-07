from explain_core.core_models.TimeVaryingElastance import TimeVaryingElastance
from explain_core.base_models.Capacitance import Capacitance


class BloodTimeVaryingElastance(TimeVaryingElastance):

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
        self._temp_max_pres = max(self.pres, self._temp_max_pres)
        self._temp_min_pres = min(self.pres, self._temp_min_pres)

        self._temp_max_vol = max(self.vol, self._temp_max_vol)
        self._temp_min_vol = min(self.vol, self._temp_min_vol)

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

        if self.vol <= 0:
            return

        # process the to2 and tco2
        for solute in ['to2', 'tco2']:
            d_solute = (model_from.aboxy[solute] - self.aboxy[solute]) * dvol
            self.aboxy[solute] += d_solute / self.vol

        # process the solutes
        for solute, conc in self.solutes.items():
            conc_from = model_from.solutes[solute]
            d_solute = (conc_from - conc) * dvol
            self.solutes[solute] += d_solute / self.vol
