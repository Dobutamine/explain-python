import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.Heart import Heart
from explain_core.core_models.BloodTimeVaryingElastance import BloodTimeVaryingElastance
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.base_models.Resistor import Resistor
from explain_core.functions.BloodComposition import set_blood_composition
from explain_core.functions.ActivationFunction import activation_function

class Mob(BaseModel):
    # independent variables 
    hw: float = 0.0                     # heart weight = 7.799 + 0.004296 * birth weight (grams)
    bm_vo2_ref: float = 0.000159        # in ml O2/cardiac cycle/gram heart_weight: vo2 when the heart is not beating and depending on do2
    bm_vo2_min: float = 0.0000318       # minimal vo2 in ml O2/cardiac cycle/gram heart_weight when do2 dropping below threshold
    ecc_c: float = 0.0                  # not implemented yet but included in basal metabolism
    pva_c: float = 0.00425              # CPVA in mL O2/cardiac cycle/mmHg*l
    resp_q: float = 0.5                 # respiratory quotient

    po2_set: float = 10.0       
    po2_max: float = 10.0
    po2_min: float = 0.0
    
    bm_po2_tc: float = 5.0
    bm_po2_g: float = 2.0               # maximal reduction of 20%   -10 * 2.0 = 20
    
    cont_po2_tc: float = 5.0
    cont_po2_g: float = 0.0

    hr_po2_tc: float = 5.0
    hr_po2_g: float = 0.0

    heart_model: str = "Heart"
    aa_model: str = "AA"
    aa_cor_model: str = "AA_COR"
    cor_model: str = "COR"
    lv_model: str = "LV"
    rv_model: str = "RV"

    # dependent variables
    mob: float = 0.0
    mvo2: float = 0.0
    mvo2_step: float = 0.0
    bm_vo2: float = 0.0
    ecc_vo2: float = 0.0
    pva_vo2: float = 0.0

    to2_co2: float = 0.0
    to2_in: float = 0.0
    ecc_lv: float = 0.0                         # pres_ms of the heart chamber 
    ecc_rv: float = 0.0
    ecc: float = 0.0
    pva: float = 0.0                            # total pva of both ventricles
    stroke_work_lv: float = 0.0                 # stroke work of left ventricle
    stroke_work_rv: float = 0.0                 # stroke work of right ventricle
    stroke_volume_lv: float = 0.0               # stroke volume in liters
    stroke_volume_rv: float = 0.0               # stroke volume in liters

    # local state variables
    _heart: Heart = {}
    _aa: BloodCapacitance = {}
    _aa_cor: Resistor = {}
    _cor: BloodTimeVaryingElastance = {}
    _lv: BloodTimeVaryingElastance = {}
    _rv: BloodTimeVaryingElastance = {}

    _prev_lv_vol: float = 0.0
    _prev_lv_pres: float = 0.0
    _prev_rv_vol: float = 0.0
    _prev_rv_pres: float = 0.0

    _pv_area_lv: float = 0.0
    _pv_area_rv: float = 0.0
    _sv_lv_cum: float = 0.0
    _sv_rv_cum: float = 0.0

    _a_po2: float = 0.0
    _d_bm_vo2: float = 0.0
    _d_cont: float = 0.0
    _d_hr: float = 0.0
    _ml_to_mmol: float = 22.414

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        self._heart = self._model.models[self.heart_model]
        self._aa = self._model.models[self.aa_model]
        self._aa_cor = self._model.models[self.aa_cor_model]
        self._cor = self._model.models[self.cor_model]
        self._lv = self._model.models[self.lv_model]
        self._rv = self._model.models[self.rv_model]

        # set the heart weight
        self.hw = 7.799 + 0.004296 * self._model.weight * 1000.0

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # inflow of oxygen
        to2_in: float = self._aa.aboxy["to2"] * self._aa_cor.flow   # mmol o2 per second
        to2_cor: float = self._cor.aboxy["to2"]                     # mmol o2 / l 
        
        # get the ecc from the heart chambers
        self.ecc_lv = self._lv.el_max * self._lv.el_max_factor
        self.ecc_rv = self._rv.el_max * self._rv.el_max_factor
        self.ecc = self.ecc_lv + self.ecc_rv

        # calculate the pressure volume loop area
        self.pva = self.calc_pva()

        # calculate the blood composition of the coronary blood capacity every heart cycle
        if self._heart.ncc_ventricular == 1:
            set_blood_composition(self._cor)

        # calculate the oxygen metabolism in mmol O2 / cardiac cycle
        self.mvo2 = self.oxygen_metabolism()

        # this total vo2 is in 1 cardiac cycle, we now have to calculate the vo2 in this model step
        hc_duration = 60.0 / self._heart.heart_rate
        self.mvo2_step = (self.mvo2 / hc_duration) * self._t
        co2_production = self.mvo2_step * self.resp_q

        # get the necessary model properties from the coronaries
        to2_cor = self._cor.aboxy["to2"]
        tco2_cor = self._cor.aboxy["tco2"]
        vol_cor = self._cor.vol

        # calculate the myocardial oxygen balance in mmol / cardiac cycle
        o2_inflow = (self._aa_cor.flow * self._aa.aboxy["to2"]) # in mmol/s
        o2_use = self.mvo2 / hc_duration                        # in mmol/s
        self.mob = (o2_inflow - o2_use) + to2_cor

        if vol_cor > 0:
            new_to2_cor =  ((to2_cor * vol_cor) - self.mvo2_step) / vol_cor
            new_tco2_cor = ((tco2_cor * vol_cor) + co2_production) / vol_cor
            if new_to2_cor >= 0:
                self._cor.aboxy["to2"] = new_to2_cor
                self._cor.aboxy["tco2"] = new_tco2_cor

        # calculate the effect on the heartrate, contractility and coronary bloodflow
        # acute hypoxia leads to an increase in heartrate, contractility and coronary blood flow -> this is modeled by the ANS model

        # and we have direct hypoxic effects making the heart less susceptible for ANS influence
        # when hypoxia gets severe the ANS influence gets inhibited and the heartrate, contractility and baseline metabolism are decreased

        # so we need a to2 dependent parameter (maybe through a activation function) which dampens the ANS influence on
        # the heartrate and contractility and decreases it further when hypoxemia gets worse

    def oxygen_metabolism(self) -> float:
        # get the po2 in mmHg from coronaries
        po2_cor = self._cor.aboxy["po2"]

        # calculate the activation function of the baseline vo2
        self._a_po2 = activation_function(po2_cor, self.po2_max, self.po2_set, self.po2_min)

        # calculate the gain depending on the reference and minimal baseline vo2 and po2 threshold from where the baseline vo2 is reduced
        # this gain determines how much the baseline vo2 is reduced when the po2 drops below the threshold
        self.bm_po2_g = (self.bm_vo2_ref - self.bm_vo2_min) / (self.po2_set - self.po2_min)

        # incorporate the time constants
        self._d_bm_vo2 = self._t * ((1 / self.bm_po2_tc) * (-self._d_bm_vo2 + self._a_po2)) + self._d_bm_vo2
        self._d_hr = self._t * ((1 / self.hr_po2_tc) * (-self._d_hr + self._a_po2)) + self._d_hr
        self._d_cont = self._t * ((1 / self.cont_po2_tc) * (-self._d_cont + self._a_po2)) + self._d_cont

        # calculate the baseline vo2 in mmol O2 /  cardiac cycle
        self.bm_vo2 = ((self.bm_vo2_ref + self._d_bm_vo2 * self.bm_po2_g) * self.hw) / self._ml_to_mmol

        # calculate the influence on the contractility and heartrate which overrule the ANS influence



        # calculate the ecc vo2 -> not implemented yet but included in baseline metabolism
        self.ecc_vo2 = self.ecc * self.ecc_c

        # calculate the pva vo2 in mmol O2 / cardiac cycle
        self.pva_vo2 = (self.pva * self.pva_c) / self._ml_to_mmol

        # return the total vo2 
        return self.bm_vo2 + self.ecc_vo2 + self.pva_vo2

    def calc_pe(self) -> float:
        pass

    def calc_pva(self) -> float:
        # detect the start of the cardiac cycle and calculate the area of the pv loop of the last cardiac cycle
        if self._heart.ncc_ventricular == 1:
            # calculate the stroke work of the ventricles
            self.stroke_work_lv = -self._pv_area_lv     # in l * mmHg/cardiac cycle
            self.stroke_work_rv = -self._pv_area_rv     # in l * mmHg/cardiac cycle

            # calculate the stroke volume of the ventricles
            self.stroke_volume_lv = self._sv_lv_cum  # in l/cardiac cycle
            self.stroke_volume_rv = self._sv_rv_cum  # in l/cardiac cycle
            
            # reset the counters
            self._pv_area_lv = 0.0
            self._pv_area_rv = 0.0
            self._sv_lv_cum = 0.0
            self._sv_rv_cum = 0.0

        # calculate the pv area of this model step
        _dV_lv = self._lv.vol - self._prev_lv_vol
        self._pv_area_lv += (_dV_lv * self._prev_lv_pres) + (_dV_lv * (self._lv.pres - self._prev_lv_pres)) / 2.0
        if _dV_lv > 0:
            self._sv_lv_cum += _dV_lv

        _dV_rv = self._rv.vol - self._prev_rv_vol
        self._pv_area_rv += (_dV_rv * self._prev_rv_pres) + (_dV_rv * (self._rv.pres - self._prev_rv_pres)) / 2.0
        if _dV_rv > 0:
            self._sv_rv_cum += _dV_rv

        # store current volumes and pressures
        self._prev_lv_vol = self._lv.vol
        self._prev_lv_pres = self._lv.pres
        
        self._prev_rv_vol = self._rv.vol
        self._prev_rv_pres = self._rv.pres

        # return the total pressure volume area of both ventricles
        return self.stroke_work_lv + self.stroke_work_rv








