from explain_core.base_models.Capacitance import Capacitance


class LymphCapacitance(Capacitance):
    # independent variables
    t_start: float = 0.0
    pacemaker: bool = False
    
    # state variables
    systole: float = 0.0
    diastole: float = 0.0
    mean: float = 0.0
    vol_max: float = 0.0
    vol_min: float = 0.0
    stroke_volume: float = 0.0
    solutes: dict[str, float] = {}
    acidbase: dict[str, float] = {}
    drugs: dict[str, float] = {}
    oxy: dict[str, float] = {}

    activator: Capacitance = {}
    contraction_timer: float = 0.0
    interval_timer: float = 0.0
    contraction_running: bool = False
    interval_running: bool = False

    contraction_interval: float = 12.0
     

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        # if blood capacitance has a fixed composition then return
        if self.fixed_composition:
            return

        # execute the parent class method
        super().volume_in(dvol)

        # return if the volume is zero
        if self.vol <= 0:
            return
            
        # process the solutes
        vol: float = self.vol + self.u_vol
        for solute, conc in self.solutes.items():
            conc_from = model_from.solutes[solute]
            d_solute = (conc_from - conc) * dvol
            self.solutes[solute] += d_solute / vol

        # process the drugs
        for drug, conc in self.drugs.items():
            conc_from = model_from.drugs[drug]
            d_drug = (conc_from - conc) * dvol
            self.drugs[drug] += d_drug / vol

        # if model_from.model_type != "LymphCapacitance":
        #     d_aboxy = (model_from.aboxy["albumin"] - self.aboxy["albumin"]) * dvol
        #     self.aboxy["albumin"] += d_aboxy / vol

#        # process the proteins
#        if model_from == LymphCapacitance:
#            for solute in ["albumin"]:
#                d_solute = (model_from.aboxy[solute] - self.aboxy[solute]) * dvol
#                self.aboxy[solute] += d_solute / vol
#        elif model_from != LymphCapacitance:
#            for solute in ["albumin"]:
#                d_solute = (conc_new - self.aboxy[solute]) * dvol
#                self.aboxy[solute] += d_solute / vol            


#        if model_from == LymphCapacitance:
#            # process the to2 and tco2, hemoglobin and albumin
#            for solute in ["albumin"]:
#                d_solute = (model_from.aboxy[solute] - self.aboxy[solute]) * dvol
#                self.aboxy[solute] += d_solute / vol
#        elif model_from != LymphCapacitance:
#            for solute in ["albumin"]:
#                d_solute = 0
#                self.aboxy[solute] += d_solute / vol
#                self.aboxy[solute] = self.aboxy[solute]*vol /(vol+dvol) 



          



