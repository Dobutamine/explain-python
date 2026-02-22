from component_models.capacitance import Capacitance


class BloodCapacitance(Capacitance):
    model_type = "blood_capacitance"

    def __init__(self, model_ref={}, name=None):
        super().__init__(model_ref=model_ref, name=name)

        self.temp = 37.0
        self.viscosity = 6.0
        self.solutes = {}
        self.drugs = {}

        self.to2 = 0.0
        self.tco2 = 0.0
        self.ph = -1.0
        self.pco2 = -1.0
        self.po2 = -1.0
        self.so2 = -1.0
        self.hco3 = -1.0
        self.be = -1.0
        self.prev_ph = 7.37
        self.prev_po2 = 18.7

    def volume_in(self, dvol, comp_from=None):
        super().volume_in(dvol)

        if comp_from is None or self.vol <= 0.0:
            return

        self.to2 += ((getattr(comp_from, "to2", 0.0) - self.to2) * dvol) / self.vol
        self.tco2 += ((getattr(comp_from, "tco2", 0.0) - self.tco2) * dvol) / self.vol

        comp_from_solutes = getattr(comp_from, "solutes", {}) or {}
        for solute_name in self.solutes:
            solute_from = comp_from_solutes.get(solute_name, 0.0)
            self.solutes[solute_name] += ((solute_from - self.solutes[solute_name]) * dvol) / self.vol

        comp_from_drugs = getattr(comp_from, "drugs", {}) or {}
        for drug_name in self.drugs:
            drug_from = comp_from_drugs.get(drug_name, 0.0)
            self.drugs[drug_name] += ((drug_from - self.drugs[drug_name]) * dvol) / self.vol

        self.temp += ((getattr(comp_from, "temp", self.temp) - self.temp) * dvol) / self.vol
        self.viscosity += ((getattr(comp_from, "viscosity", self.viscosity) - self.viscosity) * dvol) / self.vol
