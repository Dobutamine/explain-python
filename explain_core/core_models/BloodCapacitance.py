from explain_core.base_models.Capacitance import Capacitance


class BloodCapacitance(Capacitance):
    # independent variables
    solutes: dict[str, float] = {}
    aboxy: dict[str, float] = {}
    drugs: dict[str, float] = {}

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        # if blood capacitance has a fixed composition then return
        if self.fixed_composition:
            return

        # execute the parent class method of the capacitance model
        super().volume_in(dvol)

        # return if the volume is zero
        if self.vol <= 0:
            return

        # process the to2 and tco2, hemoglobin and albumin
        vol: float = self.vol + self.u_vol
        for solute in ["to2", "tco2", "hemoglobin", "albumin"]:
            d_solute = (model_from.aboxy[solute] - self.aboxy[solute]) * dvol
            self.aboxy[solute] += d_solute / vol

        # process the solutes
        for solute, conc in self.solutes.items():
            conc_from = model_from.solutes[solute]
            d_solute = (conc_from - conc) * dvol
            self.solutes[solute] += d_solute / vol

        # process the drugs
        for drug, conc in self.drugs.items():
            conc_from = model_from.drugs[drug]
            d_drug = (conc_from - conc) * dvol
            self.drugs[drug] += d_drug / vol
