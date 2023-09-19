import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasResistor import GasResistor

class VentilatorExp(BaseModel):
    #independent parameters
    freq: float = 40
    inspTime: float = 0.4
    pip: float = 3.7
    peep: float = 0.0
    expTidalVolume: float = 0.0
    inspTidalVolume: float = 0.0

    _mouth: GasCapacitance = {}
    _mouth_ds: GasResistor = {}
    _expTime: float = 0.8
    _inspCounter: float = 0.0
    _expCounter: float = 0.0
    _inspiration: bool = True
    _expiration: bool = False
    _expTidalVolumeCounter: float = 0.0
    _inspTidalVolumeCounter: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the mouth comparment
        self._mouth = self._model.models['MOUTH']
        self._mouth_ds = self._model.models['MOUTH_DS']

    def calc_model(self):
        # switch off the spontaneous breathing
        self._mouth_ds.r_for_factor = 2.0
        self._mouth_ds.r_back_factor = 1.0

        # calculate the expiration time
        self._expTime = (60.0 / self.freq) - self.inspTime

        # has the inspiration time elasped?
        if self._inspCounter > self.inspTime:
            self._inspCounter = 0.0
            self._inspiration = False
            self._expiration = True
            self.inspTidalVolume = self._inspTidalVolumeCounter
            self._inspTidalVolumeCounter = 0.0

        # has the expiration time elapsed?
        if self._expCounter > self._expTime:
            self._expCounter = 0.0
            self._inspiration = True
            self._expiration = False
            self.expTidalVolume = -self._expTidalVolumeCounter
            self._expTidalVolumeCounter = 0.0

        # if inspiration is running
        if self._inspiration:
            self._mouth.pres_ext = self.pip
            self._inspCounter += self._t
            self._inspTidalVolumeCounter += self._mouth_ds.flow * self._t
            

        if self._expiration:
            self._mouth.pres_ext = self.peep
            self._expCounter += self._t
            self._expTidalVolumeCounter += self._mouth_ds.flow * self._t

        

        

