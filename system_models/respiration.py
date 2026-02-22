from base_models.base_model import BaseModel


class Respiration(BaseModel):
	model_type = "respiration"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.upper_airways = ["MOUTH_DS"]
		self.lower_airways = ["DS_ALL", "DS_ALR"]
		self.lower_airways_left = ["DS_ALL"]
		self.lower_airways_right = ["DS_ALR"]
		self.dead_space = ["DS"]
		self.thorax = ["THORAX"]
		self.pleural_space_left = []
		self.pleural_space_right = []
		self.lungs = ["ALL", "ALR"]
		self.left_lung = ["ALL"]
		self.right_lung = ["ALR"]
		self.gas_echangers = ["GASEX_LL", "GASEX_RL"]
		self.gas_exchanger_left_lung = ["GASEX_LL"]
		self.gas_exchanger_right_lung = ["GASEX_RL"]
		self.intrapulmonary_shunt = ["IPS"]

		self.el_lungs_factor = 1.0
		self.el_thorax_factor = 1.0
		self.res_upper_airways_factor = 1.0
		self.res_lower_airways_factor = 1.0
		self.gex_factor = 1.0

		self._update_interval = 0.015
		self._update_counter = 0.0
		self._prev_el_lungs_factor = 1.0
		self._prev_el_thorax_factor = 1.0
		self._prev_gex_factor = 1.0
		self._prev_res_upper_airways_factor = 1.0
		self._prev_res_lower_airways_factor = 1.0

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

			if self._prev_el_lungs_factor != self.el_lungs_factor:
				self.set_el_lung_factor(self.el_lungs_factor)
				self._prev_el_lungs_factor = self.el_lungs_factor

			if self._prev_el_thorax_factor != self.el_thorax_factor:
				self.set_el_thorax_factor(self.el_thorax_factor)
				self._prev_el_thorax_factor = self.el_thorax_factor

			if self._prev_res_upper_airways_factor != self.res_upper_airways_factor:
				self.set_upper_airway_resistance(self.res_upper_airways_factor)
				self._prev_res_upper_airways_factor = self.res_upper_airways_factor

			if self._prev_res_lower_airways_factor != self.res_lower_airways_factor:
				self.set_lower_airway_resistance(self.res_lower_airways_factor)
				self._prev_res_lower_airways_factor = self.res_lower_airways_factor

			if self._prev_gex_factor != self.gex_factor:
				self.set_gasexchange(self.gex_factor)
				self._prev_gex_factor = self.gex_factor

	def set_el_lung_factor(self, new_factor):
		updated_factor = float(new_factor)

		for lung_name in self.lungs:
			model = self._resolve_model(lung_name)
			if model is None:
				continue

			f_ps = float(getattr(model, "el_base_factor_ps", 1.0))
			delta = updated_factor - self._prev_el_lungs_factor
			f_ps += delta

			if f_ps < 0.0:
				updated_factor = -f_ps
				f_ps = 0.0

			model.el_base_factor_ps = f_ps

		self.el_lungs_factor = updated_factor

	def set_el_thorax_factor(self, new_factor):
		updated_factor = float(new_factor)

		for thorax_name in self.thorax:
			model = self._resolve_model(thorax_name)
			if model is None:
				continue

			f_ps = float(getattr(model, "el_base_factor_ps", 1.0))
			delta = updated_factor - self._prev_el_thorax_factor
			f_ps += delta

			if f_ps < 0.0:
				updated_factor = -f_ps
				f_ps = 0.0

			model.el_base_factor_ps = f_ps

		self.el_thorax_factor = updated_factor

	def set_upper_airway_resistance(self, new_factor):
		updated_factor = float(new_factor)

		for airway_name in self.upper_airways:
			model = self._resolve_model(airway_name)
			if model is None:
				continue

			f_ps = float(getattr(model, "r_factor_ps", 1.0))
			delta = updated_factor - self._prev_res_upper_airways_factor
			f_ps += delta

			if f_ps < 0.0:
				updated_factor = -f_ps
				f_ps = 0.0

			model.r_factor_ps = f_ps

		self.res_upper_airways_factor = updated_factor

	def set_lower_airway_resistance(self, new_factor):
		updated_factor = float(new_factor)

		for airway_name in self.lower_airways:
			model = self._resolve_model(airway_name)
			if model is None:
				continue

			f_ps = float(getattr(model, "r_factor_ps", 1.0))
			delta = updated_factor - self._prev_res_lower_airways_factor
			f_ps += delta

			if f_ps < 0.0:
				updated_factor = -f_ps
				f_ps = 0.0

			model.r_factor_ps = f_ps

		self.res_lower_airways_factor = updated_factor

	def set_gasexchange(self, new_factor):
		updated_factor = float(new_factor)

		for exchanger_name in self.gas_echangers:
			model = self._resolve_model(exchanger_name)
			if model is None:
				continue

			f_ps_o2 = float(getattr(model, "dif_o2_factor_ps", 1.0))
			f_ps_co2 = float(getattr(model, "dif_co2_factor_ps", 1.0))
			delta = updated_factor - self._prev_gex_factor

			f_ps_o2 += delta
			f_ps_co2 += delta

			if f_ps_o2 < 0.0:
				updated_factor = -f_ps_o2
				f_ps_o2 = 0.0
				f_ps_co2 = 0.0

			model.dif_o2_factor_ps = f_ps_o2
			model.dif_co2_factor_ps = f_ps_co2

		self.gex_factor = updated_factor
