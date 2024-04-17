import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance

class ExampleCustomModel(BaseModel):
    # independent variables
    R_valve: float = 1.0
    R_valve_min: float = 1.0
    R_valve_max: float  = 1.0
    s_open: float = 1.0
    p_open: float = 1.0
    s_fail: float = 1.0
    p_fail: float = 1.0

    # define object which hold references to a BloodCapacitance or TimeVaryingElastance
    _model_comp_from: Capacitance = {}
    _model_comp_to: Capacitance = {}    

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        if type(self.comp_from) is str:
            self._model_comp_from = self._model.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) is str:
            self._model_comp_to = self._model.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        self.dP = self._model_comp_from.pres - self._model_comp_to.pres
        self.R_valve = self.R_valve_min + self.R_valve_max*(1/(1+math.exp(self.s_open*(self.dP-self.p_open)))+1/(1+math.exp(-self.s_fail*(self.dP-self.p_fail)))-1)

        
