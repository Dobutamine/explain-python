from base_models.base_model import BaseModel
from functions.blood_composition import calc_blood_composition


class Blood(BaseModel):
	"""Global blood composition manager and blood-gas snapshot provider."""

	model_type = "blood"

	def __init__(self, model_ref={}, name=None):
		"""Initialize global blood settings and monitored blood-gas outputs."""
		super().__init__(model_ref=model_ref, name=name)

		self.viscosity = 6.0
		self.temp = 37.0
		self.to2 = 0.0
		self.tco2 = 0.0
		self.solutes = {}
		self.P50_0 = 20.0
		self.blood_containing_modeltypes = {
			"BloodVessel",
			"HeartChamber",
			"BloodCapacitance",
			"BloodTimeVaryingElastance",
			"BloodPump",
			"MicroVascularUnit",
			"blood_vessel",
			"heart_chamber",
			"blood_capacitance",
			"blood_time_varying_elastance",
			"pump",
			"micro_vascular_unit",
		}

		self.preductal_art_bloodgas = {}
		self.art_bloodgas = {}
		self.ven_bloodgas = {}
		self.art_solutes = {}

		self._update_interval = 1.0
		self._update_counter = 0.0
		self._ascending_aorta = None
		self._descending_aorta = None
		self._right_atrium = None

	def _get_models_registry(self):
		"""Return active model registry dictionary if available."""
		if isinstance(self.model_ref, dict):
			return self.model_ref

		model_engine = getattr(self, "_model_engine", None)
		if model_engine is not None:
			models = getattr(model_engine, "models", None)
			if isinstance(models, dict):
				return models

		return None

	def _resolve_model(self, model_name):
		"""Resolve a model name from the active registry."""
		models = self._get_models_registry()
		if models is None:
			return None
		return models.get(model_name)

	def init_model(self, args=None):
		"""Initialize blood-capable models with baseline blood properties."""
		super().init_model(args)

		models = self._get_models_registry()
		if models is None:
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) not in self.blood_containing_modeltypes:
				continue

			model_to2 = float(getattr(model, "to2", 0.0) or 0.0)
			model_tco2 = float(getattr(model, "tco2", 0.0) or 0.0)
			if model_to2 == 0.0 and model_tco2 == 0.0:
				model.to2 = self.to2
				model.tco2 = self.tco2
				model.solutes = dict(self.solutes)
				model.temp = self.temp
				model.viscosity = self.viscosity

		self._ascending_aorta = models.get("AA")
		self._descending_aorta = models.get("AD")
		self._right_atrium = models.get("RA")

		self.art_solutes = dict(self.solutes)

	def calc_model(self):
		"""Periodically compute and publish arterial/venous blood-gas snapshots."""
		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		self._update_counter += time_step
		if self._update_counter < self._update_interval:
			return

		self._update_counter = 0.0

		if self._ascending_aorta is not None:
			calc_blood_composition(self._ascending_aorta)
			self.preductal_art_bloodgas = {
				"ph": self._ascending_aorta.ph,
				"pco2": self._ascending_aorta.pco2,
				"po2": self._ascending_aorta.po2,
				"hco3": self._ascending_aorta.hco3,
				"be": self._ascending_aorta.be,
				"so2": self._ascending_aorta.so2,
			}

		if self._descending_aorta is not None:
			calc_blood_composition(self._descending_aorta)
			self.art_bloodgas = {
				"ph": self._descending_aorta.ph,
				"pco2": self._descending_aorta.pco2,
				"po2": self._descending_aorta.po2,
				"hco3": self._descending_aorta.hco3,
				"be": self._descending_aorta.be,
				"so2": self._descending_aorta.so2,
			}
			self.art_solutes = dict(getattr(self._descending_aorta, "solutes", {}) or {})

		if self._right_atrium is not None:
			calc_blood_composition(self._right_atrium)
			self.ven_bloodgas = {
				"ph": self._right_atrium.ph,
				"pco2": self._right_atrium.pco2,
				"po2": self._right_atrium.po2,
				"hco3": self._right_atrium.hco3,
				"be": self._right_atrium.be,
				"so2": self._right_atrium.so2,
			}

		ivci = self._resolve_model("IVCI")
		if ivci is not None:
			calc_blood_composition(ivci)

		svc = self._resolve_model("SVC")
		if svc is not None:
			calc_blood_composition(svc)

	def set_temperature(self, new_temp, bc_site=""):
		"""Set blood temperature globally or for a specific blood compartment."""
		self.temp = float(new_temp)

		models = self._get_models_registry()
		if models is None:
			return

		if bc_site:
			model = models.get(bc_site)
			if model is not None:
				model.temp = self.temp
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.blood_containing_modeltypes:
				model.temp = self.temp

	def set_viscosity(self, new_viscosity):
		"""Set blood viscosity for all blood-containing models."""
		self.viscosity = float(new_viscosity)

		models = self._get_models_registry()
		if models is None:
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.blood_containing_modeltypes:
				model.viscosity = self.viscosity

	def set_to2(self, new_to2, bc_site=""):
		"""Set total oxygen content globally or for one blood compartment."""
		models = self._get_models_registry()
		if models is None:
			return

		value = float(new_to2)
		if bc_site:
			model = models.get(bc_site)
			if model is not None:
				model.to2 = value
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.blood_containing_modeltypes:
				model.to2 = value

	def set_tco2(self, new_tco2, bc_site=""):
		"""Set total carbon dioxide content globally or for one compartment."""
		models = self._get_models_registry()
		if models is None:
			return

		value = float(new_tco2)
		if bc_site:
			model = models.get(bc_site)
			if model is not None:
				model.tco2 = value
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.blood_containing_modeltypes:
				model.tco2 = value

	def set_solute(self, solute, solute_value, bc_site=""):
		"""Set a solute concentration globally or for one blood compartment."""
		models = self._get_models_registry()
		if models is None:
			return

		self.solutes[str(solute)] = float(solute_value)

		if bc_site:
			model = models.get(bc_site)
			if model is not None:
				model_solutes = getattr(model, "solutes", {}) or {}
				model_solutes[str(solute)] = float(solute_value)
				model.solutes = model_solutes
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.blood_containing_modeltypes:
				model.solutes = dict(self.solutes)
