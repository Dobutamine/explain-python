import math

from explain_core.helpers.BloodComposition import set_blood_composition


class Mob:
    # static properties
    model_type: str = "Mob"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.mob_active = True
        self.heart_model = "Heart"
        self.aa_model = "AA"
        self.aa_cor_model = "AA_COR"
        self.cor_model = "COR"
        self.mob_active = True
        self.heart_model = "Heart"
        self.aa_model = "AA"
        self.aa_cor_model = "AA_COR"
        self.cor_model = "COR"
        self.ecc_c = 0.00000301
        self.ecc_c_factor = 1
        self.pva_c = 0.00143245
        self.pva_c_factor = 1
        self.pe_c = 0
        self.pe_c_factor = 1
        self.to2_min = 0.0002
        self.to2_set = 0.2
        self.to2_max = 0.2
        self.bm_vo2_ref = 0.0007
        self.bm_vo2_max = 0.0007
        self.bm_vo2_min = 0.00035
        self.bm_vo2_factor = 1
        self.bm_vo2_tc = 5
        self.resp_q = 0.1
        self.hr_factor = 1
        self.hr_factor_max = 1
        self.hr_factor_min = 0.01
        self.hr_tc = 5
        self.cont_factor = 1
        self.cont_factor_max = 1
        self.cont_factor_min = 0.01
        self.cont_tc = 5
        self.ans_factor = 1
        self.ans_factor_max = 1
        self.ans_factor_min = 0.01
        self.ans_tc = 5
        self.ans_activity_factor = 1

        # dependent properties
        self.mob = 0.0
        self.mvo2 = 0.0
        self.mvo2_step = 0.0
        self.bm = 0.0
        self.bm_vo2 = 0.0
        self.ecc_vo2 = 0.0
        self.pva_vo2 = 0.0
        self.pe_vo2 = 0.0
        self.bm_g = 2.0
        self.cont_g = 0.0
        self.hr_g = 0.0
        self.ans_g = 0.0

        self.ecc_lv = 0.0
        # pres_ms of the heart chamber
        self.ecc_rv = 0.0
        self.ecc = 0.0
        # excitation contraction coupling
        self.pva = 0.0
        # total pva of both ventricles
        self.pe = 0.0
        # potenital mechanical work stored in the ventricular wall
        self.stroke_work_lv = 0.0
        # stroke work of left ventricle
        self.stroke_work_rv = 0.0
        # stroke work of right ventricle
        self.stroke_volume_lv = 0.0
        # stroke volume in liters
        self.stroke_volume_rv = 0.0
        # stroke volume in liters
        self.sv_lv_kg = 0.0
        self.sv_rv_kg = 0.0
        self.cor_po2 = 0.0
        self.cor_pco2 = 0.0
        self.cor_so2 = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._heart = {}
        self._aa = {}
        self._aa_cor = {}
        self._cor = {}

        self._prev_lv_vol = 0.0
        self._prev_lv_pres = 0.0
        self._prev_rv_vol = 0.0
        self._prev_rv_pres = 0.0

        self._pv_area_lv = 0.0
        self._pv_area_rv = 0.0
        self._pv_area_lv_inc = 0.0
        self._pv_area_rv_inc = 0.0
        self._pv_area_lv_dec = 0.0
        self._pv_area_rv_dec = 0.0

        self._sv_lv_cum = 0.0
        self._sv_rv_cum = 0.0

        self._a_to2 = 0.0
        self._d_bm_vo2 = 0.0
        self._d_cont = 0.0
        self._d_hr = 0.0
        self._d_ans = 0.0
        self._ml_to_mmol = 22.414

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the heart
        self._heart = self._model_engine.models[self.heart_model]
        self._aa = self._model_engine.models[self.aa_model]
        self._aa_cor = self._model_engine.models[self.aa_cor_model]
        self._cor = self._model_engine.models[self.cor_model]

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized and self.mob_active:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # set the heart weight -> at 3.545 that is about 23 grams
        self.hw = 7.799 + 0.004296 * self._model_engine.weight * 1000.0

        # get the necessary model properties from the coronaries
        to2_cor = self._cor.aboxy["to2"]
        tco2_cor = self._cor.aboxy["tco2"]
        vol_cor = self._cor.vol

        # calculate the activation function of the baseline vo2, which is zero when the to2 is above to2 setpoint
        # as the max is the same as the setpoint the activation function is zero when the to2 is above the setpoint
        self.to2_max = self.to2_set
        self._a_to2 = self.activation_function(
            to2_cor, self.to2_max, self.to2_set, self.to2_min
        )

        # calculate the basal metabolism in mmol O2 / sec is dependent on the to2 in the coronary blood
        self.bm_vo2 = self.calc_bm(self._a_to2)

        # calculate the energy cost of the excitation-contraction coupling in mmol O2 / cardiac cycle
        self.ecc_vo2 = self.calc_ecc(self._a_to2)

        # calculate the pressure volume loop area which is the total stroke work and convert it to mmol O2 / cardiac cycle
        self.pva_vo2 = self.calc_pva(self._a_to2)

        # calculate the potentential mechanical work stored in the ventricular wall and convert it to mmol O2 / cardiac cycle
        self.pe_vo2 = self.calc_pe(self._a_to2)

        # so the basal metabolism is always running but the pe, ecc and pva are only calculated relevant during a cardiac cycle
        bm_vo2_step = self.bm_vo2 * self._t

        # the ecc_vo2, pva_vo2 are only running during a cardiac cycle which is stored in the heart object cardiac_cycle_time variable
        ecc_vo2_step = 0.0
        pva_vo2_step = 0.0
        pe_vo2_step = 0.0

        if self._heart.cardiac_cycle_time > 0.0 and self._heart.cardiac_cycle_running:
            ecc_vo2_step = (self.ecc_vo2 / self._heart.cardiac_cycle_time) * self._t
            pva_vo2_step = (self.pva_vo2 / self._heart.cardiac_cycle_time) * self._t
            pe_vo2_step = (self.pe_vo2 / self._heart.cardiac_cycle_time) * self._t

        # calculate the total vo2 in mmol O2 for the model step
        self.mvo2_step = bm_vo2_step + ecc_vo2_step + pva_vo2_step + pe_vo2_step

        # calculate the co2 production in this model step
        co2_production = self.mvo2_step * self.resp_q

        # calculate the myocardial oxygen balance in mmol/s
        o2_inflow = self._aa_cor.flow * self._aa.aboxy["to2"]
        # in mmol/s
        o2_use = self.mvo2_step / self._t
        # in mmol/s
        self.mob = o2_inflow - o2_use + to2_cor

        # calculate the new blood composition of the coronary blood
        if vol_cor > 0:
            new_to2_cor = (to2_cor * vol_cor - self.mvo2_step) / vol_cor
            new_tco2_cor = (tco2_cor * vol_cor + co2_production) / vol_cor
            if new_to2_cor >= 0:
                self._cor.aboxy["to2"] = new_to2_cor
                self._cor.aboxy["tco2"] = new_tco2_cor

        # store the blood composition of the coronary blood
        self.cor_po2 = self._cor.aboxy["po2"]
        self.cor_pco2 = self._cor.aboxy["pco2"]
        self.cor_so2 = self._cor.aboxy["so2"]

        # calculate the effects on the heartrate, contractility and autonomic nervous system
        self.calc_effectors(self._a_to2)

    def calc_bm(self, act):
        # calculate the gain depending on the reference and minimal baseline vo2 and po2 threshold from where the baseline vo2 is reduced
        # this gain determines how much the baseline vo2 is reduced when the po2 drops below the threshold
        self.bm_g = (
            self.bm_vo2_max * self.bm_vo2_factor * self.hw
            - self.bm_vo2_min * self.bm_vo2_factor * self.hw
        ) / (self.to2_max - self.to2_min)

        # incorporate the time constants
        self._d_bm_vo2 = (
            self._t * ((1 / self.bm_vo2_tc) * (-self._d_bm_vo2 + act)) + self._d_bm_vo2
        )

        # calculate the baseline vo2 in mmol O2 /  cardiac cycle
        bm_vo2 = (
            self.bm_vo2_ref * self.bm_vo2_factor * self.hw + self._d_bm_vo2 * self.bm_g
        ) / self._ml_to_mmol
        # is about 20% in steady state

        if bm_vo2 < (self.bm_vo2_min * self.bm_vo2_factor * self.hw) / self._ml_to_mmol:
            bm_vo2 = (self.bm_vo2_min * self.bm_vo2_factor * self.hw) / self._ml_to_mmol

        return bm_vo2

    def calc_ecc(self, act):
        # calculate the excitation contraction coupling in mmol O2 / cardiac cycle relates to the costs of ion transport and calcium cycling
        self.ecc_lv = self._heart._lv.el_max * self._heart._lv.el_max_factor
        self.ecc_rv = self._heart._rv.el_max * self._heart._rv.el_max_factor
        self.ecc = (self.ecc_lv + self.ecc_rv) / 1000.0

        return (self.ecc * self.ecc_c * self.ecc_c_factor * self.hw) / self._ml_to_mmol
        # is about 15% in steady state;

    def calc_pe(self, act):
        # calculate the potential mechanical work stored in the ventricular wall in mmol O2 / cardiac cycle which does not have a direct metabolic cost but is stored energy
        self.pe = 0

        return (self.pe * self.pe_c * self.pe_c_factor * self.hw) / self._ml_to_mmol

    def calc_pva(self, act):
        # detect the start of the cardiac cycle and calculate the area of the pv loop of the last cardiac cycle
        if (
            self._heart.cardiac_cycle_running
            and not self._heart.prev_cardiac_cycle_running
        ):
            # calculate the composition the coronary blood
            set_blood_composition(self._cor)

            # calculate the stroke work of the ventricles
            self.stroke_work_lv = self._pv_area_lv_dec - self._pv_area_lv_inc
            # in l * mmHg/cardiac cycle
            self.stroke_work_rv = self._pv_area_rv_dec - self._pv_area_rv_inc
            # in l * mmHg/cardiac cycle

            # calculate the stroke volume of the ventricles
            self.stroke_volume_lv = self._sv_lv_cum
            # in l/cardiac cycle
            self.stroke_volume_rv = self._sv_rv_cum
            # in l/cardiac cycle
            self.sv_lv_kg = (self.stroke_volume_lv * 1000.0) / self._model_engine.weight
            self.sv_rv_kg = (self.stroke_volume_rv * 1000.0) / self._model_engine.weight

            # reset the counters
            self._pv_area_lv_inc = 0.0
            self._pv_area_rv_inc = 0.0
            self._pv_area_lv_dec = 0.0
            self._pv_area_rv_dec = 0.0
            self._sv_lv_cum = 0.0
            self._sv_rv_cum = 0.0

        # calculate the pv area of this model step
        _dV_lv = self._heart._lv.vol - self._prev_lv_vol
        # if the volume is increasing count the stroke volume
        if _dV_lv > 0:
            self._sv_lv_cum += _dV_lv
            self._pv_area_lv_inc += (
                _dV_lv * self._prev_lv_pres
                + (_dV_lv * (self._heart._lv.pres - self._prev_lv_pres)) / 2.0
            )
        else:
            self._pv_area_lv_dec += (
                -_dV_lv * self._prev_lv_pres
                + (-_dV_lv * (self._heart._lv.pres - self._prev_lv_pres)) / 2.0
            )

        _dV_rv = self._heart._rv.vol - self._prev_rv_vol
        # if the volume is increasing count the stroke volume
        if _dV_rv > 0:
            self._sv_rv_cum += _dV_rv
            self._pv_area_rv_inc += (
                _dV_rv * self._prev_rv_pres
                + (_dV_rv * (self._heart._rv.pres - self._prev_rv_pres)) / 2.0
            )
        else:
            self._pv_area_rv_dec += (
                -_dV_rv * self._prev_rv_pres
                + (-_dV_rv * (self._heart._rv.pres - self._prev_rv_pres)) / 2.0
            )

        # store current volumes and pressures
        self._prev_lv_vol = self._heart._lv.vol
        self._prev_lv_pres = self._heart._lv.pres

        self._prev_rv_vol = self._heart._rv.vol
        self._prev_rv_pres = self._heart._rv.pres

        # return the total pressure volume area of both ventricles
        self.pva = self.stroke_work_lv + self.stroke_work_rv

        return (self.pva * self.pva_c * self.pva_c_factor * self.hw) / self._ml_to_mmol

    def calc_effectors(self, act):
        # calculate the gain of the effectors heart rate, contractility and autonomic nervous system suppression
        self.hr_g = (self.hr_factor_max - self.hr_factor_min) / (
            self.to2_max - self.to2_min
        )
        self.cont_g = (self.cont_factor_max - self.cont_factor_min) / (
            self.to2_max - self.to2_min
        )
        self.ans_g = (self.ans_factor_max - self.ans_factor_min) / (
            self.to2_max - self.to2_min
        )

        # incorporate the time constants
        self._d_hr = self._t * ((1 / self.hr_tc) * (-self._d_hr + act)) + self._d_hr
        self._d_cont = (
            self._t * ((1 / self.cont_tc) * (-self._d_cont + act)) + self._d_cont
        )
        self._d_ans = self._t * ((1 / self.ans_tc) * (-self._d_ans + act)) + self._d_ans

        # when hypoxia gets severe the ANS influence gets inhibited and the heartrate, contractility and baseline metabolism are decreased

        # calculate the new ans activity (1.0 is max activity and 0.0 is min activity) which controls the ans activity
        self.ans_activity_factor = 1.0 + self.ans_g * self._d_ans
        self._heart.ans_activity_factor = self.ans_activity_factor

        # calculate the mob factor which controls the heart rate
        self.hr_factor = 1.0 + self.hr_g * self._d_hr
        self._heart.hr_mob_factor = self.hr_factor

        # calculate the mob factor which controls the contractility of the heart
        self.cont_factor = 1.0 + self.cont_g * self._d_cont
        self._heart._lv.el_max_mob_factor = self.cont_factor
        self._heart._rv.el_max_mob_factor = self.cont_factor
        self._heart._la.el_max_mob_factor = self.cont_factor
        self._heart._ra.el_max_mob_factor = self.cont_factor

    def activation_function(self, value, max, setpoint, min):
        activation = 0.0

        if value >= max:
            activation = max - setpoint
        else:
            if value <= min:
                activation = min - setpoint
            else:
                activation = value - setpoint

        return activation
