from base_models.base_model import BaseModel
from functions.blood_composition import calc_blood_composition
from collections.abc import Mapping


class Ans(BaseModel):
	model_type = "ans"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.ans_active = True
		self.components = {}
		self.blood_composition_models = []

		self._update_interval = 0.05
		self._update_counter = 0.0

	def init_model(self, args=None):
		if args is None:
			super().init_model(args)
			return

		normalized = dict(args) if isinstance(args, Mapping) else dict(self._normalize_init_args(args))
		linked_components = normalized.pop("components", None)

		super().init_model(normalized)

		if linked_components is not None:
			self.components = linked_components

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

		if isinstance(self.components, dict):
			component_names = list(self.components.keys())
		elif isinstance(self.components, (list, tuple, set)):
			component_names = list(self.components)
		else:
			component_names = []

		for component_name in component_names:
			component_model = self._resolve_model(component_name)
			if component_model is not None:
				component_model.is_enabled = bool(self.ans_active)

		for model_name in self.blood_composition_models:
			model = self._resolve_model(model_name)
			if model is not None and getattr(model, "is_enabled", False):
				calc_blood_composition(model)
