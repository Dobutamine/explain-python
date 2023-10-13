import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.TimeVaryingElastance import TimeVaryingElastance


class Heart(BaseModel):
    # independent variables
    heart_rate: float = 120.0
    heart_rate_ref: float = 140.0
    pq_time: float = 0.0
    qrs_time: float = 0.0
    qt_time: float = 0.0
    hr_ans_factor: float = 1.0
    hr_mob_factor: float = 1.0
    hr_temp_factor: float = 1.0
    hr_drug_factor: float = 1.0

    # dependent variables
    cqt_time: float = 0.0
    ncc_atrial: int = 0
    ncc_ventricular: int = 0
    aaf: float = 0.0
    vaf: float = 0.0

    # local variables and state variables
    _la: TimeVaryingElastance = {}
    _lv: TimeVaryingElastance = {}
    _ra: TimeVaryingElastance = {}
    _rv: TimeVaryingElastance = {}
    _cor: TimeVaryingElastance = {}

    _sa_node_interval: float = 0.0
    _sa_node_timer: float = 0.0
    _pq_running: bool = False
    _pq_timer: float = 0.0
    _qrs_running: bool = False
    _qrs_timer: float = 0.0
    _qt_running: bool = False
    _qt_timer: float = 0.0
    _ventricle_is_refractory: bool = False
    _kn: float = 0.579

    def init_model(self, model: object) -> bool:
       
        # init the parent class
        result = super().init_model(model)
        
        # get a reference to the heart models
        self._la = self._model.models[self.left_atrium]
        self._ra = self._model.models[self.right_atrium]
        self._lv = self._model.models[self.left_ventricle]
        self._rv = self._model.models[self.right_ventricle]
        self._cor = self._model.models[self.coronaries]

    def calc_model(self) -> None:
        # calculate the heartrate from the reference value and all other influences
        self.heart_rate = self.heart_rate_ref * self.hr_ans_factor * self.hr_mob_factor * self.hr_temp_factor * self.hr_drug_factor

        # calculate the qtc time depending on the heartrate
        self.cqt_time = self.calc_qtc(self.heart_rate)

        # calculate the sinus node interval in seconds depending on the heart rate
        self._sa_node_interval = 60.0 / self.heart_rate

        # has the sinus node period elapsed?
        if self._sa_node_timer > self._sa_node_interval:
            # reset the sinus node timer
            self._sa_node_timer = 0.0
            # signal that the pq-time starts running
            self._pq_running = True
            # reset the atrial activation curve counter
            self.ncc_atrial = -1

        # has the pq time period elapsed?
        if self._pq_timer > self.pq_time:
            # reset the pq timer
            self._pq_timer = 0.0
            # signal that the pq timer has stopped
            self._pq_running = False
            # check whether the ventricles are in a refractory state
            if not self._ventricle_is_refractory:
                # signal that the qrs time starts running
                self._qrs_running = True
                # reset the ventricular activation curve
                self.ncc_ventricular = -1

        # has the qrs time period elapsed?
        if self._qrs_timer > self.qrs_time:
            # reset the qrs timer
            self._qrs_timer = 0.0
            # signal that the qrs timer has stopped
            self._qrs_running = False
            # signal that the at timer starts running
            self._qt_running = True
            # signal that the ventricles are now in a refractory state
            self._ventricle_is_refractory = True

        # has the qt time period elapsed?
        if self._qt_timer > self.cqt_time:
            # reset the qt timer
            self._qt_timer = 0.0
            # signal that the qt timer has stopped
            self._qt_running = False
            # signal that the ventricles are coming out of their refractory state
            self._ventricle_is_refractory = False

        # increase the timers with the modeling stepsize as set by the model base class
        self._sa_node_timer += self._t
        if self._pq_running:
            self._pq_timer += self._t
        if self._qrs_running:
            self._qrs_timer += self._t
        if self._qt_running:
            self._qt_timer += self._t

        # increase the heart activation function counters
        self.ncc_atrial += 1
        self.ncc_ventricular += 1

        # calculate the varying elastance factor
        self.calc_varying_elastance()

    def calc_varying_elastance(self) -> None:
        # calculate the atrial activation factor
        if self.ncc_atrial >= 0 and self.ncc_atrial < self.pq_time / self._t:
            self.aaf = math.sin(
                math.pi * (self.ncc_atrial / (self.pq_time / self._t)))
        else:
            self.aaf = 0.0

        # calculate the ventricular activation factor
        _ventricular_duration: float = self.qrs_time + self.cqt_time
        if self.ncc_ventricular >= 0 and self.ncc_ventricular < _ventricular_duration / self._t:
            self.vaf = (self.ncc_ventricular / (self._kn * (_ventricular_duration / self._t))) * \
                math.sin(math.pi * (self.ncc_ventricular /
                         (_ventricular_duration / self._t)))
        else:
            self.vaf = 0.0

        # transfer the activation factor to the heart components
        self._la.act_factor = self.aaf
        self._ra.act_factor = self.aaf
        self._lv.act_factor = self.vaf
        self._rv.act_factor = self.vaf
        self._cor.act_factor = self.vaf

    def calc_qtc(self, hr: float) -> float:
        if hr > 10:
            return self.qt_time * math.sqrt(60.0 / hr)
        else:
            return self.qt_time * math.sqrt(6)
