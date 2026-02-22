from base_models.base_model import BaseModel


class AnsAfferent(BaseModel):
	model_type = "ans_afferent"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.input_model = ""
		self.input_prop = ""
		self.efferents = []
		self.effect_weight = 1.0
		self.min_value = 0.0
		self.set_value = 0.0
		self.max_value = 0.0
		self.time_constant = 1.0

		self.input_value = 0.0
		self.firing_rate = 0.0

		self._update_interval = 0.015
		self._update_counter = 0.0
		self._max_firing_rate = 1.0
		self._set_firing_rate = 0.5
		self._min_firing_rate = 0.0
		self._gain = 0.0

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

		input_component = self._resolve_model(self.input_model)
		if input_component is None or not self.input_prop:
			return

		self.input_value = float(getattr(input_component, self.input_prop, 0.0) or 0.0)

		activation = 0.0
		if self.input_value > self.max_value:
			activation = self.max_value - self.set_value
		elif self.input_value < self.min_value:
			activation = self.min_value - self.set_value
		else:
			activation = self.input_value - self.set_value

		if activation > 0.0:
			denominator = self.max_value - self.set_value
			self._gain = (
				(self._max_firing_rate - self._set_firing_rate) / denominator
				if denominator != 0.0
				else 0.0
			)
		else:
			denominator = self.set_value - self.min_value
			self._gain = (
				(self._set_firing_rate - self._min_firing_rate) / denominator
				if denominator != 0.0
				else 0.0
			)

		new_firing_rate = self._set_firing_rate + self._gain * activation
		tc = float(self.time_constant)
		if tc <= 0.0:
			tc = 1e-9
		self.firing_rate = self._update_interval * ((1.0 / tc) * (-self.firing_rate + new_firing_rate)) + self.firing_rate

		for effector_name in self.efferents:
			effector = self._resolve_model(effector_name)
			if effector is not None and hasattr(effector, "update_effector"):
				effector.update_effector(self.firing_rate, self.effect_weight)
