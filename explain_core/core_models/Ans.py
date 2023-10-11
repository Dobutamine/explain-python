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
    # local variables
    _baroreceptor: BloodCapacitance = {}
    _chemoreceptor: BloodCapacitance = {}
    _heart: Heart = {}
    _venous_reservoirs: BloodCapacitance = []
    _heart_chambers: BloodTimeVaryingElastance = []
    _svr_targets: Resistor = []
    _pvr_targets: Resistor = []
    _breathing: Breathing = {}
    _a_map: float = 0.0
    _a_ph: float = 0.0
    _a_po2: float = 0.0
    _a_pco2: float = 0.0

    _d_map_hp: float = 0.0
    _d_po2_hp: float = 0.0
    _d_pco2_hp: float = 0.0
    _d_ph_hp: float = 0.0

    _d_map_ven_pool: float = 0.0
    _d_po2_ven_pool: float = 0.0
    _d_pco2_ven_pool: float = 0.0
    _d_ph_ven_pool: float = 0.0

    _d_map_cont: float = 0.0
    _d_po2_cont: float = 0.0
    _d_pco2_cont: float = 0.0
    _d_ph_cont: float = 0.0

    _d_map_svr: float = 0.0
    _d_po2_svr: float = 0.0
    _d_pco2_svr: float = 0.0
    _d_ph_svr: float = 0.0

    _d_po2_pvr: float = 0.0
    _d_pco2_pvr: float = 0.0
    _d_ph_pvr: float = 0.0

    _d_po2_ve: float = 0.0
    _d_pco2_ve: float = 0.0
    _d_ph_ve: float = 0.0
    _update_window: float = 0.015
    _update_counter: float = 0.0

    _venpool:float = 1.0
    _cont: float = 1.0
    _svr: float = 1.0
    _pvr: float = 1.0

    _pressures: float = []
    _data_window: int = 133

    def init_model(self, model: object) -> bool:
        # initialize the basemodel parent class
        super().init_model(model)

        # get a reference to the baroreceptor location, the heart and the breathing model
        self._baroreceptor = self._model.models[self.baroreceptor_location]
        self._chemoreceptor = self._model.models[self.chemoreceptor_location]
        self._heart = self._model.models['Heart']
        self._breathing = self._model.models['Breathing']

        for hc in self.heart_chambers:
            self._heart_chambers.append(self._model.models[hc])

        for venres in self.venous_reservoirs:
            self._venous_reservoirs.append(self._model.models[venres])

        for svrt in self.svr_targets:
            self._svr_targets.append(self._model.models[svrt])

        for pvrt in self.pvr_targets:
            self._pvr_targets.append(self._model.models[pvrt])

        # fill the list of pressures with the baroreflex start point
        self._pressures = [self.set_baro] * self._data_window

        return self._is_initialized

    def calc_model(self) -> None:

        if self._update_counter > self._update_window:
            # insert a new pressure at the start of the list
            self._pressures.insert(0, self._baroreceptor.pres)

            # remove the last pressure from the list
            self._pressures.pop()
            
            # get the moving average of the pressure
            _baro_pres: float = sum(self._pressures) / (self._data_window)

            # for the chemoreflex we need the acidbase and oxygenation of the location of the chemoreceptor
            set_blood_composition(self._chemoreceptor)

            # get the chemoreflex inputs
            _po2 = self._chemoreceptor.aboxy['po2']
            _pco2 = self._chemoreceptor.aboxy['pco2']
            _ph = self._chemoreceptor.aboxy['ph']

            # calculate the activation function of the baroreceptor
            self._a_map = activation_function(
                _baro_pres, self.max_baro, self.set_baro, self.min_baro)

            # calculate the activation functions of the chemoreceptors
            self._a_po2 = activation_function(
                _po2, self.max_po2, self.set_po2, self.min_po2)

            self._a_pco2 = activation_function(
                _pco2, self.max_pco2, self.set_pco2, self.min_pco2)

            self._a_ph = activation_function(
                _ph, self.max_ph, self.set_ph, self.min_ph)

            # calculate the effectors and use the time constant
            self._d_map_hp = self._update_window * \
                ((1 / self.tc_map_hp) * (-self._d_map_hp + self._a_map)) + self._d_map_hp

            self._d_po2_hp = self._update_window * \
                ((1 / self.tc_po2_hp) * (-self._d_po2_hp + self._a_po2)) + self._d_po2_hp

            self._d_pco2_hp = self._update_window * \
                ((1 / self.tc_pco2_hp) * (-self._d_pco2_hp + self._a_pco2)) + self._d_pco2_hp

            self._d_ph_hp = self._update_window * \
                ((1 / self.tc_ph_hp) * (-self._d_ph_hp + self._a_ph)) + self._d_ph_hp

            self._d_map_ven_pool = self._update_window * \
                ((1 / self.tc_map_ven_pool) * (-self._d_map_ven_pool + self._a_map)) + self._d_map_ven_pool

            self._d_po2_ven_pool = self._update_window * \
                ((1 / self.tc_po2_ven_pool) * (-self._d_po2_ven_pool + self._a_po2)) + self._d_po2_ven_pool

            self._d_pco2_ven_pool = self._update_window * \
                ((1 / self.tc_pco2_ven_pool) * (-self._d_pco2_ven_pool + self._a_pco2)) + self._d_pco2_ven_pool

            self._d_ph_ven_pool = self._update_window * \
                ((1 / self.tc_ph_ven_pool) * (-self._d_ph_ven_pool + self._a_ph)) + self._d_ph_ven_pool

            self._d_map_cont = self._update_window * \
                ((1 / self.tc_map_cont) * (-self._d_map_cont + self._a_map)) + self._d_map_cont

            self._d_po2_cont = self._update_window * \
                ((1 / self.tc_po2_cont) * (-self._d_po2_cont + self._a_po2)) + self._d_po2_cont

            self._d_pco2_cont = self._update_window * \
                ((1 / self.tc_pco2_cont) * (-self._d_pco2_cont + self._a_pco2)) + self._d_pco2_cont

            self._d_ph_cont = self._update_window * \
                ((1 / self.tc_ph_cont) * (-self._d_ph_cont + self._a_ph)) + self._d_ph_cont

            self._d_map_svr = self._update_window * \
                ((1 / self.tc_map_svr) * (-self._d_map_svr + self._a_map)) + self._d_map_svr

            self._d_po2_svr = self._update_window * \
                ((1 / self.tc_po2_svr) * (-self._d_po2_svr + self._a_po2)) + self._d_po2_svr

            self._d_pco2_svr = self._update_window * \
                ((1 / self.tc_pco2_svr) * (-self._d_pco2_svr + self._a_pco2)) + self._d_pco2_svr

            self._d_ph_svr = self._update_window * \
                ((1 / self.tc_ph_svr) * (-self._d_ph_svr + self._a_ph)) + self._d_ph_svr

            self._d_po2_pvr = self._update_window * \
                ((1 / self.tc_po2_pvr) * (-self._d_po2_pvr + self._a_po2)) + self._d_po2_pvr

            self._d_pco2_pvr = self._update_window * \
                ((1 / self.tc_pco2_pvr) * (-self._d_pco2_pvr + self._a_pco2)) + self._d_pco2_pvr

            self._d_ph_pvr = self._update_window * \
                ((1 / self.tc_ph_pvr) * (-self._d_ph_pvr + self._a_ph)) + self._d_ph_pvr

            self._d_po2_ve = self._update_window * \
                ((1 / self.tc_po2_ve) * (-self._d_po2_ve + self._a_po2)) + self._d_po2_ve

            self._d_pco2_ve = self._update_window * \
                ((1 / self.tc_pco2_ve) * (-self._d_pco2_ve + self._a_pco2)) + self._d_pco2_ve

            self._d_ph_ve = self._update_window * \
                ((1 / self.tc_ph_ve) * (-self._d_ph_ve + self._a_ph)) + self._d_ph_ve

            # apply the effects using the gain
            
            self._heart.heart_rate = self.heart_rate_ref + self.g_map_hp * self._d_map_hp + self.g_po2_hp * \
                self._d_po2_hp + self.g_pco2_hp * self._d_pco2_hp + self.g_ph_hp * self._d_ph_hp

            target_mv = self.minute_volume_ref + self.g_po2_ve * self._d_po2_ve + \
                self.g_pco2_ve * self._d_pco2_ve + self.g_ph_ve * self._d_ph_ve
            if (target_mv < 0.01):
                target_mv = 0.01
            self._breathing.target_minute_volume = target_mv
            
            # cumulative effect on unstressed volume/stressed volume distribution of the venous reservoirs
            cum_ven_pool_change = self.g_map_ven_pool * self._d_map_ven_pool + self.g_po2_ven_pool * self._d_po2_ven_pool + self.g_pco2_ven_pool * self._d_pco2_ven_pool + self.g_ph_ven_pool * self._d_ph_ven_pool
            ven_pool = self.ven_pool_ref
            if cum_ven_pool_change > 0:
                ven_pool = self.ven_pool_ref + cum_ven_pool_change      
            if cum_ven_pool_change < 0:
                ven_pool = self.ven_pool_ref - cum_ven_pool_change
                ven_pool = 1.0 / ven_pool
            if ven_pool > 0:
                self._venpool = ven_pool
                for r in self._venous_reservoirs:
                    r.u_vol_factor = ven_pool

            
            # cumulative effect on the heart contractility
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

            cum_pvr_change = self.g_po2_pvr * self._d_po2_pvr + self.g_pco2_pvr * self._d_pco2_pvr + self.g_ph_pvr * self._d_ph_pvr
            pvr = self.pvr_ref
            if cum_pvr_change > 0:
                pvr = self.pvr_ref + cum_pvr_change
            if cum_pvr_change < 0:
                pvr = self.pvr_ref = cum_pvr_change
                pvr = 1.0 / pvr
            if pvr > 0:
                self._pvr = pvr
                for pvr_target in self._pvr_targets:
                    pvr_target.r_ans_factor = pvr
            
            # reset the update counter
            self._update_counter = 0.0

        self._update_counter += self._t


