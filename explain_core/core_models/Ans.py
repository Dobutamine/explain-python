import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Resistor import Resistor
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodTimeVaryingElastance import BloodTimeVaryingElastance
from explain_core.core_models.Heart import Heart
from explain_core.core_models.Breathing import Breathing
from explain_core.functions.ActivationFunction import activation_function
from explain_core.functions.BloodComposition import set_blood_composition

class Ans(BaseModel):
    # independent parameters
    baroreceptor_location: str = "AAR"
    chemoreceptor_locatio: str = "AAR"

    hr_targets: str = ["Heart"]
    mv_targets: str = ["Breathing"]
    venpool_targets: str = ["IVCE", "SVC"]
    cont_targets: str = ["LV","RV","LA","RA"]
    svr_targets: str = ["AD_INT", "AD_KID","AD_LS", "AAR_RUB", "AD_RLB"]
    pvr_targets: str = ["PA_LL", "PA_RL"]
    
    hr_effect_factor: float = 0.0
    mv_effect_factor: float = 0.0
    venpool_effect_factor: float = 0.0
    cont_effect_factor: float = 0.0
    svr_effect_factor: float = 0.0
    pvr_effect_factor: float = 0.0

    min_map: float = 20.0
    set_map: float = 57.5
    max_map: float = 100.0

    min_pco2: float = 20.0
    set_pco2: float = 57.5
    max_pco2: float = 100.0

    min_ph: float = 20.0
    set_ph: float = 57.5
    max_ph: float = 100.0

    min_po2: float = 20.0
    set_po2: float = 57.5
    max_po2: float = 100.0

    # local variables
    _baroreceptor: BloodCapacitance = {}
    _chemoreceptor: BloodCapacitance = {}

    _hr_targets: Heart = []
    _hr_effector = {}
    _mv_targets: Breathing = []
    _mv_effector = {}
    _venpool_targets: BloodCapacitance = []
    _venpool_effector = {}
    _cont_targets: BloodTimeVaryingElastance = []
    _cont_effector = {}
    _svr_targets: Resistor = []
    _svr_effector = {}
    _pvr_targets: Resistor = []
    _pvr_effector = {}

    _update_window: float = 0.015
    _update_counter: float = 0.0

    _pressures: float = []
    _data_window: int = 133

    def init_model(self, model: object) -> bool:
        # initialize the basemodel parent class
        super().init_model(model)

        # get a reference to the baroreceptor and chemoreceptor locations
        self._baroreceptor = self._model.models[self.baroreceptor_location]
        self._chemoreceptor = self._model.models[self.chemoreceptor_location]

        # get references to the ans targets
        for hr_target in self.hr_targets:
            self._hr_targets.append(self._model.models[hr_target])
        
        for mv_target in self.mv_targets:
            self._mv_targets.append(self._model.models[mv_target])

        for venpool_target in self.venpool_targets:
            self._venpool_targets.append(self._model.models[venpool_target])

        for cont_target in self.cont_targets:
            self._cont_targets.append(self._model.models[cont_target])

        for svr_target in self.svr_targets:
            self._svr_targets.append(self._model.models[svr_target])
        
        for pvr_target in self.pvr_targets:
            self._pvr_targets.append(self._model.models[pvr_target])

        # fill the list of pressures with the baroreflex start point
        self._pressures = [self.set_map] * self._data_window

        # initialize the effectors
        self.init_effectors()

        return self._is_initialized
    
    def set_map(self, _min, _set, _max):
        self.min_map = _min
        self.set_map = _set
        self.max_map = _max

    def set_pco2(self, _min, _set, _max):
        self.min_pco2 = _min
        self.set_pco2 = _set
        self.max_pco2 = _max
    
    def set_ph(self, _min, _set, _max):
        self.min_ph = _min
        self.set_ph = _set
        self.max_ph = _max
    
    def set_pco2(self, _min, _set, _max):
        self.min_po2 = _min
        self.set_po2 = _set
        self.max_po2 = _max
    
    def set_effects_map_on_hr(self, mxe_low, mxe_high, mxe_tc):
        self.hr_mxe_map_low = mxe_low
        self.hr_mxe_map_high = mxe_high
        self.hr_tc_map = mxe_tc
        self.init_effectors()
    
    def set_effects_pco2_on_hr(self, mxe_low, mxe_high, mxe_tc):
        self.hr_mxe_pco2_low = mxe_low
        self.hr_mxe_pco2_high = mxe_high
        self.hr_tc_pco2 = mxe_tc
        self.init_effectors()

    def set_effects_ph_on_hr(self, mxe_low, mxe_high, mxe_tc):
        self.hr_mxe_ph_low = mxe_low
        self.hr_mxe_ph_high = mxe_high
        self.hr_tc_ph = mxe_tc
        self.init_effectors()

    def set_effects_po2_on_hr(self, mxe_low, mxe_high, mxe_tc):
        self.hr_mxe_po2_low = mxe_low
        self.hr_mxe_po2_high = mxe_high
        self.hr_tc_po2 = mxe_tc
        self.init_effectors()


    def set_effects_map_on_mv(self, mxe_low, mxe_high, mxe_tc):
        self.mv_mxe_map_low = mxe_low
        self.mv_mxe_map_high = mxe_high
        self.mv_tc_map = mxe_tc
        self.init_effectors()
    
    def set_effects_pco2_on_mv(self, mxe_low, mxe_high, mxe_tc):
        self.mv_mxe_pco2_low = mxe_low
        self.mv_mxe_pco2_high = mxe_high
        self.mv_tc_pco2 = mxe_tc
        self.init_effectors()

    def set_effects_ph_on_mv(self, mxe_low, mxe_high, mxe_tc):
        self.mv_mxe_ph_low = mxe_low
        self.mv_mxe_ph_high = mxe_high
        self.mv_tc_ph = mxe_tc
        self.init_effectors()

    def set_effects_po2_on_mv(self, mxe_low, mxe_high, mxe_tc):
        self.mv_mxe_po2_low = mxe_low
        self.mv_mxe_po2_high = mxe_high
        self.mv_tc_po2 = mxe_tc
        self.init_effectors()

    
    def set_effects_map_on_venpool(self, mxe_low, mxe_high, mxe_tc):
        self.venpool_mxe_map_low = mxe_low
        self.venpool_mxe_map_high = mxe_high
        self.venpool_tc_map = mxe_tc
        self.init_effectors()
    
    def set_effects_pco2_on_venpool(self, mxe_low, mxe_high, mxe_tc):
        self.venpool_mxe_pco2_low = mxe_low
        self.venpool_mxe_pco2_high = mxe_high
        self.venpool_tc_pco2 = mxe_tc
        self.init_effectors()

    def set_effects_ph_on_venpool(self, mxe_low, mxe_high, mxe_tc):
        self.venpool_mxe_ph_low = mxe_low
        self.venpool_mxe_ph_high = mxe_high
        self.venpool_tc_ph = mxe_tc
        self.init_effectors()

    def set_effects_po2_on_venpool(self, mxe_low, mxe_high, mxe_tc):
        self.venpool_mxe_po2_low = mxe_low
        self.venpool_mxe_po2_high = mxe_high
        self.venpool_tc_po2 = mxe_tc
        self.init_effectors()


    def set_effects_map_on_cont(self, mxe_low, mxe_high, mxe_tc):
        self.cont_mxe_map_low = mxe_low
        self.cont_mxe_map_high = mxe_high
        self.cont_tc_map = mxe_tc
        self.init_effectors()
    
    def set_effects_pco2_on_cont(self, mxe_low, mxe_high, mxe_tc):
        self.cont_mxe_pco2_low = mxe_low
        self.cont_mxe_pco2_high = mxe_high
        self.cont_tc_pco2 = mxe_tc
        self.init_effectors()

    def set_effects_ph_on_cont(self, mxe_low, mxe_high, mxe_tc):
        self.cont_mxe_ph_low = mxe_low
        self.cont_mxe_ph_high = mxe_high
        self.cont_tc_ph = mxe_tc
        self.init_effectors()

    def set_effects_po2_on_cont(self, mxe_low, mxe_high, mxe_tc):
        self.cont_mxe_po2_low = mxe_low
        self.cont_mxe_po2_high = mxe_high
        self.cont_tc_po2 = mxe_tc
        self.init_effectors()

    
    def set_effects_map_on_svr(self, mxe_low, mxe_high, mxe_tc):
        self.svr_mxe_map_low = mxe_low
        self.svr_mxe_map_high = mxe_high
        self.svr_tc_map = mxe_tc
        self.init_effectors()
    
    def set_effects_pco2_on_svr(self, mxe_low, mxe_high, mxe_tc):
        self.svr_mxe_pco2_low = mxe_low
        self.svr_mxe_pco2_high = mxe_high
        self.svr_tc_pco2 = mxe_tc
        self.init_effectors()

    def set_effects_ph_on_svr(self, mxe_low, mxe_high, mxe_tc):
        self.svr_mxe_ph_low = mxe_low
        self.svr_mxe_ph_high = mxe_high
        self.svr_tc_ph = mxe_tc
        self.init_effectors()

    def set_effects_po2_on_svr(self, mxe_low, mxe_high, mxe_tc):
        self.svr_mxe_po2_low = mxe_low
        self.svr_mxe_po2_high = mxe_high
        self.svr_tc_po2 = mxe_tc
        self.init_effectors()


    def set_effects_map_on_pvr(self, mxe_low, mxe_high, mxe_tc):
        self.pvr_mxe_map_low = mxe_low
        self.pvr_mxe_map_high = mxe_high
        self.pvr_tc_map = mxe_tc
        self.init_effectors()
    
    def set_effects_pco2_on_pvr(self, mxe_low, mxe_high, mxe_tc):
        self.pvr_mxe_pco2_low = mxe_low
        self.pvr_mxe_pco2_high = mxe_high
        self.pvr_tc_pco2 = mxe_tc
        self.init_effectors()

    def set_effects_ph_on_pvr(self, mxe_low, mxe_high, mxe_tc):
        self.pvr_mxe_ph_low = mxe_low
        self.pvr_mxe_ph_high = mxe_high
        self.pvr_tc_ph = mxe_tc
        self.init_effectors()

    def set_effects_po2_on_pvr(self, mxe_low, mxe_high, mxe_tc):
        self.pvr_mxe_po2_low = mxe_low
        self.pvr_mxe_po2_high = mxe_high
        self.pvr_tc_po2 = mxe_tc
        self.init_effectors()


    def calc_model(self) -> None:
        # the ans model is executed at a lower frequency then the model step for performance reasons
        if self._update_counter > self._update_window:
            # insert a new pressure at the start of the list
            self._pressures.insert(0, self._baroreceptor.pres)

            # remove the last pressure from the list
            self._pressures.pop()
            
            # get the moving average of the pressure. We now have the mean arterial pressure
            self._map: float = sum(self._pressures) / (self._data_window)

            # for the chemoreflex we need the acidbase and oxygenation of the location of the chemoreceptor
            set_blood_composition(self._chemoreceptor)

            # get the chemoreflex inputs
            self._po2 = self._chemoreceptor.aboxy['po2']
            self._pco2 = self._chemoreceptor.aboxy['pco2']
            self._ph = self._chemoreceptor.aboxy['ph']

            # calculate the ans effect factors and apply the effects
            self.hr_effect_factor = self._hr_effector.calc_ans_effect_factor(self._map, self._pco2, self._ph, self._po2)
            for hrt in self._hr_targets:
                hrt.hr_ans_factor = self.hr_effect_factor

            self.mv_effect_factor = self._mv_effector.calc_ans_effect_factor(self._map, self._pco2, self._ph, self._po2)
            for mvt in self._mv_targets:
                mvt.mv_ans_factor = self.mv_effect_factor

            self.venpool_effect_factor = self._venpool_effector.calc_ans_effect_factor(self._map, self._pco2, self._ph, self._po2)
            for vpt in self._venpool_targets:
                vpt.u_vol_ans_factor = self.venpool_effect_factor

            self.cont_effect_factor = self._cont_effector.calc_ans_effect_factor(self._map, self._pco2, self._ph, self._po2)
            for contt in self._cont_targets:
                contt.el_max_ans_factor = self.cont_effect_factor

            self.svr_effect_factor = self._svr_effector.calc_ans_effect_factor(self._map, self._pco2, self._ph, self._po2)
            for svrt in self._svr_targets:
                svrt.r_ans_factor = self.svr_effect_factor
            
            self.pvr_effect_factor = self._pvr_effector.calc_ans_effect_factor(self._map, self._pco2, self._ph, self._po2)
            for pvrt in self._pvr_targets:
                pvrt.r_ans_factor = self.pvr_effect_factor

            # reset the update counter
            self._update_counter = 0.0

        self._update_counter += self._t

    def init_effectors(self):
        # set the class attributes (so for all classes)
        AnsTarget.min_map = self.min_map
        AnsTarget.set_map = self.set_map
        AnsTarget.max_map = self.max_map

        AnsTarget.min_pco2 = self.min_pco2
        AnsTarget.set_pco2 = self.set_pco2
        AnsTarget.max_pco2 = self.max_pco2
        
        AnsTarget.min_ph = self.min_ph
        AnsTarget.set_ph = self.set_ph
        AnsTarget.max_ph = self.max_ph
        
        AnsTarget.min_po2 = self.min_po2
        AnsTarget.set_po2 = self.set_po2
        AnsTarget.max_po2 = self.max_po2

        self._hr_effector = AnsTarget()
        self._hr_effector.factor = self.hr_factor
        self._hr_effector.factor_max = self.hr_factor_max
        self._hr_effector.factor_min = self.hr_factor_min
        self._hr_effector.mxe_map_low = self.hr_mxe_map_low
        self._hr_effector.mxe_map_high = self.hr_mxe_map_high
        self._hr_effector.tc_map = self.hr_tc_map
        self._hr_effector.mxe_pco2_low = self.hr_mxe_pco2_low
        self._hr_effector.mxe_pco2_high = self.hr_mxe_pco2_high
        self._hr_effector.tc_pco2 = self.hr_tc_pco2
        self._hr_effector.mxe_ph_low = self.hr_mxe_ph_low
        self._hr_effector.mxe_ph_high = self.hr_mxe_ph_high
        self._hr_effector.tc_ph = self.hr_tc_ph
        self._hr_effector.mxe_po2_low = self.hr_mxe_po2_low
        self._hr_effector.mxe_po2_high = self.hr_mxe_po2_high
        self._hr_effector.tc_po2 = self.hr_tc_po2
        self._hr_effector.calc_gains()

        self._mv_effector = AnsTarget()
        self._mv_effector.factor = self.mv_factor
        self._mv_effector.factor_max = self.mv_factor_max
        self._mv_effector.factor_min = self.mv_factor_min
        self._mv_effector.mxe_map_low = self.mv_mxe_map_low
        self._mv_effector.mxe_map_high = self.mv_mxe_map_high
        self._mv_effector.tc_map = self.mv_tc_map
        self._mv_effector.mxe_pco2_low = self.mv_mxe_pco2_low
        self._mv_effector.mxe_pco2_high = self.mv_mxe_pco2_high
        self._mv_effector.tc_pco2 = self.mv_tc_pco2
        self._mv_effector.mxe_ph_low = self.mv_mxe_ph_low
        self._mv_effector.mxe_ph_high = self.mv_mxe_ph_high
        self._mv_effector.tc_ph = self.mv_tc_ph
        self._mv_effector.mxe_po2_low = self.mv_mxe_po2_low
        self._mv_effector.mxe_po2_high = self.mv_mxe_po2_high
        self._mv_effector.tc_po2 = self.mv_tc_po2
        self._mv_effector.calc_gains()

        self._venpool_effector = AnsTarget()
        self._venpool_effector.factor = self.venpool_factor
        self._venpool_effector.factor_max = self.venpool_factor_max
        self._venpool_effector.factor_min = self.venpool_factor_min
        self._venpool_effector.mxe_map_low = self.venpool_mxe_map_low
        self._venpool_effector.mxe_map_high = self.venpool_mxe_map_high
        self._venpool_effector.tc_map = self.venpool_tc_map
        self._venpool_effector.mxe_pco2_low = self.venpool_mxe_pco2_low
        self._venpool_effector.mxe_pco2_high = self.venpool_mxe_pco2_high
        self._venpool_effector.tc_pco2 = self.venpool_tc_pco2
        self._venpool_effector.mxe_ph_low = self.venpool_mxe_ph_low
        self._venpool_effector.mxe_ph_high = self.venpool_mxe_ph_high
        self._venpool_effector.tc_ph = self.venpool_tc_ph
        self._venpool_effector.mxe_po2_low = self.venpool_mxe_po2_low
        self._venpool_effector.mxe_po2_high = self.venpool_mxe_po2_high
        self._venpool_effector.tc_po2 = self.venpool_tc_po2
        self._venpool_effector.calc_gains()

        self._cont_effector = AnsTarget()
        self._cont_effector.factor = self.cont_factor
        self._cont_effector.factor_max = self.cont_factor_max
        self._cont_effector.factor_min = self.cont_factor_min
        self._cont_effector.mxe_map_low = self.cont_mxe_map_low
        self._cont_effector.mxe_map_high = self.cont_mxe_map_high
        self._cont_effector.tc_map = self.cont_tc_map
        self._cont_effector.mxe_pco2_low = self.cont_mxe_pco2_low
        self._cont_effector.mxe_pco2_high = self.cont_mxe_pco2_high
        self._cont_effector.tc_pco2 = self.cont_tc_pco2
        self._cont_effector.mxe_ph_low = self.cont_mxe_ph_low
        self._cont_effector.mxe_ph_high = self.cont_mxe_ph_high
        self._cont_effector.tc_ph = self.cont_tc_ph
        self._cont_effector.mxe_po2_low = self.cont_mxe_po2_low
        self._cont_effector.mxe_po2_high = self.cont_mxe_po2_high
        self._cont_effector.tc_po2 = self.cont_tc_po2
        self._cont_effector.calc_gains()

        self._svr_effector = AnsTarget()
        self._svr_effector.factor = self.svr_factor
        self._svr_effector.factor_max = self.svr_factor_max
        self._svr_effector.factor_min = self.svr_factor_min
        self._svr_effector.mxe_map_low = self.svr_mxe_map_low
        self._svr_effector.mxe_map_high = self.svr_mxe_map_high
        self._svr_effector.tc_map = self.svr_tc_map
        self._svr_effector.mxe_pco2_low = self.svr_mxe_pco2_low
        self._svr_effector.mxe_pco2_high = self.svr_mxe_pco2_high
        self._svr_effector.tc_pco2 = self.svr_tc_pco2
        self._svr_effector.mxe_ph_low = self.svr_mxe_ph_low
        self._svr_effector.mxe_ph_high = self.svr_mxe_ph_high
        self._svr_effector.tc_ph = self.svr_tc_ph
        self._svr_effector.mxe_po2_low = self.svr_mxe_po2_low
        self._svr_effector.mxe_po2_high = self.svr_mxe_po2_high
        self._svr_effector.tc_po2 = self.svr_tc_po2
        self._svr_effector.calc_gains()

        self._pvr_effector = AnsTarget()
        self._pvr_effector.factor = self.pvr_factor
        self._pvr_effector.factor_max = self.pvr_factor_max
        self._pvr_effector.factor_min = self.pvr_factor_min
        self._pvr_effector.mxe_map_low = self.pvr_mxe_map_low
        self._pvr_effector.mxe_map_high = self.pvr_mxe_map_high
        self._pvr_effector.tc_map = self.pvr_tc_map
        self._pvr_effector.mxe_pco2_low = self.pvr_mxe_pco2_low
        self._pvr_effector.mxe_pco2_high = self.pvr_mxe_pco2_high
        self._pvr_effector.tc_pco2 = self.pvr_tc_pco2
        self._pvr_effector.mxe_ph_low = self.pvr_mxe_ph_low
        self._pvr_effector.mxe_ph_high = self.pvr_mxe_ph_high
        self._pvr_effector.tc_ph = self.pvr_tc_ph
        self._pvr_effector.mxe_po2_low = self.pvr_mxe_po2_low
        self._pvr_effector.mxe_po2_high = self.pvr_mxe_po2_high
        self._pvr_effector.tc_po2 = self.pvr_tc_po2
        self._pvr_effector.calc_gains()


    
