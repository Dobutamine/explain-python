import importlib
import inspect
import json
import re
from collections.abc import Mapping
from pathlib import Path

from base_models.base_model import BaseModel


class ModelEngine:
	def __init__(self, modeling_stepsize=0.0005):
		self.models = {}
		self.model_definition = {}
		self.modeling_stepsize = float(modeling_stepsize)
		self.is_initialized = False

	def load_json_file(self, file_path):
		path = Path(file_path)
		if not path.exists():
			raise FileNotFoundError(f"Model definition file not found: {path}")

		with path.open("r", encoding="utf-8") as file_handle:
			definition = json.load(file_handle)

		self.build(definition)
		return self

	def build(self, model_definition):
		if not isinstance(model_definition, Mapping):
			raise TypeError("Model definition must be a dictionary")

		self.is_initialized = False
		self.model_definition = dict(model_definition)
		self.models = {}

		self._apply_general_settings(model_definition)
		model_configs = self._extract_model_configs(model_definition)

		for model_name, model_config in model_configs.items():
			model_type = model_config.get("model_type")
			if not model_type:
				raise ValueError(f"Model '{model_name}' is missing 'model_type'")

			model_class = self._resolve_model_class(model_type)
			if model_class is None:
				raise ValueError(f"Unknown model_type '{model_type}' for model '{model_name}'")

			self.models[model_name] = model_class(model_ref=self, name=model_name)

		for model_name, model_config in model_configs.items():
			self.models[model_name].init_model(dict(model_config))

		self.is_initialized = True
		return self

	def step_model(self):
		for model in self.models.values():
			model.step_model()

	def _apply_general_settings(self, model_definition):
		general_config = model_definition.get("general")
		if isinstance(general_config, Mapping):
			for key, value in general_config.items():
				setattr(self, key, value)

		excluded_keys = {"models", "components", "helpers", "general"}
		for key, value in model_definition.items():
			if key in excluded_keys:
				continue
			setattr(self, key, value)

		self.modeling_stepsize = float(getattr(self, "modeling_stepsize", self.modeling_stepsize))

	def _extract_model_configs(self, model_definition):
		merged_configs = {}

		for section_key in ["models", "components", "helpers"]:
			section_data = model_definition.get(section_key)
			if section_data is None:
				continue

			section_configs = self._normalize_model_section(section_data, section_name=section_key)
			for model_name, model_config in section_configs.items():
				merged_configs[model_name] = model_config

		return merged_configs

	def _normalize_model_section(self, section_data, section_name):
		configs = {}

		if isinstance(section_data, Mapping):
			for key, value in section_data.items():
				if not isinstance(value, Mapping):
					continue

				model_name = str(value.get("name") or key)
				config = dict(value)
				config["name"] = model_name
				configs[model_name] = config
			return configs

		if isinstance(section_data, list):
			for index, item in enumerate(section_data):
				if not isinstance(item, Mapping):
					continue

				item_name = item.get("name")
				if not item_name:
					raise ValueError(
						f"Entry at index {index} in '{section_name}' must define 'name'"
					)

				config = dict(item)
				config["name"] = str(item_name)
				configs[str(item_name)] = config
			return configs

		raise TypeError(f"'{section_name}' must be a dictionary or a list")

	def _resolve_model_class(self, model_type):
		model_type_str = str(model_type)
		normalized_target = re.sub(r"_", "", model_type_str).lower()
		legacy_aliases = {
			"bloodpump": ("pump", "pump"),
		}
		if normalized_target in legacy_aliases:
			normalized_target, snake_name = legacy_aliases[normalized_target]
		else:
			snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", model_type_str).lower()

		candidate_modules = [
			f"base_models.{snake_name}",
			f"composite_models.{snake_name}",
			f"derived_models.{snake_name}",
			f"system_models.{snake_name}",
			f"device_models.{snake_name}",
		]

		for module_name in candidate_modules:
			try:
				module = importlib.import_module(module_name)
			except ModuleNotFoundError:
				continue

			for _, candidate_class in inspect.getmembers(module, inspect.isclass):
				if not issubclass(candidate_class, BaseModel):
					continue

				normalized_name = re.sub(r"_", "", candidate_class.__name__).lower()
				normalized_model_type = re.sub(
					r"_", "", str(getattr(candidate_class, "model_type", ""))
				).lower()

				if normalized_name == normalized_target or normalized_model_type == normalized_target:
					return candidate_class

		return None
