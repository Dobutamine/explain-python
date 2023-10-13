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
    baroreceptor_location: str = "AA"
    chemoreceptor_locatio: str = "AA"

    hr_targets: str = ["Heart"]
    mv_targets: str = ["Breathing"]
    venpool_targets: str = ["IVCE", "SVC"]
    cont_targets: str = ["LV","RV","LA","RA"]
    svr_targets: str = ["AD_INT", "AD_KID","AD_LS", "AAR_RUB", "AD_RLB"]
    pvr_targets: str = ["PA_LL", "PA_RL"]

    hr_factor: float = 1.0
    hr_factor_max: float = 5.0
    hr_factor_min: float = 0.1

    mv_factor: float = 1.0
    mv_factor_max: float = 5.0
    mv_factor_min: float = 0.1

    venpool_ref: float = 1.0
    venpool_factor:float = 1.0
    venpool_factor_max:float = 5.0
    venpool_factor_min:float = 0.1

    cont_ref: float = 1.0
    cont_factor: float = 1.0
    cont_factor_max: float = 5.0
    cont_factor_min: float = 0.1

    svr_ref: float = 1.0
    svr_factor: float = 1.0
    svr_factor_max: float = 5.0
    svr_factor_min: float = 0.1

    pvr_ref: float = 1.0
    pvr_factor: float = 1.0
    pvr_factor_max: float = 5.0
    pvr_factor_min: float = 0.1

    min_map: float = 20.0
    set_map: float = 57.5
    max_map: float = 100.0
    mxe_map_low_hr: float = 0.0
    mxe_map_high_hr: float = 0.0
    mxe_map_low_mv: float = 0.0
    mxe_map_high_mv: float = 0.0
    mxe_map_low_cont: float = 0.0
    mxe_map_high_cont: float = 0.0
    mxe_map_low_venpool: float = 0.0
    mxe_map_high_venpool: float = 0.0
    mxe_map_low_svr: float = 0.0
    mxe_map_high_svr: float = 0.0
    mxe_map_low_pvr: float = 0.0
    mxe_map_high_pvr: float = 0.0
    tc_map_hr: float = 2.0
    tc_map_mv: float = 30.0
    tc_map_venpool: float = 30.0
    tc_map_cont: float = 5.0
    tc_map_svr: float = 30.0
    tc_map_pvr: float = 30.0

    min_pco2: float = 20.0
    set_pco2: float = 57.5
    max_pco2: float = 100.0
    mxe_pco2_low_hr: float = 0.0
    mxe_pco2_high_hr: float = 0.0
    mxe_pco2_low_mv: float = 0.0
    mxe_pco2_high_mv: float = 0.0
    mxe_pco2_low_cont: float = 0.0
    mxe_pco2_high_cont: float = 0.0
    mxe_pco2_low_venpool: float = 0.0
    mxe_pco2_high_venpool: float = 0.0
    mxe_pco2_low_svr: float = 0.0
    mxe_pco2_high_svr: float = 0.0
    mxe_pco2_low_pvr: float = 0.0
    mxe_pco2_high_pvr: float = 0.0
    tc_pco2_hr: float = 2.0
    tc_pco2_mv: float = 30.0
    tc_pco2_venpool: float = 30.0
    tc_pco2_cont: float = 5.0
    tc_pco2_svr: float = 30.0
    tc_pco2_pvr: float = 30.0

    min_ph: float = 20.0
    set_ph: float = 57.5
    max_ph: float = 100.0
    mxe_ph_low_hr: float = 0.0
    mxe_ph_high_hr: float = 0.0
    mxe_ph_low_mv: float = 0.0
    mxe_ph_high_mv: float = 0.0
    mxe_ph_low_cont: float = 0.0
    mxe_ph_high_cont: float = 0.0
    mxe_ph_low_venpool: float = 0.0
    mxe_ph_high_venpool: float = 0.0
    mxe_ph_low_svr: float = 0.0
    mxe_ph_high_svr: float = 0.0
    mxe_ph_low_pvr: float = 0.0
    mxe_ph_high_pvr: float = 0.0
    tc_ph_hr: float = 2.0
    tc_ph_mv: float = 30.0
    tc_ph_venpool: float = 30.0
    tc_ph_cont: float = 5.0
    tc_ph_svr: float = 30.0
    tc_ph_pvr: float = 30.0

    min_po2: float = 20.0
    set_po2: float = 57.5
    max_po2: float = 100.0
    mxe_po2_low_hr: float = 0.0
    mxe_po2_high_hr: float = 0.0
    mxe_po2_low_mv: float = 0.0
    mxe_po2_high_mv: float = 0.0
    mxe_po2_low_cont: float = 0.0
    mxe_po2_high_cont: float = 0.0
    mxe_po2_low_venpool: float = 0.0
    mxe_po2_high_venpool: float = 0.0
    mxe_po2_low_svr: float = 0.0
    mxe_po2_high_svr: float = 0.0
    mxe_po2_low_pvr: float = 0.0
    mxe_po2_high_pvr: float = 0.0
    tc_po2_hr: float = 2.0
    tc_po2_mv: float = 30.0
    tc_po2_venpool: float = 30.0
    tc_po2_cont: float = 5.0
    tc_po2_svr: float = 30.0
    tc_po2_pvr: float = 30.0

    hr_effects_enabled: bool = True
    mv_effects_enabled: bool = True
    venpool_effects_enabled: bool = True
    cont_effects_enabled: bool = True
    svr_effects_enabled: bool = True
    pvr_effects_enabled: bool = True

    # dependent variables
    g_map_high_hr: float = 0.0
    g_map_low_hr: float = 0.0
    g_map_high_mv: float = 0.0
    g_map_low_mv: float = 0.0
    g_map_high_venpool: float = 0.0
    g_map_low_venpool: float = 0.0
    g_map_high_cont: float = 0.0
    g_map_low_cont: float = 0.0
    g_map_high_svr: float = 0.0
    g_map_low_svr: float = 0.0
    g_map_high_pvr: float = 0.0
    g_map_low_pvr: float = 0.0

    g_pco2_high_hr: float = 0.0
    g_pco2_low_hr: float = 0.0
    g_pco2_high_mv: float = 0.0
    g_pco2_low_mv: float = 0.0
    g_pco2_high_venpool: float = 0.0
    g_pco2_low_venpool: float = 0.0
    g_pco2_high_cont: float = 0.0
    g_pco2_low_cont: float = 0.0
    g_pco2_high_svr: float = 0.0
    g_pco2_low_svr: float = 0.0
    g_pco2_high_pvr: float = 0.0
    g_pco2_low_pvr: float = 0.0

    g_ph_high_hr: float = 0.0
    g_ph_low_hr: float = 0.0
    g_ph_high_mv: float = 0.0
    g_ph_low_mv: float = 0.0
    g_ph_high_venpool: float = 0.0
    g_ph_low_venpool: float = 0.0
    g_ph_high_cont: float = 0.0
    g_ph_low_cont: float = 0.0
    g_ph_high_svr: float = 0.0
    g_ph_low_svr: float = 0.0
    g_ph_high_pvr: float = 0.0
    g_ph_low_pvr: float = 0.0

    g_po2_high_hr: float = 0.0
    g_po2_low_hr: float = 0.0
    g_po2_high_mv: float = 0.0
    g_po2_low_mv: float = 0.0
    g_po2_high_venpool: float = 0.0
    g_po2_low_venpool: float = 0.0
    g_po2_high_cont: float = 0.0
    g_po2_low_cont: float = 0.0
    g_po2_high_svr: float = 0.0
    g_po2_low_svr: float = 0.0
    g_po2_high_pvr: float = 0.0
    g_po2_low_pvr: float = 0.0

    # local variables
    _baroreceptor: BloodCapacitance = {}
    _chemoreceptor: BloodCapacitance = {}

    _hr_targets: Heart = []
    _mv_targets: Breathing = []
    _venpool_targets: BloodCapacitance = []
    _cont_targets: BloodTimeVaryingElastance = []
    _svr_targets: Resistor = []
    _pvr_targets: Resistor = []

    _map: float = 0.0
    _ph: float = 0.0
    _pco2: float = 0.0
    _po2: float = 0.0

    _a_map: float = 0.0
    _a_ph: float = 0.0
    _a_po2: float = 0.0
    _a_pco2: float = 0.0

    _d_map_hr: float = 0.0
    _d_po2_hr: float = 0.0
    _d_pco2_hr: float = 0.0
    _d_ph_hr: float = 0.0

    _d_map_venpool: float = 0.0
    _d_po2_venpool: float = 0.0
    _d_pco2_venpool: float = 0.0
    _d_ph_venpool: float = 0.0

    _d_map_cont: float = 0.0
    _d_po2_cont: float = 0.0
    _d_pco2_cont: float = 0.0
    _d_ph_cont: float = 0.0

    _d_map_svr: float = 0.0
    _d_po2_svr: float = 0.0
    _d_pco2_svr: float = 0.0
    _d_ph_svr: float = 0.0

    _d_map_pvr: float = 0.0
    _d_po2_pvr: float = 0.0
    _d_pco2_pvr: float = 0.0
    _d_ph_pvr: float = 0.0

    _d_map_mv: float = 0.0
    _d_po2_mv: float = 0.0
    _d_pco2_mv: float = 0.0
    _d_ph_mv: float = 0.0

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

        # calculatet the gains
        self.calc_gains()

        return self._is_initialized

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

            # calculate the activation functions
            self._a_map = activation_function(self._map, self.max_map, self.set_map, self.min_map)
            self._a_po2 = activation_function(self._po2, self.max_po2, self.set_po2, self.min_po2)
            self._a_pco2 = activation_function(self._pco2, self.max_pco2, self.set_pco2, self.min_pco2)
            self._a_ph = activation_function(self._ph, self.max_ph, self.set_ph, self.min_ph)

            # apply the time constants
            self._d_map_hr = self.time_constant(self.tc_map_hr, self._d_map_hr, self._a_map)
            self._d_pco2_hr = self.time_constant(self.tc_pco2_hr, self._d_pco2_hr, self._a_pco2)
            self._d_ph_hr = self.time_constant(self.tc_ph_hr, self._d_ph_hr, self._a_ph)
            self._d_po2_hr = self.time_constant(self.tc_po2_hr, self._d_po2_hr, self._a_po2)

            self._d_map_mv = self.time_constant(self.tc_map_mv, self._d_map_mv, self._a_map)
            self._d_pco2_mv = self.time_constant(self.tc_pco2_mv, self._d_pco2_mv, self._a_pco2)
            self._d_ph_mv = self.time_constant(self.tc_ph_mv, self._d_ph_mv, self._a_ph)
            self._d_po2_mv = self.time_constant(self.tc_po2_mv, self._d_po2_mv, self._a_po2)

            self._d_map_venpool = self.time_constant(self.tc_map_venpool, self._d_map_venpool, self._a_map)
            self._d_pco2_venpool = self.time_constant(self.tc_pco2_venpool, self._d_pco2_venpool, self._a_pco2)
            self._d_ph_venpool = self.time_constant(self.tc_ph_venpool, self._d_ph_venpool, self._a_ph)
            self._d_po2_venpool = self.time_constant(self.tc_po2_venpool, self._d_po2_venpool, self._a_po2)

            self._d_map_cont = self.time_constant(self.tc_map_cont, self._d_map_cont, self._a_map)
            self._d_pco2_cont = self.time_constant(self.tc_pco2_cont, self._d_pco2_cont, self._a_pco2)
            self._d_ph_cont = self.time_constant(self.tc_ph_cont, self._d_ph_cont, self._a_ph)
            self._d_po2_cont = self.time_constant(self.tc_po2_cont, self._d_po2_cont, self._a_po2)

            self._d_map_svr = self.time_constant(self.tc_map_svr, self._d_map_svr, self._a_map)
            self._d_pco2_svr = self.time_constant(self.tc_pco2_svr, self._d_pco2_svr, self._a_pco2)
            self._d_ph_svr = self.time_constant(self.tc_ph_svr, self._d_ph_svr, self._a_ph)
            self._d_po2_svr = self.time_constant(self.tc_po2_svr, self._d_po2_svr, self._a_po2)

            self._d_map_pvr = self.time_constant(self.tc_map_pvr, self._d_map_pvr, self._a_map)
            self._d_pco2_pvr = self.time_constant(self.tc_pco2_pvr, self._d_pco2_pvr, self._a_pco2)
            self._d_ph_pvr = self.time_constant(self.tc_ph_pvr, self._d_ph_pvr, self._a_ph)
            self._d_po2_pvr = self.time_constant(self.tc_po2_pvr, self._d_po2_pvr, self._a_po2)

            # apply the effects if enabled
            if self.hr_effects_enabled:
                self.calc_hr_effects()
            if self.mv_effects_enabled:
                self.calc_mv_effects()
            if self.venpool_effects_enabled:
                self.calc_venpool_effects()
            if self.cont_effects_enabled:
                self.calc_cont_effects()
            if self.svr_effects_enabled:
                self.calc_svr_effects()
            if self.pvr_effects_enabled:
                self.calc_pvr_effects()

            # reset the update counter
            self._update_counter = 0.0

        self._update_counter += self._t



    def calc_hr_effects(self):
        # reset the cumulative hr factor
        cum_hr_factor: float = 0.0

        # mean arterial pressure influence on hr
        if self._d_map_hr > 0:
            cum_hr_factor = self.g_map_high_hr * self._d_map_hr
        else:
            cum_hr_factor = self.g_map_low_hr * self._d_map_hr

        # pco2 influence on hr
        if self._d_pco2_hr > 0:
            cum_hr_factor += self.g_pco2_high_hr * self._d_pco2_hr
        else:
            cum_hr_factor += self.g_pco2_low_hr * self._d_pco2_hr
        
        # ph influence on hr
        if self._d_ph_hr > 0:
            cum_hr_factor += self.g_ph_high_hr * self._d_ph_hr
        else:
            cum_hr_factor += self.g_ph_low_hr * self._d_ph_hr

        # po2 influence on hr
        if self._d_po2_hr > 0:
            cum_hr_factor += self.g_po2_high_hr * self._d_po2_hr
        else:
            cum_hr_factor += self.g_po2_low_hr * self._d_po2_hr

        # calculate the new heartrate factor
        self.hr_factor = self.calc_factor(cum_hr_factor)

        # gueard the minimum and maximum factor values
        if self.hr_factor > self.hr_factor_max:
            self.hr_factor = self.hr_factor_max
        if self.hr_factor < self.hr_factor_min:
            self.hr_factor = self.hr_factor_min

        # apply the effect
        for hr_target in self._hr_targets:
            hr_target.hr_ans_factor = self.hr_factor
        
    def calc_mv_effects(self):
        # reset the cumulative mv factor
        cum_mv_factor: float = 0.0

        # mean arterial pressure influence on mv
        if self._d_map_mv > 0:
            cum_mv_factor = self.g_map_high_mv * self._d_map_mv
        else:
            cum_mv_factor = self.g_map_low_mv * self._d_map_mv

        # pco2 influence on mv
        if self._d_pco2_mv > 0:
            cum_mv_factor += self.g_pco2_high_mv * self._d_pco2_mv
        else:
            cum_mv_factor += self.g_pco2_low_mv * self._d_pco2_mv
        
        # ph influence on mv
        if self._d_ph_mv > 0:
            cum_mv_factor += self.g_ph_high_mv * self._d_ph_mv
        else:
            cum_mv_factor += self.g_ph_low_mv * self._d_ph_mv

        # po2 influence on mv
        if self._d_po2_mv > 0:
            cum_mv_factor += self.g_po2_high_mv * self._d_po2_mv
        else:
            cum_mv_factor += self.g_po2_low_mv * self._d_po2_mv

        # calculate the new heartrate factor
        self.mv_factor = self.calc_factor(cum_mv_factor)

        # gueard the minimum and maximum factor values
        if self.mv_factor > self.mv_factor_max:
            self.mv_factor = self.mv_factor_max
        if self.mv_factor < self.mv_factor_min:
            self.mv_factor = self.mv_factor_min

        # apply the effect
        for mv_target in self._mv_targets:
            mv_target.mv_ans_factor = self.mv_factor
        
    def calc_cont_effects(self):
        # reset the cumulative cont factor
        cum_cont_factor: float = 0.0

        # mean arterial pressure influence on cont
        if self._d_map_cont > 0:
            cum_cont_factor = self.g_map_high_cont * self._d_map_cont
        else:
            cum_cont_factor = self.g_map_low_cont * self._d_map_cont

        # pco2 influence on cont
        if self._d_pco2_cont > 0:
            cum_cont_factor += self.g_pco2_high_cont * self._d_pco2_cont
        else:
            cum_cont_factor += self.g_pco2_low_cont * self._d_pco2_cont
        
        # ph influence on cont
        if self._d_ph_cont > 0:
            cum_cont_factor += self.g_ph_high_cont * self._d_ph_cont
        else:
            cum_cont_factor += self.g_ph_low_cont * self._d_ph_cont

        # po2 influence on cont
        if self._d_po2_cont > 0:
            cum_cont_factor += self.g_po2_high_cont * self._d_po2_cont
        else:
            cum_cont_factor += self.g_po2_low_cont * self._d_po2_cont

        # calculate the new heartrate factor
        self.cont_factor = self.calc_factor(cum_cont_factor)

        # gueard the minimum and maximum factor values
        if self.cont_factor > self.cont_factor_max:
            self.cont_factor = self.cont_factor_max
        if self.cont_factor < self.cont_factor_min:
            self.cont_factor = self.cont_factor_min

        # calculate the new heart_rate
        new_cont: float  = self.cont_factor * self.cont_ref

        # apply the effect
        for cont_target in self._cont_targets:
            cont_target.el_max_factor = new_cont

    def calc_venpool_effects(self):
        # reset the cumulative venpool factor
        cum_venpool_factor: float = 0.0

        # mean arterial pressure influence on venpool
        if self._d_map_venpool > 0:
            cum_venpool_factor = self.g_map_high_venpool * self._d_map_venpool
        else:
            cum_venpool_factor = self.g_map_low_venpool * self._d_map_venpool

        # pco2 influence on venpool
        if self._d_pco2_venpool > 0:
            cum_venpool_factor += self.g_pco2_high_venpool * self._d_pco2_venpool
        else:
            cum_venpool_factor += self.g_pco2_low_venpool * self._d_pco2_venpool
        
        # ph influence on venpool
        if self._d_ph_venpool > 0:
            cum_venpool_factor += self.g_ph_high_venpool * self._d_ph_venpool
        else:
            cum_venpool_factor += self.g_ph_low_venpool * self._d_ph_venpool

        # po2 influence on venpool
        if self._d_po2_venpool > 0:
            cum_venpool_factor += self.g_po2_high_venpool * self._d_po2_venpool
        else:
            cum_venpool_factor += self.g_po2_low_venpool * self._d_po2_venpool

        # calculate the new heartrate factor
        self.venpool_factor = self.calc_factor(cum_venpool_factor)

        # gueard the minimum and maximum factor values
        if self.venpool_factor > self.venpool_factor_max:
            self.venpool_factor = self.venpool_factor_max
        if self.venpool_factor < self.venpool_factor_min:
            self.venpool_factor = self.venpool_factor_min

        # calculate the new heart_rate
        new_venpool: float  = self.venpool_factor * self.venpool_ref

        # apply the effect
        for venpool_target in self._venpool_targets:
            venpool_target.u_vol_factor = new_venpool

    def calc_svr_effects(self):
        # reset the cumulative svr factor
        cum_svr_factor: float = 0.0

        # mean arterial pressure influence on svr
        if self._d_map_svr > 0:
            cum_svr_factor = self.g_map_high_svr * self._d_map_svr
        else:
            cum_svr_factor = self.g_map_low_svr * self._d_map_svr

        # pco2 influence on svr
        if self._d_pco2_svr > 0:
            cum_svr_factor += self.g_pco2_high_svr * self._d_pco2_svr
        else:
            cum_svr_factor += self.g_pco2_low_svr * self._d_pco2_svr
        
        # ph influence on svr
        if self._d_ph_svr > 0:
            cum_svr_factor += self.g_ph_high_svr * self._d_ph_svr
        else:
            cum_svr_factor += self.g_ph_low_svr * self._d_ph_svr

        # po2 influence on svr
        if self._d_po2_svr > 0:
            cum_svr_factor += self.g_po2_high_svr * self._d_po2_svr
        else:
            cum_svr_factor += self.g_po2_low_svr * self._d_po2_svr

        # calculate the new heartrate factor
        self.svr_factor = self.calc_factor(cum_svr_factor)

        # gueard the minimum and maximum factor values
        if self.svr_factor > self.svr_factor_max:
            self.svr_factor = self.svr_factor_max
        if self.svr_factor < self.svr_factor_min:
            self.svr_factor = self.svr_factor_min

        # calculate the new heart_rate
        new_svr: float  = self.svr_factor * self.svr_ref

        # apply the effect
        for svr_target in self._svr_targets:
            svr_target.r_ans_factor = new_svr

    def calc_pvr_effects(self):
        # reset the cumulative pvr factor
        cum_pvr_factor: float = 0.0

        # mean arterial pressure influence on pvr
        if self._d_map_pvr > 0:
            cum_pvr_factor = self.g_map_high_pvr * self._d_map_pvr
        else:
            cum_pvr_factor = self.g_map_low_pvr * self._d_map_pvr

        # pco2 influence on pvr
        if self._d_pco2_pvr > 0:
            cum_pvr_factor += self.g_pco2_high_pvr * self._d_pco2_pvr
        else:
            cum_pvr_factor += self.g_pco2_low_pvr * self._d_pco2_pvr
        
        # ph influence on pvr
        if self._d_ph_pvr > 0:
            cum_pvr_factor += self.g_ph_high_pvr * self._d_ph_pvr
        else:
            cum_pvr_factor += self.g_ph_low_pvr * self._d_ph_pvr

        # po2 influence on pvr
        if self._d_po2_pvr > 0:
            cum_pvr_factor += self.g_po2_high_pvr * self._d_po2_pvr
        else:
            cum_pvr_factor += self.g_po2_low_pvr * self._d_po2_pvr

        # calculate the new heartrate factor
        self.pvr_factor = self.calc_factor(cum_pvr_factor)

        # gueard the minimum and maximum factor values
        if self.pvr_factor > self.pvr_factor_max:
            self.pvr_factor = self.pvr_factor_max
        if self.pvr_factor < self.pvr_factor_min:
            self.pvr_factor = self.pvr_factor_min

        # calculate the new heart_rate
        new_pvr: float  = self.pvr_factor * self.pvr_ref

        # apply the effect
        for pvr_target in self._pvr_targets:
            pvr_target.r_ans_factor = new_pvr

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

    def calc_gains(self):
        # heart rate gains
        self.g_map_low_hr = self.translate_mxe(self.mxe_map_low_hr) / (self.min_map - self.set_map)
        self.g_map_high_hr = self.translate_mxe(self.mxe_map_high_hr) / (self.max_map - self.set_map)

        self.g_pco2_low_hr = self.translate_mxe(self.mxe_pco2_low_hr) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high_hr = self.translate_mxe(self.mxe_pco2_high_hr) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low_hr = self.translate_mxe(self.mxe_ph_low_hr) / (self.min_ph - self.set_ph)
        self.g_ph_high_hr = self.translate_mxe(self.mxe_ph_high_hr) / (self.max_ph - self.set_ph)

        self.g_po2_low_hr = self.translate_mxe(self.mxe_po2_low_hr) / (self.min_po2 - self.set_po2)
        self.g_po2_high_hr = self.translate_mxe(self.mxe_po2_high_hr) / (self.max_po2 - self.set_po2)

        # minute volume gains
        self.g_map_low_mv = self.translate_mxe(self.mxe_map_low_mv) / (self.min_map - self.set_map)
        self.g_map_high_mv = self.translate_mxe(self.mxe_map_high_mv) / (self.max_map - self.set_map)

        self.g_pco2_low_mv = self.translate_mxe(self.mxe_pco2_low_mv) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high_mv = self.translate_mxe(self.mxe_pco2_high_mv) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low_mv = self.translate_mxe(self.mxe_ph_low_mv) / (self.min_ph - self.set_ph)
        self.g_ph_high_mv = self.translate_mxe(self.mxe_ph_high_mv) / (self.max_ph - self.set_ph)

        self.g_po2_low_mv = self.translate_mxe(self.mxe_po2_low_mv) / (self.min_po2 - self.set_po2)
        self.g_po2_high_mv = self.translate_mxe(self.mxe_po2_high_mv) / (self.max_po2 - self.set_po2)

        # venpool gains
        self.g_map_low_venpool = self.translate_mxe(self.mxe_map_low_venpool) / (self.min_map - self.set_map)
        self.g_map_high_venpool = self.translate_mxe(self.mxe_map_high_venpool) / (self.max_map - self.set_map)

        self.g_pco2_low_venpool = self.translate_mxe(self.mxe_pco2_low_venpool) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high_venpool = self.translate_mxe(self.mxe_pco2_high_venpool) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low_venpool = self.translate_mxe(self.mxe_ph_low_venpool) / (self.min_ph - self.set_ph)
        self.g_ph_high_venpool = self.translate_mxe(self.mxe_ph_high_venpool) / (self.max_ph - self.set_ph)

        self.g_po2_low_venpool = self.translate_mxe(self.mxe_po2_low_venpool) / (self.min_po2 - self.set_po2)
        self.g_po2_high_venpool = self.translate_mxe(self.mxe_po2_high_venpool) / (self.max_po2 - self.set_po2)

        # cont gains
        self.g_map_low_cont = self.translate_mxe(self.mxe_map_low_cont) / (self.min_map - self.set_map)
        self.g_map_high_cont = self.translate_mxe(self.mxe_map_high_cont) / (self.max_map - self.set_map)

        self.g_pco2_low_cont = self.translate_mxe(self.mxe_pco2_low_cont) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high_cont = self.translate_mxe(self.mxe_pco2_high_cont) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low_cont = self.translate_mxe(self.mxe_ph_low_cont) / (self.min_ph - self.set_ph)
        self.g_ph_high_cont = self.translate_mxe(self.mxe_ph_high_cont) / (self.max_ph - self.set_ph)

        self.g_po2_low_cont = self.translate_mxe(self.mxe_po2_low_cont) / (self.min_po2 - self.set_po2)
        self.g_po2_high_cont = self.translate_mxe(self.mxe_po2_high_cont) / (self.max_po2 - self.set_po2)

        # svr gains
        self.g_map_low_svr = self.translate_mxe(self.mxe_map_low_svr) / (self.min_map - self.set_map)
        self.g_map_high_svr = self.translate_mxe(self.mxe_map_high_svr) / (self.max_map - self.set_map)

        self.g_pco2_low_svr = self.translate_mxe(self.mxe_pco2_low_svr) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high_svr = self.translate_mxe(self.mxe_pco2_high_svr) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low_svr = self.translate_mxe(self.mxe_ph_low_svr) / (self.min_ph - self.set_ph)
        self.g_ph_high_svr = self.translate_mxe(self.mxe_ph_high_svr) / (self.max_ph - self.set_ph)

        self.g_po2_low_svr = self.translate_mxe(self.mxe_po2_low_svr) / (self.min_po2 - self.set_po2)
        self.g_po2_high_svr = self.translate_mxe(self.mxe_po2_high_svr) / (self.max_po2 - self.set_po2)
        
        # pvr gains
        self.g_map_low_pvr = self.translate_mxe(self.mxe_map_low_pvr) / (self.min_map - self.set_map)
        self.g_map_high_pvr = self.translate_mxe(self.mxe_map_high_pvr) / (self.max_map - self.set_map)

        self.g_pco2_low_pvr = self.translate_mxe(self.mxe_pco2_low_pvr) / (self.min_pco2 - self.set_pco2)
        self.g_pco2_high_pvr = self.translate_mxe(self.mxe_pco2_high_pvr) / (self.max_pco2 - self.set_pco2)

        self.g_ph_low_pvr = self.translate_mxe(self.mxe_ph_low_pvr) / (self.min_ph - self.set_ph)
        self.g_ph_high_pvr = self.translate_mxe(self.mxe_ph_high_pvr) / (self.max_ph - self.set_ph)

        self.g_po2_low_pvr = self.translate_mxe(self.mxe_po2_low_pvr) / (self.min_po2 - self.set_po2)
        self.g_po2_high_pvr = self.translate_mxe(self.mxe_po2_high_pvr) / (self.max_po2 - self.set_po2)

