from explain_core.base_models.TimeVaryingElastance import TimeVaryingElastance
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

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        # if blood capacitance has a fixed composition then return
        if self.fixed_composition:
            return
        
        # execute the parent class method
        super().volume_in(dvol)

        if self.vol <= 0:
            return

        # process the to2 and tco2
        vol:float = self.vol + self.u_vol
        for solute in ['to2', 'tco2', 'hemoglobin', 'albumin']:
            d_solute = (model_from.aboxy[solute] - self.aboxy[solute]) * dvol
            self.aboxy[solute] += d_solute / vol

        # process the solutes
        for solute, conc in self.solutes.items():
            conc_from = model_from.solutes[solute]
            d_solute = (conc_from - conc) * dvol
            self.solutes[solute] += d_solute / vol
