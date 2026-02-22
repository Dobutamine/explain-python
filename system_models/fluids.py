from base_models.base_model import BaseModel


class Fluids(BaseModel):
	"""Fluid administration manager for scheduled infusions into compartments."""

	model_type = "fluids"

	def __init__(self, model_ref={}, name=None):
		"""Initialize fluid presets, infusion queue, and update cadence."""
		super().__init__(model_ref=model_ref, name=name)

		self.fluids_temp = 37.0
		self.fluids = {}
		self.default_volume = 10.0

		self._default_time = 10.0
		self._default_type = "normal_saline"
		self._running_fluid_list = []
		self._update_interval = 0.015
		self._update_counter = 0.0

	def init_model(self, args=None):
		"""Initialize fluid model configuration."""
		super().init_model(args)

	def _resolve_model(self, model_name):
		"""Resolve a model by name from local registry or attached engine."""
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
		"""Advance infusion scheduler and apply queued fluid deliveries."""
		self._update_counter += getattr(self, "_t", 0.0)
		if self._update_counter > self._update_interval:
			self._update_counter = 0.0
			self.process_fluid_list()

	def add_volume(self, volume, in_time=10.0, fluid_in="normal_saline", site="VLB"):
		"""Queue an infusion with volume/time/composition and target site."""
		volume_l = float(volume) / 1000.0
		in_time = float(in_time)
		if in_time <= 0.0:
			in_time = self._update_interval

		composition = {}
		if isinstance(self.fluids, dict):
			composition = dict(self.fluids.get(str(fluid_in), {}) or {})

		delta = volume_l / (in_time / self._update_interval)

		fluid = {
			"vol": volume_l,
			"time_left": in_time,
			"delta": delta,
			"site": str(site),
			"to2": 0.0,
			"tco2": 0.0,
			"temp": float(self.fluids_temp),
			"viscosity": 1.0,
			"solutes": composition,
			"drugs": {},
		}

		self._running_fluid_list.append(fluid)

	def process_fluid_list(self):
		"""Process active infusions and deliver per-step volume increments."""
		if not self._running_fluid_list:
			return

		self._running_fluid_list = [
			item for item in self._running_fluid_list if float(item.get("time_left", 0.0) or 0.0) > 0.0
		]

		for fluid in self._running_fluid_list:
			fluid["vol"] = float(fluid.get("vol", 0.0) or 0.0) - float(fluid.get("delta", 0.0) or 0.0)
			fluid["time_left"] = float(fluid.get("time_left", 0.0) or 0.0) - self._update_interval

			if fluid["time_left"] <= 0.0:
				fluid["delta"] = 0.0
				fluid["time_left"] = 0.0

			site_model = self._resolve_model(fluid.get("site"))
			if site_model is None:
				continue

			delta_volume = float(fluid.get("delta", 0.0) or 0.0)
			if delta_volume > 0.0 and hasattr(site_model, "volume_in"):
				site_model.volume_in(delta_volume, fluid)
