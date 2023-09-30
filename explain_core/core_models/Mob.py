import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.Heart import Heart
from explain_core.core_models.BloodTimeVaryingElastance import BloodTimeVaryingElastance

class Mob(BaseModel):
    
    # dependent variables
    pv_lv: float = 0.0
    pv_rv: float = 0.0

    # local state variables
    _heart: Heart = {}
    _lv: BloodTimeVaryingElastance = {}
    _rv: BloodTimeVaryingElastance = {}

    _prev_lv_vol: float = 0.0
    _prev_lv_pres: float = 0.0
    _prev_rv_vol: float = 0.0
    _prev_rv_pres: float = 0.0

    _area_lv: float = 0.0
    _area_rv: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        self._heart = self._model.models["Heart"]
        self._lv = self._model.models["LV"]
        self._rv = self._model.models["RV"]

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self):
        # detect the start of the cardiac cycle and calculate the area of the pv loop of the last cardiac cycle
        if self._heart.ncc_ventricular == 1:
            self.pv_lv = -self._area_lv     # in l * mmHg/cardiac cycle
            self._area_lv = 0.0
            self.pv_rv = -self._area_rv     # in l * mmHg/cardiac cycle
            self._area_rv = 0.0

        # store the pv area of this model step
        _dV_lv = self._lv.vol - self._prev_lv_vol
        self._area_lv += (_dV_lv * self._prev_lv_pres) + (_dV_lv * (self._lv.pres - self._prev_lv_pres)) / 2.0

        _dV_rv = self._rv.vol - self._prev_rv_vol
        self._area_rv += (_dV_rv * self._prev_rv_pres) + (_dV_rv * (self._rv.pres - self._prev_rv_pres)) / 2.0

        # store current volumes and pressures
        self._prev_lv_vol = self._lv.vol
        self._prev_lv_pres = self._lv.pres
        
        self._prev_rv_vol = self._rv.vol
        self._prev_rv_pres = self._rv.pres







