import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Resistor import Resistor
from explain_core.base_models.TimeVaryingElastance import TimeVaryingElastance
from explain_core.core_models.Container import Container


class Heart(BaseModel):
    # independent variables
    rhythm_type: int = 0
    heart_rate: float = 120.0
    heart_rate_ref: float = 140.0
    heart_rate_override: bool = False
    heart_rate_forced: float = 30.0
    pq_time: float = 0.0
    qrs_time: float = 0.0
    qt_time: float = 0.0
    hr_ans_factor: float = 1.0
    ans_activity_factor: float = 1.0
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
    _mv: Resistor = {}
    _lv: TimeVaryingElastance = {}
    _av: Resistor = {}
    _ra: TimeVaryingElastance = {}
    _tv: Resistor = {}
    _rv: TimeVaryingElastance = {}
    _pv: Resistor = {}
    _cor: TimeVaryingElastance = {}
    _pc: Container = {}
    _cor_ra: Resistor = {}

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
        self._mv = self._model.models[self.mitral_valve]
        self._tv = self._model.models[self.tricuspid_valve]
        self._pv = self._model.models[self.pulmonary_valve]
        self._av = self._model.models[self.aortic_valve]
        self._cor = self._model.models[self.coronaries]
        self._cor_ra = self._model.models[self.coronary_sinus]
        self._pc = self._model.models[self.pericardium]

    def calc_model(self) -> None:
        # calculate the heartrate from the reference value and all other influences
        self.heart_rate = (
            self.heart_rate_ref
            + (self.hr_ans_factor * self.heart_rate_ref - self.heart_rate_ref)
            * self.ans_activity_factor
            + (self.hr_mob_factor * self.heart_rate_ref - self.heart_rate_ref)
            + (self.hr_temp_factor * self.heart_rate_ref - self.heart_rate_ref)
            + (self.hr_drug_factor * self.heart_rate_ref - self.heart_rate_ref)
        )

        if self.heart_rate_override:
            self.heart_rate = self.heart_rate_forced

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
            self.aaf = math.sin(math.pi * (self.ncc_atrial / (self.pq_time / self._t)))
        else:
            self.aaf = 0.0

        # calculate the ventricular activation factor
        _ventricular_duration: float = self.qrs_time + self.cqt_time
        if (
            self.ncc_ventricular >= 0
            and self.ncc_ventricular < _ventricular_duration / self._t
        ):
            self.vaf = (
                self.ncc_ventricular / (self._kn * (_ventricular_duration / self._t))
            ) * math.sin(
                math.pi * (self.ncc_ventricular / (_ventricular_duration / self._t))
            )
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

    def heart_rate_ref(self, new_hr_ref):
        if new_hr_ref > 0.0:
            self.heart_rate_ref = new_hr_ref

    def set_rhythm_type(self, new_rt):
        self.rhythm_type = new_rt

    def set_pq_time(self, new_pq_time):
        if new_pq_time > 0.0:
            self.pq_time = new_pq_time

    def set_qrs_time(self, new_qrs_time):
        if new_qrs_time > 0.0:
            self.qrs_time = new_qrs_time

    def set_qt_time(self, new_qt_time):
        if new_qt_time > 0.0:
            self.qt_time = new_qt_time

    def change_mitral_valve_resistance(self, res_change):
        if res_change > 0.0:
            self._mv.set_r_for_factor(res_change)

    def change_tricuspid_valve_resistance(self, res_change):
        if res_change > 0.0:
            self._tv.set_r_for_factor(res_change)

    def change_aortic_valve_resistance(self, res_change):
        if res_change > 0.0:
            self._av.set_r_for_factor(res_change)

    def change_pulmonary_valve_resistance(self, res_change):
        if res_change > 0.0:
            self._pv.set_r_for_factor(res_change)

    def change_mitral_valve_regurgitation(self, res_change):
        if res_change > 0.0:
            self._mv.set_r_back_factor(res_change)
            self._mv.allow_backflow()
        else:
            self._mv.set_r_back_factor(1.0)
            self._mv.prevent_backflow()

    def change_tricuspid_valve_regurgitation(self, res_change):
        if res_change > 0.0:
            self._tv.set_r_back_factor(res_change)
            self._tv.allow_backflow()
        else:
            self._tv.set_r_back_factor(1.0)
            self._tv.prevent_backflow()

    def change_aortic_valve_regurgitation(self, res_change):
        if res_change > 0.0:
            self._av.set_r_back_factor(res_change)
            self._av.allow_backflow()
        else:
            self._av.set_r_back_factor(1.0)
            self._av.prevent_backflow()

    def change_pulmonary_valve_regurgitation(self, res_change):
        if res_change > 0.0:
            self._pv.set_r_back_factor(res_change)
            self._pv.allow_backflow()
        else:
            self._pv.set_r_back_factor(1.0)
            self._pv.prevent_backflow()

    def change_contractility(self, cont_change):
        if cont_change > 0.0:
            self._lv.el_max_factor = cont_change
            self._la.el_max_factor = cont_change
            self._rv.el_max_factor = cont_change
            self._ra.el_max_factor = cont_change

    def change_left_heart_contractility(self, cont_change):
        if cont_change > 0.0:
            self._lv.el_max_factor = cont_change
            self._la.el_max_factor = cont_change

    def change_right_heart_contractility(self, cont_change):
        if cont_change > 0.0:
            self._rv.el_max_factor = cont_change
            self._ra.el_max_factor = cont_change

    def change_relaxation(self, relax_change):
        if relax_change > 0.0:
            self._lv.el_min_factor = relax_change
            self._la.el_min_factor = relax_change
            self._rv.el_min_factor = relax_change
            self._ra.el_min_factor = relax_change

    def change_left_heart_relaxation(self, relax_change):
        if relax_change > 0.0:
            self._lv.el_min_factor = relax_change
            self._la.el_min_factor = relax_change
            self._rv.el_min_factor = relax_change
            self._ra.el_min_factor = relax_change

    def change_right_heart_relaxation(self, relax_change):
        if relax_change > 0.0:
            self._rv.el_min_factor = relax_change
            self._ra.el_min_factor = relax_change

    def change_pericardium_compliance(self, comp_change):
        if comp_change > 0.0:
            self._pc.el_base_factor = 1.0 / comp_change

    def set_pericardium_effusion(self, extra_volume):
        if extra_volume >= 0.0:
            self._pc.vol_extra = extra_volume
