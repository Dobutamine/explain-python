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
    heart_model: str = "Heart"
    aa_model: str = "AA"
    aa_cor_model: str = "AA_COR"
    cor_model: str = "COR"
    lv_model: str = "LV"
    rv_model: str = "RV"

    # dependent variables
    to2_co2: float = 0.0
    to2_in: float = 0.0
    ecc_lv: float = 0.0                         # pres_ms of the heart chamber 
    ecc_rv: float = 0.0
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

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # inflow of oxygen
        to2_in: float = self._aa.aboxy["to2"] * self._aa_cor.flow   # mmol o2 per second
        to2_cor: float = self._cor.aboxy["to2"]                     # mmol o2 / l 
        
        # get the ecc from the heart chambers
        self.ecc_lv = self._lv.pres_ms
        self.ecc_rv = self._rv.pres_ms

        # calculate the pressure volume loop area
        self.pva = self.calc_pva()

        # calculate the blood composition of the coronary blood capacity every heart cycle
        if self._heart.ncc_ventricular == 1:
            set_blood_composition(self._cor)

        # calculate the oxygen metabolism
        self.oxygen_metabolism()

    def oxygen_metabolism(self) -> None:
        po2_cor = self._cor.aboxy["po2"]

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








