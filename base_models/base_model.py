from abc import ABC, abstractmethod
from collections.abc import Mapping
import importlib
import inspect
import re


class BaseModel(ABC):
    # define class-level properties that are common to all models
    model_type = "base"

    def __init__(self, model_ref=None, name=None):
        # initialization of the base model properties
        if model_ref is None:
            model_ref = {}

        self.name = name # unique name of the component, which can be used to reference it in the model
        self.description = "" # optional description of the component
        self.is_enabled = False # flag to indicate whether the component is active in the model, default is False. This can be used to enable or disable components without removing them from the model.
        self.components = {} # nested component definitions for this model

        self._model_engine = model_ref if hasattr(model_ref, "models") else None
        if self._model_engine is not None:
            models = getattr(self._model_engine, "models", None)
            self.model_ref = models if isinstance(models, dict) else {}
            self._t = float(getattr(self._model_engine, "modeling_stepsize", 0.0) or 0.0)
        else:
            self.model_ref = model_ref if isinstance(model_ref, dict) else {}
            self._t = 0.0
        self._is_initialized = False

    def init_model(self, args=None):
        # model property initialization from args (dict or [{"key":..., "value":...}])
        for key, value in self._normalize_init_args(args).items():
            if not hasattr(self, key):
                raise AttributeError(f"Unknown property: {key}")
            setattr(self, key, value)

        self._init_components()
        self._is_initialized = True

    def _normalize_init_args(self, args):
        if args is None:
            return {}

        if isinstance(args, Mapping):
            return dict(args)

        if isinstance(args, (list, tuple)):
            normalized = {}
            for item in args:
                if not isinstance(item, Mapping) or "key" not in item:
                    raise TypeError("list args must contain dict-like items with 'key' and 'value'")
                normalized[item["key"]] = item.get("value")
            return normalized

        raise TypeError("args must be a dict or a list/tuple of {'key', 'value'} items")

    def _init_components(self):
        if not isinstance(self.components, Mapping) or not self.components:
            return

        model_registry = self._get_model_registry()
        if model_registry is None:
            return

        for component_name, component_def in self.components.items():
            if component_name in model_registry:
                continue
            if not isinstance(component_def, Mapping):
                raise TypeError(f"Component definition for '{component_name}' must be a dict")

            model_type = component_def.get("model_type")
            if not model_type:
                raise ValueError(f"Component '{component_name}' is missing 'model_type'")

            component_class = self._resolve_model_class(model_type)
            if component_class is None:
                raise ValueError(f"Unknown component model_type: {model_type}")

            model_ref = self._model_engine if self._model_engine is not None else model_registry
            model_registry[component_name] = component_class(model_ref=model_ref, name=component_name)

        for component_name, component_def in self.components.items():
            component_args = [{"key": key, "value": value} for key, value in component_def.items()]
            model_registry[component_name].init_model(component_args)

    def _get_model_registry(self):
        if isinstance(self.model_ref, dict):
            return self.model_ref

        if self._model_engine is not None:
            models = getattr(self._model_engine, "models", None)
            if isinstance(models, dict):
                return models

        return None

    def _resolve_model_class(self, model_type):
        model_type_str = str(model_type)
        normalized_target = re.sub(r"_", "", model_type_str).lower()
        snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", model_type_str).lower()

        candidate_modules = [
            f"base_models.{snake_name}",
            f"composite_models.{snake_name}",
            f"component_models.{snake_name}",
            f"system_models.{snake_name}",
            f"device_models.{snake_name}",
        ]

        for module_name in candidate_modules:
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError:
                continue

            for _, candidate in inspect.getmembers(module, inspect.isclass):
                if not issubclass(candidate, BaseModel):
                    continue
                normalized_name = re.sub(r"_", "", candidate.__name__).lower()
                normalized_model_type = re.sub(r"_", "", str(getattr(candidate, "model_type", ""))).lower()
                if normalized_name == normalized_target or normalized_model_type == normalized_target:
                    return candidate

        return None

    def step_model(self):
        # default step_model implementation that can be overridden by subclasses
        if not self.is_enabled or not self._is_initialized:
            return
        
        self.calc_model()

    @abstractmethod
    def calc_model(self):
        raise NotImplementedError("calc_model must be implemented by subclasses")
