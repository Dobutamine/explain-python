import math

from base_models.base_model import BaseModel


class Breathing(BaseModel):
	model_type = "breathing"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.breathing_enabled = True
		self.minute_volume_ref = 0.2
		self.minute_volume_ref_factor = 1.0
		self.minute_volume_ref_scaling_factor = 1.0
		self.vt_rr_ratio = 0.0001212
		self.vt_rr_ratio_factor = 1.0
		self.vt_rr_ratio_scaling_factor = 1.0
		self.rmp_gain_max = 100.0
		self.ie_ratio = 0.3
		self.mv_ans_factor = 1.0
		self.ans_activity_factor = 1.0

		self.target_minute_volume = 0.0
		self.resp_rate = 36.0
		self.resp_rate_measured = 36.0
		self.target_tidal_volume = 0.0
		self.minute_volume = 0.0
		self.exp_tidal_volume = 0.0
		self.insp_tidal_volume = 0.0
		self.resp_muscle_pressure = 0.0
		self.ncc_insp = 0
		self.ncc_exp = 0
		self.rmp_gain = 9.5

		self._e_min_4 = math.exp(-4.0)
		self._ti = 0.4
		self._te = 1.0
		self._breath_timer = 0.0
		self._breath_interval = 60.0
		self._insp_running = False
		self._insp_timer = 0.0
		self._temp_insp_volume = 0.0
		self._exp_running = False
		self._exp_timer = 0.0
		self._temp_exp_volume = 0.0
		self._rr_counter = 0.0
		self._rr_factor = 0.0

		self.debug_factor1 = 0.0

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

	def calc_model(self):
		model_engine = getattr(self, "_model_engine", None)
		weight = float(getattr(model_engine, "weight", 1.0) or 1.0)
		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		minute_volume_ref = (
			self.minute_volume_ref
			* self.minute_volume_ref_factor
			* self.minute_volume_ref_scaling_factor
			* weight
		)
		self.target_minute_volume = (
			minute_volume_ref + (self.mv_ans_factor - 1.0) * minute_volume_ref
		) * self.ans_activity_factor

		self.vt_rr_controller(weight)

		self._breath_interval = 60.0
		if self.resp_rate > 0.0:
			self._breath_interval = 60.0 / self.resp_rate
			self._ti = self.ie_ratio * self._breath_interval
			self._te = self._breath_interval - self._ti

		if self._breath_timer > self._breath_interval:
			self._breath_timer = 0.0
			self._insp_running = True
			self._insp_timer = 0.0
			self.ncc_insp = 0

		if self._insp_timer > self._ti:
			self._insp_timer = 0.0
			self._insp_running = False
			self._exp_running = True
			self.ncc_exp = 0
			self._temp_exp_volume = 0.0
			self.insp_tidal_volume = self._temp_insp_volume

		if self._exp_timer > self._te:
			self._exp_timer = 0.0
			self._exp_running = False
			self._temp_insp_volume = 0.0
			self.exp_tidal_volume = -self._temp_exp_volume

			if self.breathing_enabled:
				if abs(self.exp_tidal_volume) < self.target_tidal_volume:
					self.rmp_gain += 0.1
				if abs(self.exp_tidal_volume) > self.target_tidal_volume:
					self.rmp_gain -= 0.1
				self.rmp_gain = max(0.0, min(self.rmp_gain, self.rmp_gain_max))

			self.minute_volume = self.exp_tidal_volume * self.resp_rate

		self._breath_timer += time_step

		mouth_ds = self._resolve_model("MOUTH_DS")
		mouth_flow = float(getattr(mouth_ds, "flow", 0.0) or 0.0)

		if self._insp_running:
			self._insp_timer += time_step
			self.ncc_insp += 1
			if mouth_flow > 0.0:
				self._temp_insp_volume += mouth_flow * time_step

		if self._exp_running:
			self._exp_timer += time_step
			self.ncc_exp += 1
			if mouth_flow < 0.0:
				self._temp_exp_volume += mouth_flow * time_step

		self.resp_muscle_pressure = 0.0
		if self.breathing_enabled:
			self.resp_muscle_pressure = self.calc_resp_muscle_pressure()
		else:
			self.resp_rate = 0.0
			self.ncc_insp = 0.0
			self.ncc_exp = 0.0
			self.target_tidal_volume = 0.0
			self.resp_muscle_pressure = 0.0

		if self.ncc_insp == 1 and self._rr_counter > 0.0:
			self.resp_rate_measured = 60.0 / self._rr_counter
			self._rr_counter = 0.0
			self._rr_factor = 1.0

		if self._rr_counter > 2.0 * self._rr_factor and self._rr_counter > 0.0:
			self.resp_rate_measured = 60.0 / self._rr_counter
			self._rr_factor += 1.0

		self._rr_counter += time_step

		thorax = self._resolve_model("THORAX")
		if thorax is not None and hasattr(thorax, "el_base_factor"):
			thorax.el_base_factor += self.resp_muscle_pressure

	def vt_rr_controller(self, weight):
		if not self.breathing_enabled:
			self.resp_rate = 0.0
			return

		denominator = (
			self.vt_rr_ratio
			* self.vt_rr_ratio_factor
			* self.vt_rr_ratio_scaling_factor
			* weight
		)
		if denominator <= 0.0:
			self.resp_rate = 0.0
			self.target_tidal_volume = 0.0
			return

		self.resp_rate = math.sqrt(self.target_minute_volume / denominator)

		if self.resp_rate > 0.0:
			self.target_tidal_volume = self.target_minute_volume / self.resp_rate
		else:
			self.target_tidal_volume = 0.0

	def calc_resp_muscle_pressure(self):
		mp = 0.0
		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return mp

		if self._insp_running and self._ti > 0.0:
			mp = (self.ncc_insp / (self._ti / time_step)) * self.rmp_gain

		if self._exp_running and self._te > 0.0:
			mp = (
				(math.exp(-4.0 * (self.ncc_exp / (self._te / time_step))) - self._e_min_4)
				/ (1.0 - self._e_min_4)
			) * self.rmp_gain

		return mp

	def switch_breathing(self, state):
		self.breathing_enabled = bool(state)
