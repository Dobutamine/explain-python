import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.Heart import Heart
from explain_core.core_models.BloodTimeVaryingElastance import BloodTimeVaryingElastance
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.base_models.Resistor import Resistor
from explain_core.functions.BloodComposition import set_blood_composition

class Mob(BaseModel):
    # independent variables
    baseline_metabolism: float = 0.0            # vo2 when the heart is not beating and depending on do2


    heart_model: float = "Heart"
    lv_model: float = "LV"
    rv_model: float = "RV"

    # dependent variables
    to2_co2: float = 0.0
    to2_in: float = 0.0
    ecc_lv: float = 0.0                         # pres_ms of the heart chamber 
    ecc_rv: float = 0.0
    pva_lv: float = 0.0
    pva_rv: float = 0.0
    stroke_work_lv: float = 0.0      # stroke work of left ventricle
    stroke_work_rv: float = 0.0      # stroke work of right ventricle

    stroke_volume_lv: float = 0.0      # stroke volume in liters
    stroke_volume_rv: float = 0.0      # stroke volume in liters

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

    _area_lv: float = 0.0
    _area_rv: float = 0.0
    _sv_lv_cum: float = 0.0
    _sv_rv_cum: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        self._heart = self._model.models[self.heart_model]
        self._cor = self._model.models[self.cor_model]
        self._lv = self._model.models[self.lv_model]
        self._rv = self._model.models[self.rv_model]

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self):
        # inflow of oxygen
        to2_in: float = self._aa.aboxy["to2"] * self._aa_cor.flow   # mmol o2 per second
        to2_cor: float = self._cor.aboxy["to2"]                     # mmol o2 / l 
        
        # get the ecc from the chambers
        self.ecc_lv = self._lv.pres_ms
        self.ecc_rv = self._rv.pres_ms

        # detect the start of the cardiac cycle and calculate the area of the pv loop of the last cardiac cycle
        if self._heart.ncc_ventricular == 1:
            # calculate the acidbase and oxygenation of the coronaries
            set_blood_composition(self._cor)
            # calculate the stroke work of the ventricles
            self.stroke_work_lv = -self._area_lv     # in l * mmHg/cardiac cycle
            self.stroke_work_rv = -self._area_rv     # in l * mmHg/cardiac cycle
            # calculate the stroke volume of the ventricles
            self.stroke_volume_lv = self._sv_lv_cum  # in l/cardiac cycle
            self.stroke_volume_rv = self._sv_rv_cum  # in l/cardiac cycle
            # reset the counters
            self._area_lv = 0.0
            self._area_rv = 0.0
            self._sv_lv_cum = 0.0
            self._sv_rv_cum = 0.0

        # calculate the pv area of this model step
        _dV_lv = self._lv.vol - self._prev_lv_vol
        self._area_lv += (_dV_lv * self._prev_lv_pres) + (_dV_lv * (self._lv.pres - self._prev_lv_pres)) / 2.0
        if _dV_lv > 0:
            self._sv_lv_cum += _dV_lv

        _dV_rv = self._rv.vol - self._prev_rv_vol
        self._area_rv += (_dV_rv * self._prev_rv_pres) + (_dV_rv * (self._rv.pres - self._prev_rv_pres)) / 2.0
        if _dV_rv > 0:
            self._sv_rv_cum += _dV_rv

        # store current volumes and pressures
        self._prev_lv_vol = self._lv.vol
        self._prev_lv_pres = self._lv.pres
        
        self._prev_rv_vol = self._rv.vol
        self._prev_rv_pres = self._rv.pres







