from base_models.base_model import BaseModel


class AnsEfferent(BaseModel):
	model_type = "ans_efferent"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.target_model = ""
		self.target_prop = ""
		self.effect_at_max_firing_rate = 0.0
		self.effect_at_min_firing_rate = 0.0
		self.tc = 0.0

		self.firing_rate = 0.0
		self.effector = 1.0

		self._update_interval = 0.015
		self._update_counter = 0.0
		self._cum_firing_rate = 0.0
		self._cum_firing_rate_counter = 1.0

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
		self._update_counter += getattr(self, "_t", 0.0)
		if self._update_counter < self._update_interval:
			return

		self._update_counter = 0.0

		self.firing_rate = 0.5
		if self._cum_firing_rate_counter > 0.0:
			self.firing_rate = self._cum_firing_rate / self._cum_firing_rate_counter

		if self.firing_rate >= 0.5:
			effector = 1.0 + ((self.effect_at_max_firing_rate - 1.0) / 0.5) * (self.firing_rate - 0.5)
		else:
			effector = self.effect_at_min_firing_rate + ((1.0 - self.effect_at_min_firing_rate) / 0.5) * self.firing_rate

		tc = float(self.tc)
		if tc <= 0.0:
			tc = 1e-9
		self.effector = self._update_interval * ((1.0 / tc) * (-self.effector + effector)) + self.effector

		target = self._resolve_model(self.target_model)
		if target is not None and self.target_prop:
			setattr(target, self.target_prop, self.effector)

		self._cum_firing_rate = 0.5
		self._cum_firing_rate_counter = 0.0

	def update_effector(self, new_firing_rate, weight):
		self._cum_firing_rate += (float(new_firing_rate) - 0.5) * float(weight)
		self._cum_firing_rate_counter += 1.0
