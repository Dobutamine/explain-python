import math

from base_models.base_model import BaseModel


class DuctusArteriosus(BaseModel):
	model_type = "pda"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.diameter_ao = 4.0
		self.diameter_pa = 2.0
		self.diameter_max = 5.0
		self.length = 20.0
		self.type = "conical"
		self.el_min = 30000.0
		self.el_max = 150000.0
		self.viscosity = 6.0

		self.flow = 0.0
		self.vol = 0.0
		self.velocity = 0.0
		self.flow_ao = 0.0
		self.flow_pa = 0.0
		self.velocity_ao = 0.0
		self.velocity_pa = 0.0
		self.res_ao = 1500.0
		self.res_pa = 1500.0
		self.el = 40000.0

		self._da = None
		self._aar_da = None
		self._da_pa = None

	def _resolve_model(self, model_name):
		if not model_name:
			return None

		if isinstance(self.model_ref, dict):
			return self.model_ref.get(model_name)

		model_engine = getattr(self, "_model_engine", None)
		if model_engine is not None:
			models = getattr(model_engine, "models", None)
			if isinstance(models, dict):
				return models.get(model_name)

		return None

	def calc_model(self):
		self._aar_da = self._resolve_model("AAR_DA")
		self._da = self._resolve_model("DA")
		self._da_pa = self._resolve_model("DA_PA")

		if self._aar_da is None or self._da is None or self._da_pa is None:
			return

		self.flow_ao = float(getattr(self._aar_da, "flow", 0.0) or 0.0)
		self.flow_pa = float(getattr(self._da_pa, "flow", 0.0) or 0.0)
		self.viscosity = float(getattr(self._da, "viscosity", self.viscosity) or self.viscosity)

		self._da.el_base = self.el_min

		self.diameter_ao = min(float(self.diameter_ao), float(self.diameter_max))
		self.diameter_pa = min(float(self.diameter_pa), float(self.diameter_max))

		self._aar_da.no_flow = self.diameter_ao == 0.0
		self._da_pa.no_flow = self.diameter_pa == 0.0

		segment_length = float(self.length) / 2.0
		self.res_ao = self.calc_resistance(self.diameter_ao, segment_length, self.viscosity)
		self.res_pa = self.calc_resistance(self.diameter_pa, segment_length, self.viscosity)

		self._aar_da.r_for = self.res_ao
		self._aar_da.r_back = self.res_ao
		self._da_pa.r_for = self.res_pa
		self._da_pa.r_back = self.res_pa

		if self.diameter_max > 0.0:
			self.el = self.el_min + (self.el_max - self.el_min) * (self.diameter_pa / self.diameter_max)
		else:
			self.el = self.el_max

		area_ao = math.pi * math.pow((self.diameter_ao * 0.001) / 2.0, 2.0)
		area_pa = math.pi * math.pow((self.diameter_pa * 0.001) / 2.0, 2.0)

		self.velocity_ao = ((self.flow_ao * 0.001) / area_ao) if area_ao > 0.0 else 0.0
		self.velocity_pa = ((self.flow_pa * 0.001) / area_pa) if area_pa > 0.0 else 0.0

		self.vol = float(getattr(self._da, "vol", 0.0) or 0.0)

	def set_diameter(self, new_diameter):
		new_value = float(new_diameter)
		self.diameter_ao = new_value
		self.diameter_pa = new_value

	def calc_closure(self):
		pass

	def calc_resistance(self, diameter, length=20.0, viscosity=6.0):
		diameter = float(diameter)
		length = float(length)
		viscosity = float(viscosity)

		if diameter > 0.0 and length > 0.0:
			n_pas = viscosity / 1000.0
			length_meters = length / 1000.0
			radius_meters = (diameter / 2.0) / 1000.0

			resistance = (8.0 * n_pas * length_meters) / (math.pi * math.pow(radius_meters, 4))
			resistance = resistance * 0.00000750062
			return resistance

		return 100000000.0
