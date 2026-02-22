import math

from base_models.base_model import BaseModel


class Shunts(BaseModel):
	"""Septal shunt model (FO/VSD) with diameter-based resistance updates."""

	model_type = "shunts"

	def __init__(self, model_ref={}, name=None):
		"""Initialize shunt geometry, viscosity, and hemodynamic outputs."""
		super().__init__(model_ref=model_ref, name=name)

		self.diameter_fo = 2.0
		self.diameter_fo_max = 10.0
		self.diameter_vsd = 2.0
		self.diameter_vsd_max = 10.0

		self.atrial_septal_width = 3.0
		self.ventricular_septal_width = 5.0
		self.fo_lr_factor = 10.0
		self.viscosity = 6.0

		self.flow_fo = 0.0
		self.flow_vsd = 0.0
		self.velocity_fo = 0.0
		self.velocity_vsd = 0.0
		self.res_fo = 500.0
		self.res_vsd = 500.0

		self._fo = None
		self._vsd = None
		self._lv = None

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
		"""Update shunt resistances/velocities from current diameters and flows."""
		self._fo = self._resolve_model("FO")
		self._vsd = self._resolve_model("VSD")
		self._lv = self._resolve_model("LV")

		if self._fo is None or self._vsd is None:
			return

		if self._lv is not None:
			self.viscosity = float(getattr(self._lv, "viscosity", self.viscosity) or self.viscosity)

		self.diameter_fo = min(float(self.diameter_fo), float(self.diameter_fo_max))
		self.diameter_vsd = min(float(self.diameter_vsd), float(self.diameter_vsd_max))

		self._fo.no_flow = self.diameter_fo == 0.0
		self._vsd.no_flow = self.diameter_vsd == 0.0

		self.res_fo = self.calc_resistance(self.diameter_fo, self.atrial_septal_width, self.viscosity)
		self.res_vsd = self.calc_resistance(self.diameter_vsd, self.ventricular_septal_width, self.viscosity)

		self._fo.r_for = self.res_fo * float(self.fo_lr_factor)
		self._fo.r_back = self.res_fo
		self._vsd.r_for = self.res_vsd
		self._vsd.r_back = self.res_vsd

		self.flow_fo = float(getattr(self._fo, "flow", 0.0) or 0.0)
		self.flow_vsd = float(getattr(self._vsd, "flow", 0.0) or 0.0)

		area_fo = math.pi * math.pow((self.diameter_fo * 0.001) / 2.0, 2.0)
		area_vsd = math.pi * math.pow((self.diameter_vsd * 0.001) / 2.0, 2.0)

		self.velocity_fo = ((self.flow_fo * 0.001) / area_fo) if area_fo > 0.0 else 0.0
		self.velocity_vsd = ((self.flow_vsd * 0.001) / area_vsd) if area_vsd > 0.0 else 0.0

	def calc_resistance(self, diameter, length=2.0, viscosity=6.0):
		"""Return Poiseuille-based resistance estimate for shunt pathway."""
		diameter = float(diameter)
		length = float(length)
		viscosity = float(viscosity)

		if diameter > 0.0 and length > 0.0:
			n_pas = viscosity / 1000.0
			length_meters = length / 1000.0
			radius_meters = (diameter / 2.0) / 1000.0
			resistance = (8.0 * n_pas * length_meters) / (math.pi * math.pow(radius_meters, 4))
			return resistance * 0.00000750062

		return 100000000.0
