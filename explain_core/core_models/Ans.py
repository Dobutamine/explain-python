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

    hr_ref: float = 140.0
    hr_ref_max: float = 210.0
    hr_ref_min: float = 60.0
    mv_ref: float = 0.66
    venpool_ref: float = 1.0
    cont_ref: float = 1.0
    svr_ref: float = 1.0
    pvr_ref: float = 1.0

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
    mv_effects_enabled: bool = False
    venpool_effects_enabled: bool = False
    cont_effects_enabled: bool = False
    svr_effects_enabled: bool = False
    pvr_effects_enabled: bool = False

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

    _hr_factor: float = 1.0
    _hr_factor_hi: float = 1.0
    _hr_factor_lo: float = 1.0
    _venpool:float = 1.0
    _cont: float = 1.0
    _svr: float = 1.0
    _pvr: float = 1.0

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

    def calc_effect(self, d, g_high, g_low, v_ref, nv_min, nv_max) -> float:
        # reset the cumulative hr factor
        factor: float = 1.0
        cum_factor: float = 0.0

        # apply the appropriate gain depending whether map is above or under the threshold
        if d > 0:
            cum_factor = g_high * d
        else:
            cum_factor = g_low * d
        
        #   calculate the hr_factor which determines the heartrate 
        if cum_factor > 0:
            factor = 1.0 + cum_factor
        if cum_factor < 0:
            factor = 1.0 - cum_factor
            factor = 1.0 / factor
        
        # if the factor is within the limits then apply the effect
        nv: float  = factor * v_ref
        if nv > nv_max:
            nv = nv_max

        if nv < nv_min:
            nv = nv_min

        return nv

    def calc_hr_effects(self):
        new_hr = self.calc_effect(self._d_map_hr, self.g_map_high_hr, self.g_map_low_hr, self.hr_ref, self.hr_ref_min, self.hr_ref_max)

        # # reset the cumulative hr factor
        # cum_hr_factor: float = 0.0

        # # apply the appropriate gain depending whether map is above or under the threshold
        # if self._d_map_hr > 0:
        #     cum_hr_factor = self.g_map_high_hr * self._d_map_hr
        # else:
        #     cum_hr_factor = self.g_map_low_hr * self._d_map_hr
        
        # #   calculate the hr_factor which determines the heartrate 
        # if cum_hr_factor > 0:
        #     self._hr_factor = 1.0 + cum_hr_factor
        # if cum_hr_factor < 0:
        #     self._hr_factor = 1.0 - cum_hr_factor
        #     self._hr_factor = 1.0 / self._hr_factor
        
        # # if the factor is within the limits then apply the effect
        # new_hr = self._hr_factor * self.hr_ref
        # if new_hr > self.hr_ref_max:
        #     new_hr = self.hr_ref_max

        # if new_hr < self.hr_ref_min:
        #     new_hr = self.hr_ref_min

        # apply the effect
        for hr_target in self.hr_targets:
            hr.heart_rate = new_hr
        

    def calc_mv_effects(self):
        pass

    def calc_cont_effects(self):
        pass

    def calc_venpool_effects(self):
        pass

    def calc_svr_effects(self):
        pass

    def calc_pvr_effects(self):
        pass

    def time_constant(self, tc, cv, nv, t = 0.015):
        return t * (( 1.0 / tc) * (-cv + nv)) + cv


    def apply_effects(self):
            # hr - cumulative effect on the heart rate
            self._heart.heart_rate = self.heart_rate_ref + self.g_map_hp * self._d_map_hr + self.g_po2_hp * \
                self._d_po2_hr + self.g_pco2_hp * self._d_pco2_hr + self.g_ph_hp * self._d_ph_hr

            # mv - cumulative ffect on the minute volume
            target_mv = self.minute_volume_ref + self.g_po2_ve * self._d_po2_mv + \
                self.g_pco2_ve * self._d_pco2_mv + self.g_ph_ve * self._d_ph_mv
            if (target_mv < 0.01):
                target_mv = 0.01
            self._breathing.target_minute_volume = target_mv
            
            # venpool - cumulative effect on unstressed volume/stressed volume distribution of the venous reservoirs
            cum_venpool_change = self.g_map_venpool * self._d_map_venpool + self.g_po2_venpool * self._d_po2_venpool + self.g_pco2_venpool * self._d_pco2_venpool + self.g_ph_venpool * self._d_ph_venpool
            venpool = self.venpool_ref
            if cum_venpool_change > 0:
                venpool = self.venpool_ref + cum_venpool_change      
            if cum_venpool_change < 0:
                venpool = self.venpool_ref - cum_venpool_change
                venpool = 1.0 / venpool
            if venpool > 0:
                self._venpool = venpool
                for r in self._venous_reservoirs:
                    r.u_vol_factor = venpool

            
            # cont - cumulative effect on the heart contractility
            cum_cont_change = self.g_map_cont * self._d_map_cont + self.g_po2_cont * self._d_po2_cont + self.g_pco2_cont * self._d_pco2_cont + self.g_ph_cont * self._d_ph_cont
            cont = self.cont_ref
            if cum_cont_change > 0:
                cont = self.cont_ref + cum_cont_change
            if cum_cont_change < 0:
                cont = self.cont_ref - cum_cont_change
                cont = 1.0 / cont
            if cont > 0:
                self._cont = cont
                for hc in self._heart_chambers:
                    hc.el_max_ans_factor = cont

            # svr - cumulative effect on the systemic vascular resistance
            cum_svr_change = self.g_map_svr * self._d_map_svr + self.g_po2_svr * self._d_po2_svr + self.g_pco2_svr * self._d_pco2_svr + self.g_ph_svr * self._d_ph_svr
            svr = self.svr_ref
            if cum_svr_change > 0:
                svr = self.svr_ref + cum_svr_change
            if cum_svr_change < 0:
                svr = self.svr_ref - cum_svr_change
                svr = 1.0 / svr  
            if svr > 0:
                self._svr = svr
                for svr_target in self._svr_targets:
                    svr_target.r_ans_factor = svr

            # pvr - cumulative effect on the pulmonary vascular resistance
            cum_pvr_change = self.g_po2_pvr * self._d_po2_pvr + self.g_pco2_pvr * self._d_pco2_pvr + self.g_ph_pvr * self._d_ph_pvr
            pvr = self.pvr_ref
            if cum_pvr_change > 0:
                pvr = self.pvr_ref + cum_pvr_change
            if cum_pvr_change < 0:
                pvr = self.pvr_ref - cum_pvr_change
                pvr = 1.0 / pvr
            if pvr > 0:
                self._pvr = pvr
                for pvr_target in self._pvr_targets:
                    pvr_target.r_ans_factor = pvr

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
        self.g_map_low_hr = self.translate_mxe(self.mxe_map_low_hr) / (self.min_map - self.set_map)
        self.g_map_high_hr = self.translate_mxe(self.mxe_map_high_hr) / (self.max_map - self.set_map)
        