class AnsTarget:
    is_enabled: bool = True

    min_map: float = 20.0
    set_map: float = 57.5
    max_map: float = 100.0

    min_pco2: float = 20.0
    set_pco2: float = 57.5
    max_pco2: float = 100.0

    min_ph: float = 20.0
    set_ph: float = 57.5
    max_ph: float = 100.0

    min_po2: float = 20.0
    set_po2: float = 57.5
    max_po2: float = 100.0
    
    factor: float = 1.0
    factor_max: float = 2.5
    factor_min: float = 0.01

    mxe_map_low: float = 0.0
    g_map_low: float = 0.0
    mxe_map_high: float = 0.0
    g_map_high: float = 0.0
    tc_map: float = 1.0

    mxe_pco2_low: float = 0.0
    g_pco2_low: float = 0.0
    mxe_pco2_high: float = 0.0
    g_pco2_high: float = 0.0
    tc_pco2: float = 1.0

    mxe_ph_low: float = 0.0
    g_ph_low: float = 0.0
    mxe_ph_high: float = 0.0
    g_ph_high: float = 0.0
    tc_ph: float = 1.0

    mxe_po2_low: float = 0.0
    g_po2_low: float = 0.0
    mxe_po2_high: float = 0.0
    g_po2_high: float = 0.0
    tc_po2: float = 1.0

    _a_map: float = 0.0
    _a_pco2: float = 0.0
    _a_ph: float = 0.0
    _a_po2: float = 0.0

    _d_map: float = 0.0
    _d_pco2: float = 0.0
    _d_ph: float = 0.0
    _d_po2: float = 0.0

    def calc_gains(self):
        self.g_map_low = self.translate_mxe(self.mxe_map_low) / (self.min_map - self.set_map)
        self.g_map_high = self.translate_mxe(self.mxe_map_high) / (self.max_map - self.set_map)

        self.g_pco2_low = self.translate_mxe(self.mxe_pco2_low) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high = self.translate_mxe(self.mxe_pco2_high) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low = self.translate_mxe(self.mxe_ph_low) / (self.min_ph - self.set_ph)
        self.g_ph_high = self.translate_mxe(self.mxe_ph_high) / (self.max_ph - self.set_ph)

        self.g_po2_low = self.translate_mxe(self.mxe_po2_low) / (self.min_po2 - self.set_po2)
        self.g_po2_high = self.translate_mxe(self.mxe_po2_high) / (self.max_po2 - self.set_po2)

    def calc_ans_effect_factor(self, _map: float, _pco2: float, _ph: float, _po2: float) -> float:
        # calculate the activation functions
        self._a_map = activation_function(_map, self.max_map, self.set_map, self.min_map)
        self._a_po2 = activation_function(_po2, self.max_po2, self.set_po2, self.min_po2)
        self._a_pco2 = activation_function(_pco2, self.max_pco2, self.set_pco2, self.min_pco2)
        self._a_ph = activation_function(_ph, self.max_ph, self.set_ph, self.min_ph)

        # apply the time constants
        self._d_map = self.time_constant(self.tc_map, self._d_map, self._a_map)
        self._d_pco2 = self.time_constant(self.tc_pco2, self._d_pco2, self._a_pco2)
        self._d_ph = self.time_constant(self.tc_ph, self._d_ph, self._a_ph)
        self._d_po2 = self.time_constant(self.tc_po2, self._d_po2, self._a_po2)

        # reset the cumulative hr factor
        cum_factor: float = 0.0
        # mean arterial pressure influence
        if self._d_map > 0:
            cum_factor = self.g_map_high * self._d_map
        else:
            cum_factor = self.g_map_low * self._d_map
        # pco2 influence
        if self._d_pco2 > 0:
            cum_factor += self.g_pco2_high * self._d_pco2
        else:
            cum_factor += self.g_pco2_low * self._d_pco2
        # ph influence
        if self._d_ph > 0:
            cum_factor += self.g_ph_high * self._d_ph
        else:
            cum_factor += self.g_ph_low * self._d_ph
        # po2 influence
        if self._d_po2 > 0:
            cum_factor += self.g_po2_high * self._d_po2
        else:
            cum_factor += self.g_po2_low * self._d_po2
        # calculate the new heartrate factor
        self.factor = self.calc_factor(cum_factor)
        # gueard the minimum and maximum factor values
        if self.factor > self.factor_max:
            self.factor = self.factor_max
        if self.factor < self.factor_min:
            self.factor = self.factor_min

        # return the calculated factor
        return self.factor

    def calc_factor(self, cum_factor) -> float:
        # reset the cumulative hr factor
        factor: float = 1.0
        if cum_factor > 0:
            factor = 1.0 + cum_factor
        if cum_factor < 0:
            factor = 1.0 - cum_factor
            factor = 1.0 / factor
        return factor

    def time_constant(self, tc, cv, nv, t = 0.015):
        return t * (( 1.0 / tc) * (-cv + nv)) + cv

    def translate_mxe(self, mxe) -> float:
        # a mxe of 1.5 that max effect is 1.5 * reference value (hr_ref, mv_ref, venpool_ref, cont_ref, svr_ref, pvr_ref)
        if mxe > 1.0:
            mxe = mxe - 1.0
            return mxe
        
        if mxe > 0.0 and mxe < 1.0:
            mxe = (-1.0 / mxe) + 1.0
            return mxe

        return 0
