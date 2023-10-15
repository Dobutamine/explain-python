from explain_core.base_models.BaseModel import BaseModel


class Resuscitation(BaseModel):
    # independent parameters
    chest_comp_freq: float = 100.0          # number of chest compressions per minute
    chest_comp_pres: float = 20.0           # pressure of the chest compressions in mmHg
    vent_freq: float = 30.0                 # number of ventilations per minute
    vent_pres: float = 20.0                 # pressure of the ventilations in mmHg
    vent_insp_time: float = 1.0             # inspiration time of the ventilations
    vent_comp_ratio: float = 0.33           # ratio of ventilation to compressions
    thorax_model: str = "THORAX"

    # dependent parameters

    # local parameters
    _thorax: BaseModel = {}

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        self._thorax = self._model.models[self.thorax_model]

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized
    
    def calc_model(self) -> None:
        pass

    
    

