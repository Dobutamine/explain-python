import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.Heart import Heart
from explain_core.core_models.Breathing import Breathing
from explain_core.functions.ActivationFunction import activation_function
from explain_core.functions.Acidbase import calc_acidbase_from_tco2
from explain_core.functions.Oxygenation import calc_oxygenation_from_to2


class Ans(BaseModel):
    # local variables
    _baroreceptor: BloodCapacitance = {}
    _chemoreceptor: BloodCapacitance = {}
    _heart: Heart = {}
    _breathing: Breathing = {}
    _a_map: float = 0.0
    _a_ph: float = 0.0
    _a_po2: float = 0.0
    _a_pco2: float = 0.0

    _d_map_hp: float = 0.0
    _d_po2_hp: float = 0.0
    _d_pco2_hp: float = 0.0
    _d_ph_hp: float = 0.0

    _d_po2_ve: float = 0.0
    _d_pco2_ve: float = 0.0
    _d_ph_ve: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the basemodel parent class
        super().init_model(model)

        # get a reference to the baroreceptor location, the heart and the breathing model
        self._baroreceptor = self._model.models[self.baroreceptor_location]
        self._chemoreceptor = self._model.models[self.chemoreceptor_location]
        self._heart = self._model.models['Heart']
        self._breathing = self._model.models['Breathing']

        return self._is_initialized

    def calc_model(self) -> None:
        # get the baroreflex input
        _baro_pres: float = self._baroreceptor.mean

        # for the chemoreflex we need the acidbase and oxygenation of the location of the chemoreceptor
        # calculate the po2 and pco2 in the blood compartments
        result = calc_acidbase_from_tco2(self._chemoreceptor)
        if result is not None:
            self._chemoreceptor.aboxy['ph'] = result['ph']
            self._chemoreceptor.aboxy['pco2'] = result['pco2']
            self._chemoreceptor.aboxy['hco3'] = result['hco3']
            self._chemoreceptor.aboxy['be'] = result['be']
            self._chemoreceptor.aboxy['sid_app'] = result['sid_app']

        result_oxy = calc_oxygenation_from_to2(self._chemoreceptor)
        if result_oxy is not None:
            self._chemoreceptor.aboxy['po2'] = result_oxy['po2']
            self._chemoreceptor.aboxy['so2'] = result_oxy['so2']

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
        self._d_map_hp = self._t * \
            ((1 / self.tc_map_hp) * (-self._d_map_hp + self._a_map)) + self._d_map_hp

        self._d_po2_hp = self._t * \
            ((1 / self.tc_po2_hp) * (-self._d_po2_hp + self._a_po2)) + self._d_po2_hp

        self._d_pco2_hp = self._t * \
            ((1 / self.tc_pco2_hp) * (-self._d_pco2_hp + self._a_pco2)) + self._d_pco2_hp

        self._d_ph_hp = self._t * \
            ((1 / self.tc_ph_hp) * (-self._d_ph_hp + self._a_ph)) + self._d_ph_hp

        self._d_po2_ve = self._t * \
            ((1 / self.tc_po2_ve) * (-self._d_po2_ve + self._a_po2)) + self._d_po2_ve

        self._d_pco2_ve = self._t * \
            ((1 / self.tc_pco2_ve) * (-self._d_pco2_ve + self._a_pco2)) + self._d_pco2_ve

        self._d_ph_ve = self._t * \
            ((1 / self.tc_ph_ve) * (-self._d_ph_ve + self._a_ph)) + self._d_ph_ve

        # apply the effects using the gain
        self._heart.heart_rate = self.heart_rate_ref + self.g_map_hp * self._d_map_hp + self.g_po2_hp * \
            self._d_po2_hp + self.g_pco2_hp * self._d_pco2_hp + self.g_ph_hp * self._d_ph_hp

        target_mv = self.minute_volume_ref + self.g_po2_ve * self._d_po2_ve + \
            self.g_pco2_ve * self._d_pco2_ve + self.g_ph_ve * self._d_ph_ve
        if (target_mv < 0.01):
            target_mv = 0.01

        self._breathing.target_minute_volume = target_mv
