import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.Container import Container

class Resuscitation(BaseModel):
    # independent parameters
    chest_comp_freq: float = 100.0          # number of chest compressions per minute
    chest_comp_pres: float = 20.0           # pressure of the chest compressions in mmHg
    vent_freq: float = 30.0                 # number of ventilations per minute
    vent_pres: float = 20.0                 # pressure of the ventilations in mmHg
    vent_fio2: float = 0.21                 # fio2 of the ventilations
    vent_insp_time: float = 1.0             # inspiration time of the ventilations
    vent_comp_ratio: float = 0.33           # ratio of ventilation to compressions
    thorax_model: str = "THORAX"

    # dependent parameters
    cor_flow: float = 0.0                   # coronary flow in l/min
    cor_o2_flow: float = 0.0                # coronary o2 flow in ml O2/min
    brain_flow: float = 0.0                 # brain flow in l/min
    brain_o2_flow: float = 0.0              # brain o2 flow in l/min
    lvo: float = 0.0                        # left ventricular output in l/min
    rvo: float = 0.0                        # right ventricular output in l/min

    # local parameters
    _thorax: BaseModel = {}
    _cpr_enabled: bool = False
    _comp_interval: float = 0.0
    _comp_duration: float = 0.0
    _comp_duration_counter: float = 0.0
    _comp_time_counter: float = 0.0
    _comp_pres: float = 0.0
    _comp_running: bool = False

    _x: float = 0.0
    _x_step: float = 0.0


    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the heart
        self._thorax = self._model.models[self.thorax_model]

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized
    
    def calc_model(self) -> None:
        if not self._cpr_enabled:
            return
        
        # determine the interval between the compressions in seconds
        self._comp_interval = 60.0 / self.chest_comp_freq
        self._comp_duration = self._comp_interval
        self._x_step = math.pi / (self._comp_duration / self._t)


        # is it time for a compression?
        if self._comp_time_counter > self._comp_interval:
            # reset the timer
            self._comp_time_counter = 0.0
            # signal that the compression is starting
            self._comp_running = True
            # reset the compression duration counter
            self._comp_duration_counter = 0.0
            
        # start the compression
        if self._comp_running:
            # increase the compression timer
            self._comp_duration_counter += self._t
            # increase the compression pressure
            self._comp_pres = math.sin(self._x)
            self._x += self._x_step


        # has the compression elapsed?
        if self._comp_duration_counter > self._comp_duration:
            # signal that the compression is not running anymore
            self._comp_running = False
            # reset the compression duration counter
            self._comp_duration_counter = 0.0
            # reset the compression pressure
            self._comp_pres = 0.0
            # reset the signal
            self._x = 0.0

        self._comp_time_counter += self._t

    
    def start_cpr(self) -> None:
        self._cpr_enabled = True

    def stop_cpr(self) -> None:
        self._cpr_enabled = False

    def cardiac_arrest(self, state) -> None:
        pass


    

