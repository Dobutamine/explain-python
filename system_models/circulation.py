from base_models.base_model import BaseModel


class Circulation(BaseModel):
	model_type = "circulation"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.heart_chambers = []
		self.coronaries = []
		self.systemic_arteries = []
		self.systemic_veins = []
		self.systemic_capillaries = []
		self.pulmonary_arteries = []
		self.pulmonary_veins = []
		self.pulmonary_capillaries = []
		self.ans_activity = 1.0
		self.svr_factor = 1.0
		self.pvr_factor = 1.0

		self.total_blood_volume = 0.0
		self.syst_blood_volume = 0.0
		self.pulm_blood_volume = 0.0
		self.heart_blood_volume = 0.0
		self.syst_blood_volume_perc = 0.0
		self.pulm_blood_volume_perc = 0.0
		self.heart_blood_volume_perc = 0.0

		self._combined_list = []
		self._syst_models = []
		self._pulm_models = []
		self._prev_ans_activity = 0.0
		self._prev_svr_factor = 1.0
		self._prev_pvr_factor = 1.0
		self._update_interval = 0.015
		self._update_counter = 0.0
		self._update_interval_slow = 1.0
		self._update_counter_slow = 0.0

	def init_model(self, args=None):
		super().init_model(args)

		self._combined_list = [
			*self.systemic_arteries,
			*self.systemic_capillaries,
			*self.systemic_veins,
			*self.pulmonary_arteries,
			*self.pulmonary_capillaries,
			*self.pulmonary_veins,
		]

		self._syst_models = [
			*self.systemic_arteries,
			*self.systemic_capillaries,
			*self.systemic_veins,
		]

		self._pulm_models = [
			*self.pulmonary_arteries,
			*self.pulmonary_capillaries,
			*self.pulmonary_veins,
		]

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
		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		self._update_counter += time_step
		if self._update_counter > self._update_interval:
			self._update_counter = 0.0

			if self._prev_ans_activity != self.ans_activity:
				for model_name in self._combined_list:
					model = self._resolve_model(model_name)
					if model is None:
						continue
					model.ans_activity = self.ans_activity
				self._prev_ans_activity = self.ans_activity

			if self._prev_svr_factor != self.svr_factor:
				self.set_svr_factor(self.svr_factor)
				self._prev_svr_factor = self.svr_factor

			if self._prev_pvr_factor != self.pvr_factor:
				self.set_pvr_factor(self.pvr_factor)
				self._prev_pvr_factor = self.pvr_factor

		self._update_counter_slow += time_step
		if self._update_counter_slow > self._update_interval_slow:
			self._update_counter_slow = 0.0
			self.calc_blood_volumes()

	def set_svr_factor(self, new_svr_factor):
		updated_svr_factor = float(new_svr_factor)

		for model_name in self._syst_models:
			model = self._resolve_model(model_name)
			if model is None:
				continue

			f_ps = float(getattr(model, "r_factor_ps", 1.0))
			delta_svr = updated_svr_factor - self._prev_svr_factor
			f_ps += delta_svr

			if f_ps < 0.0:
				updated_svr_factor = -f_ps
				f_ps = 0.0

			model.r_factor_ps = f_ps

		self.svr_factor = updated_svr_factor

	def set_pvr_factor(self, new_pvr_factor):
		updated_pvr_factor = float(new_pvr_factor)

		for model_name in self._pulm_models:
			model = self._resolve_model(model_name)
			if model is None:
				continue

			f_ps = float(getattr(model, "r_factor_ps", 1.0))
			delta_pvr = updated_pvr_factor - self._prev_pvr_factor
			f_ps += delta_pvr

			if f_ps < 0.0:
				updated_pvr_factor = -f_ps
				f_ps = 0.0

			model.r_factor_ps = f_ps

		self.pvr_factor = updated_pvr_factor

	def calc_blood_volumes(self):
		self.total_blood_volume = 0.0
		self.syst_blood_volume = 0.0
		self.pulm_blood_volume = 0.0
		self.heart_blood_volume = 0.0

		for model_name in self._syst_models:
			model = self._resolve_model(model_name)
			if model is not None and getattr(model, "is_enabled", False):
				self.syst_blood_volume += float(getattr(model, "vol", 0.0) or 0.0)

		for model_name in self.heart_chambers:
			model = self._resolve_model(model_name)
			if model is not None and getattr(model, "is_enabled", False):
				self.heart_blood_volume += float(getattr(model, "vol", 0.0) or 0.0)

		for model_name in self.coronaries:
			model = self._resolve_model(model_name)
			if model is not None and getattr(model, "is_enabled", False):
				self.syst_blood_volume += float(getattr(model, "vol", 0.0) or 0.0)

		for model_name in self._pulm_models:
			model = self._resolve_model(model_name)
			if model is not None and getattr(model, "is_enabled", False):
				self.pulm_blood_volume += float(getattr(model, "vol", 0.0) or 0.0)

		self.total_blood_volume = self.syst_blood_volume + self.pulm_blood_volume + self.heart_blood_volume

		if self.total_blood_volume > 0.0:
			self.syst_blood_volume_perc = (self.syst_blood_volume / self.total_blood_volume) * 100.0
			self.pulm_blood_volume_perc = (self.pulm_blood_volume / self.total_blood_volume) * 100.0
			self.heart_blood_volume_perc = (self.heart_blood_volume / self.total_blood_volume) * 100.0
		else:
			self.syst_blood_volume_perc = 0.0
			self.pulm_blood_volume_perc = 0.0
			self.heart_blood_volume_perc = 0.0
