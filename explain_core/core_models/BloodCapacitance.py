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

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # do the cap actions
        super().calc_model()

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        super().volume_in(dvol)

        if self.vol <= 0:
            return

        # process the to2 and tco2
        for solute in ['to2', 'tco2']:
            d_solute = (model_from.aboxy[solute] - self.aboxy[solute]) * dvol
            self.aboxy[solute] += d_solute / self.vol

        for solute, conc in self.solutes.items():
            conc_from = model_from.solutes[solute]
            d_solute = (conc_from - conc) * dvol
            self.solutes[solute] += d_solute / self.vol
