from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from custom_models.LymphCapacitance import LymphCapacitance
from explain_core.functions.BloodComposition import set_blood_composition

class LymphDiffusor(BaseModel):
    # independent variables
    dif_o2: float = 0.01
    dif_o2_factor: float = 1.0
    dif_co2: float = 0.01
    dif_co2_factor: float = 1.0

    dif_na: float = 0.01
    dif_na_factor: float = 1.0
    dif_k: float = 0.01
    dif_k_factor: float = 1.0
    dif_ca: float = 0.01
    dif_ca_factor: float = 1.0
    dif_mg: float = 0.01
    dif_mg_factor: float = 1.0    
    dif_cl: float = 0.01
    dif_cl_factor: float = 1.0
    dif_lact: float = 0.01
    dif_lact_factor: float = 1.0 

    dif_albumin: float = 0.000001
    dif_albumin_factor: float = 1.0       


    # local variables
    _comp1: BloodCapacitance or LymphCapacitance = {}
    _comp2: BloodCapacitance or LymphCapacitance = {}
    _flux_o2: float = 0
    _flux_co2: float = 0
    _flux_na: float = 0
    _flux_k: float = 0
    _flux_ca: float = 0
    _flux_mg: float = 0
    _flux_cl: float = 0
    _flux_lact: float = 0
    _flux_albumin: float = 0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # get a reference to the blood capacitances
        if type(self.comp1) is str:
            self._comp1 = self._model.models[self.comp1]
        else:
            self._comp1 = self.comp1

        if type(self.comp2) is str:
            self._comp2 = self._model.models[self.comp2]
        else:
            self._comp2 = self.comp2

    def calc_model(self) -> None:
        super().calc_model()

        # we need to po2 and pco2 so we need to calculate the blood composition
        #set_blood_composition(self._comp1)
        #set_blood_composition(self._comp2)

        # get the partial pressures and gas concentrations from the components
        to2_comp1: float = self._comp1.aboxy['to2']
        tco2_comp1: float = self._comp1.aboxy['tco2']
        albumin_comp1: float = self._comp1.aboxy['albumin']
        na_comp1: float = self._comp1.solutes['na']
        k_comp1: float = self._comp1.solutes['k']
        ca_comp1: float = self._comp1.solutes['ca']
        mg_comp1: float = self._comp1.solutes['mg']
        cl_comp1: float = self._comp1.solutes['cl']
        lact_comp1: float = self._comp1.solutes['lact']

        to2_comp2: float = self._comp2.aboxy['to2']
        tco2_comp2: float = self._comp2.aboxy['tco2']
        albumin_comp2: float = self._comp2.aboxy['albumin']
        na_comp2: float = self._comp2.solutes['na']
        k_comp2: float = self._comp2.solutes['k']
        ca_comp2: float = self._comp2.solutes['ca']
        mg_comp2: float = self._comp2.solutes['mg']
        cl_comp2: float = self._comp2.solutes['cl']
        lact_comp2: float = self._comp2.solutes['lact']

        # calculate the O2 and CO2 flux
        self._flux_o2 = (to2_comp1 - to2_comp2) * self.dif_o2 * self.dif_o2_factor * self._t
        self._flux_co2 = (tco2_comp1 - tco2_comp2) * self.dif_co2 * self.dif_co2_factor * self._t
        self._flux_albumin = (albumin_comp1 - albumin_comp2) * self.dif_albumin * self.dif_albumin_factor * self._t
        self._flux_na = (na_comp1 - na_comp2) * self.dif_na * self.dif_na_factor * self._t
        self._flux_k = (k_comp1 - k_comp2) * self.dif_k * self.dif_k_factor * self._t
        self._flux_ca = (ca_comp1 - ca_comp2) * self.dif_ca * self.dif_ca_factor * self._t
        self._flux_mg = (mg_comp1 - mg_comp2) * self.dif_mg * self.dif_mg_factor * self._t
        self._flux_cl = (cl_comp1 - cl_comp2) * self.dif_cl * self.dif_cl_factor * self._t
        self._flux_lact = (lact_comp1 - lact_comp2) * self.dif_lact * self.dif_lact_factor * self._t


        # calculate the new O2 and CO2 concentrations
        _comp1_vol:float = self._comp1.vol + self._comp1.u_vol
        _comp2_vol:float = self._comp2.vol + self._comp2.u_vol

        new_to2_comp1: float = (to2_comp1 * _comp1_vol - self._flux_o2) / _comp1_vol
        if new_to2_comp1 < 0:
            new_to2_comp1 = 0

        new_to2_comp2: float = (to2_comp2 * _comp2_vol + self._flux_o2) / _comp2_vol
        if new_to2_comp2 < 0:
            new_to2_comp2 = 0

        new_tco2_comp1: float = (tco2_comp1 * _comp1_vol - self._flux_co2) / _comp1_vol
        if new_tco2_comp1 < 0:
            new_tco2_comp1 = 0

        new_tco2_comp2: float = (tco2_comp2 * _comp2_vol + self._flux_co2) / _comp2_vol
        if new_tco2_comp2 < 0:
            new_tco2_comp2 = 0

        new_albumin_comp1: float = (albumin_comp1 * _comp1_vol - self._flux_albumin) / _comp1_vol
        if new_albumin_comp1 < 0:
            new_albumin_comp1 = 0

        new_albumin_comp2: float = (albumin_comp2 * _comp2_vol + self._flux_albumin) / _comp2_vol
        if new_albumin_comp2 < 0:
            new_albumin_comp2 = 0

        new_na_comp1: float = (na_comp1 * _comp1_vol - self._flux_na) / _comp1_vol
        if new_na_comp1 < 0:
            new_na_comp1 = 0

        new_na_comp2: float = (na_comp2 * _comp2_vol + self._flux_na) / _comp2_vol
        if new_na_comp2 < 0:
            new_na_comp2 = 0

        new_k_comp1: float = (k_comp1 * _comp1_vol - self._flux_k) / _comp1_vol
        if new_k_comp1 < 0:
            new_k_comp1 = 0

        new_k_comp2: float = (k_comp2 * _comp2_vol + self._flux_k) / _comp2_vol
        if new_k_comp2 < 0:
            new_k_comp2 = 0

        new_ca_comp1: float = (ca_comp1 * _comp1_vol - self._flux_ca) / _comp1_vol
        if new_ca_comp1 < 0:
            new_ca_comp1 = 0

        new_ca_comp2: float = (ca_comp2 * _comp2_vol + self._flux_ca) / _comp2_vol
        if new_ca_comp2 < 0:
            new_ca_comp2 = 0

        new_mg_comp1: float = (mg_comp1 * _comp1_vol - self._flux_mg) / _comp1_vol
        if new_mg_comp1 < 0:
            new_mg_comp1 = 0

        new_mg_comp2: float = (mg_comp2 * _comp2_vol + self._flux_mg) / _comp2_vol
        if new_mg_comp2 < 0:
            new_mg_comp2 = 0

        new_cl_comp1: float = (cl_comp1 * _comp1_vol - self._flux_cl) / _comp1_vol
        if new_cl_comp1 < 0:
            new_cl_comp1 = 0

        new_cl_comp2: float = (cl_comp2 * _comp2_vol + self._flux_cl) / _comp2_vol
        if new_cl_comp2 < 0:
            new_cl_comp2 = 0

        new_lact_comp1: float = (lact_comp1 * _comp1_vol - self._flux_lact) / _comp1_vol
        if new_lact_comp1 < 0:
            new_lact_comp1 = 0

        new_lact_comp2: float = (lact_comp2 * _comp2_vol + self._flux_lact) / _comp2_vol
        if new_lact_comp2 < 0:
            new_lact_comp2 = 0

        # set the new concentrations
        self._comp1.aboxy['to2'] = new_to2_comp1
        self._comp1.aboxy['tco2'] = new_tco2_comp1
        self._comp1.aboxy['albumin'] = new_albumin_comp1
        self._comp1.aboxy['na'] = new_na_comp1
        self._comp1.aboxy['k'] = new_k_comp1
        self._comp1.aboxy['ca'] = new_ca_comp1
        self._comp1.aboxy['mg'] = new_mg_comp1
        self._comp1.aboxy['cl'] = new_cl_comp1
        self._comp1.aboxy['lact'] = new_lact_comp1

        self._comp2.aboxy['to2'] = new_to2_comp2
        self._comp2.aboxy['tco2'] = new_tco2_comp2
        self._comp2.aboxy['albumin'] = new_albumin_comp2
        self._comp2.aboxy['na'] = new_na_comp2
        self._comp2.aboxy['k'] = new_k_comp2
        self._comp2.aboxy['ca'] = new_ca_comp2
        self._comp2.aboxy['mg'] = new_mg_comp2
        self._comp2.aboxy['cl'] = new_cl_comp2
        self._comp2.aboxy['lact'] = new_lact_comp2