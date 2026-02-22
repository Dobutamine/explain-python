from base_models.base_model import BaseModel


class Metabolism(BaseModel):
	"""Whole-body metabolism model consuming O2 and producing CO2 per compartment."""

	model_type = "metabolism"

	def __init__(self, model_ref={}, name=None):
		"""Initialize metabolism settings and active compartment distribution."""
		super().__init__(model_ref=model_ref, name=name)

		self.met_active = True
		self.vo2 = 8.1
		self.vo2_factor = 1.0
		self.resp_q = 0.8
		self.metabolic_active_models = {}

	def set_metabolic_active_model(self, site, fvo2=None, new_fvo2=None):
		"""Set fractional oxygen consumption contribution for one site."""
		if not site:
			return

		value = fvo2 if fvo2 is not None else new_fvo2
		if value is None:
			return

		self.metabolic_active_models[str(site)] = float(value)

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
		"""Run one metabolic step and update to2/tco2 in active compartments."""
		if not self.met_active:
			return

		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		model_engine = getattr(self, "_model_engine", None)
		body_weight = float(getattr(model_engine, "weight", 1.0) or 1.0)

		vo2_step = ((0.039 * self.vo2 * self.vo2_factor * body_weight) / 60.0) * time_step

		for model_name, fvo2 in self.metabolic_active_models.items():
			compartment = self._resolve_model(model_name)
			if compartment is None:
				continue

			compartment_type = str(getattr(compartment, "model_type", "")).lower()
			if compartment_type in {"microvascularunit", "micro_vascular_unit"}:
				capillary_compartment = self._resolve_model(f"{model_name}_CAP")
				if capillary_compartment is not None:
					compartment = capillary_compartment

			vol = float(getattr(compartment, "vol", 0.0) or 0.0)
			if vol == 0.0:
				continue

			to2 = float(getattr(compartment, "to2", 0.0) or 0.0)
			tco2 = float(getattr(compartment, "tco2", 0.0) or 0.0)

			dto2 = vo2_step * float(fvo2)
			new_to2 = max((to2 * vol - dto2) / vol, 0.0)

			dtco2 = vo2_step * float(fvo2) * self.resp_q
			new_tco2 = max((tco2 * vol + dtco2) / vol, 0.0)

			compartment.to2 = new_to2
			compartment.tco2 = new_tco2
