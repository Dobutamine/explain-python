from base_models.base_model import BaseModel


class Mob(BaseModel):
	model_type = "mob"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.mob_active = True
		self.to2_min = 0.0002
		self.to2_ref = 0.2
		self.resp_q = 0.1
		self.bm_vo2_ref = 0.0007
		self.bm_vo2_min = 0.00035
		self.bm_vo2_tc = 5.0
		self.bm_g = 0.0
		self.ecc_ref = 0.00000301
		self.pva_ref = 0.00143245
		self.pe_ref = 0.0
		self.hr_factor = 1.0
		self.hr_factor_max = 1.0
		self.hr_factor_min = 0.01
		self.hr_tc = 5.0
		self.cont_factor = 1.0
		self.cont_factor_max = 1.0
		self.cont_factor_min = 0.01
		self.cont_tc = 5.0
		self.act_factor = 1.0
		self.ans_factor = 1.0
		self.ans_factor_max = 1.0
		self.ans_factor_min = 0.01
		self.ans_tc = 5.0
		self.ans_activity_factor = 1.0

		self.hw = 0.0
		self.mob_vo2 = 0.0
		self.bm_vo2 = 0.0
		self.ecc_vo2 = 0.0
		self.pe_vo2 = 0.0
		self.pva_vo2 = 0.0
		self.pva = 0.0
		self.stroke_work_lv = 0.0
		self.stroke_work_rv = 0.0
		self.mob = 0.0
		self.mvo2_step = 0.0

		self._aa = None
		self._cor = None
		self._aa_cor = None
		self._heart = None
		self._lv = None
		self._rv = None
		self._la = None
		self._ra = None
		self._a_to2 = 0.0
		self._d_bm_vo2 = 0.0
		self._d_hr = 0.0
		self._d_cont = 0.0
		self._d_ans = 0.0
		self._ml_to_mmol = 22.414
		self._cc_time = 0.0
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

	def _resolve_model(self, model_name):
		if not model_name:
			return None

		if isinstance(self.model_ref, dict) and model_name in self.model_ref:
			return self.model_ref[model_name]

		model_engine = getattr(self, "_model_engine", None)
		if model_engine is not None:
			models = getattr(model_engine, "models", None)
			if isinstance(models, dict):
				return models.get(model_name)

		return None

	def _resolve_first(self, *names):
		for name in names:
			model = self._resolve_model(name)
			if model is not None:
				return model
		return None

	def calc_model(self):
		if not self.mob_active:
			return

		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		model_engine = getattr(self, "_model_engine", None)
		weight = float(getattr(model_engine, "weight", 3.5) or 3.5)
		self.hw = 7.799 + 0.004296 * weight * 1000.0

		to2_span = self.to2_ref - self.to2_min
		if to2_span <= 0.0:
			return

		self.bm_g = (self.bm_vo2_ref * self.hw - self.bm_vo2_min * self.hw) / to2_span
		self.hr_g = (self.hr_factor_max - self.hr_factor_min) / to2_span
		self.cont_g = (self.cont_factor_max - self.cont_factor_min) / to2_span
		self.ans_g = (self.ans_factor_max - self.ans_factor_min) / to2_span

		self._aa = self._resolve_first("AA", "AORTA")
		self._aa_cor = self._resolve_first("AA_COR", "AAR_COR")
		self._cor = self._resolve_model("COR")
		self._heart = self._resolve_first("Heart", "HEART", "heart")
		self._lv = self._resolve_model("LV")
		self._rv = self._resolve_model("RV")
		self._la = self._resolve_model("LA")
		self._ra = self._resolve_model("RA")

		if any(model is None for model in [self._aa, self._aa_cor, self._cor, self._heart, self._lv, self._rv]):
			return

		to2_cor = float(getattr(self._cor, "to2", 0.0) or 0.0)
		tco2_cor = float(getattr(self._cor, "tco2", 0.0) or 0.0)
		vol_cor = float(getattr(self._cor, "vol", 0.0) or 0.0)
		self._cc_time = float(getattr(self._heart, "cardiac_cycle_time", 0.0) or 0.0)

		self._a_to2 = self.activation_function(to2_cor, self.to2_ref, self.to2_ref, self.to2_min)

		self._d_bm_vo2 = time_step * ((1.0 / self.bm_vo2_tc) * (-self._d_bm_vo2 + self._a_to2)) + self._d_bm_vo2
		self._d_hr = time_step * ((1.0 / self.hr_tc) * (-self._d_hr + self._a_to2)) + self._d_hr
		self._d_cont = time_step * ((1.0 / self.cont_tc) * (-self._d_cont + self._a_to2)) + self._d_cont
		self._d_ans = time_step * ((1.0 / self.ans_tc) * (-self._d_ans + self._a_to2)) + self._d_ans

		self.bm_vo2 = self.calc_bm()
		self.calc_hypoxia_effects()

		self.ecc_vo2 = self.calc_ecc()
		self.pva_vo2 = self.calc_pva()
		self.pe_vo2 = self.calc_pe()

		self.mob_vo2 = self.bm_vo2 + self.ecc_vo2 + self.pva_vo2 + self.pe_vo2

		bm_vo2_step = self.bm_vo2 * time_step
		ecc_vo2_step = 0.0
		pva_vo2_step = 0.0
		pe_vo2_step = 0.0

		if self._cc_time > 0.0 and bool(getattr(self._heart, "cardiac_cycle_running", 0)):
			ecc_vo2_step = (self.ecc_vo2 / self._cc_time) * time_step
			pva_vo2_step = (self.pva_vo2 / self._cc_time) * time_step
			pe_vo2_step = (self.pe_vo2 / self._cc_time) * time_step

		self.mvo2_step = bm_vo2_step + ecc_vo2_step + pva_vo2_step + pe_vo2_step
		co2_production = self.mvo2_step * self.resp_q

		o2_inflow = float(getattr(self._aa_cor, "flow", 0.0) or 0.0) * float(getattr(self._aa, "to2", 0.0) or 0.0)
		o2_use = self.mvo2_step / time_step
		self.mob = o2_inflow - o2_use + to2_cor

		if vol_cor > 0.0:
			new_to2_cor = (to2_cor * vol_cor - self.mvo2_step) / vol_cor
			new_tco2_cor = (tco2_cor * vol_cor + co2_production) / vol_cor
			if new_to2_cor >= 0.0:
				self._cor.to2 = new_to2_cor
				self._cor.tco2 = new_tco2_cor

	def calc_bm(self):
		bm_vo2 = self.bm_vo2_ref * self.hw + self._d_bm_vo2 * self.bm_g
		min_bm = self.bm_vo2_min * self.hw
		if bm_vo2 < min_bm:
			bm_vo2 = min_bm
		return bm_vo2 / self._ml_to_mmol

	def calc_ecc(self):
		self.ecc_lv = float(getattr(self._lv, "el_max", 0.0) or 0.0)
		self.ecc_rv = float(getattr(self._rv, "el_max", 0.0) or 0.0)
		self.ecc = (self.ecc_lv + self.ecc_rv) / 1000.0
		return (self.ecc * self.ecc_ref * self.hw) / self._ml_to_mmol

	def calc_pe(self):
		self.pe = 0.0
		return (self.pe * self.pe_ref * self.hw) / self._ml_to_mmol

	def calc_pva(self):
		if bool(getattr(self._heart, "cardiac_cycle_running", 0)) and not bool(
			getattr(self._heart, "_prev_cardiac_cycle_running", 0)
		):
			self.stroke_work_lv = self._pv_area_lv_dec - self._pv_area_lv_inc
			self.stroke_work_rv = self._pv_area_rv_dec - self._pv_area_rv_inc
			self._pv_area_lv_inc = 0.0
			self._pv_area_rv_inc = 0.0
			self._pv_area_lv_dec = 0.0
			self._pv_area_rv_dec = 0.0

		delta_v_lv = float(getattr(self._lv, "vol", 0.0) or 0.0) - self._prev_lv_vol
		lv_pres = float(getattr(self._lv, "pres", 0.0) or 0.0)
		if delta_v_lv > 0.0:
			self._pv_area_lv_inc += delta_v_lv * self._prev_lv_pres + (delta_v_lv * (lv_pres - self._prev_lv_pres)) / 2.0
		else:
			self._pv_area_lv_dec += (-delta_v_lv) * self._prev_lv_pres + ((-delta_v_lv) * (lv_pres - self._prev_lv_pres)) / 2.0

		delta_v_rv = float(getattr(self._rv, "vol", 0.0) or 0.0) - self._prev_rv_vol
		rv_pres = float(getattr(self._rv, "pres", 0.0) or 0.0)
		if delta_v_rv > 0.0:
			self._pv_area_rv_inc += delta_v_rv * self._prev_rv_pres + (delta_v_rv * (rv_pres - self._prev_rv_pres)) / 2.0
		else:
			self._pv_area_rv_dec += (-delta_v_rv) * self._prev_rv_pres + ((-delta_v_rv) * (rv_pres - self._prev_rv_pres)) / 2.0

		self._prev_lv_vol = float(getattr(self._lv, "vol", 0.0) or 0.0)
		self._prev_lv_pres = lv_pres
		self._prev_rv_vol = float(getattr(self._rv, "vol", 0.0) or 0.0)
		self._prev_rv_pres = rv_pres

		self.pva = self.stroke_work_lv + self.stroke_work_rv
		return (self.pva * self.pva_ref * self.hw) / self._ml_to_mmol

	def calc_hypoxia_effects(self):
		self.ans_activity_factor = 1.0 + self.ans_g * self._d_ans
		setattr(self._heart, "ans_activity_factor", self.ans_activity_factor)

		self.hr_factor = 1.0 + self.hr_g * self._d_hr
		self._heart.hr_mob_factor = self.hr_factor

		self.cont_factor = 1.0 + self.cont_g * self._d_cont

		for chamber in [self._lv, self._rv, self._la, self._ra]:
			if chamber is None:
				continue
			setattr(chamber, "el_max_mob_factor", self.cont_factor)
			if hasattr(chamber, "el_max_factor"):
				chamber.el_max_factor = self.cont_factor

	def activation_function(self, value, max_value, setpoint, min_value):
		activation = 0.0

		if value >= max_value:
			activation = max_value - setpoint
		elif value <= min_value:
			activation = min_value - setpoint
		else:
			activation = value - setpoint

		return activation
