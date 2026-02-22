from base_models.base_model import BaseModel
from functions.gas_composition import calc_gas_composition


class Gas(BaseModel):
	model_type = "gas"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.pres_atm = 760.0
		self.fio2 = 0.21
		self.temp = 20.0
		self.humidity = 0.5
		self.humidity_settings = {}
		self.temp_settings = {}

		self.gas_containing_modeltypes = ["GasCapacitance", "gas_capacitance"]

	def init_model(self, args=None):
		super().init_model(args)

		models = self._get_models_registry()
		if models is None:
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.gas_containing_modeltypes:
				model.pres_atm = self.pres_atm
				model.temp = self.temp
				model.target_temp = self.temp

		for model_name, temp in self.temp_settings.items():
			model = models.get(model_name)
			if model is None:
				continue
			model.temp = temp
			model.target_temp = temp

		for model_name, humidity in self.humidity_settings.items():
			model = models.get(model_name)
			if model is None:
				continue
			model.humidity = humidity

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.gas_containing_modeltypes:
				calc_gas_composition(model, self.fio2, model.temp, model.humidity)

	def calc_model(self):
		return

	def _get_models_registry(self):
		if isinstance(self.model_ref, dict):
			return self.model_ref

		model_engine = getattr(self, "_model_engine", None)
		if model_engine is not None:
			models = getattr(model_engine, "models", None)
			if isinstance(models, dict):
				return models

		return None

	def set_atmospheric_pressure(self, new_pres_atm):
		self.pres_atm = float(new_pres_atm)

		models = self._get_models_registry()
		if models is None:
			return

		for model in models.values():
			if str(getattr(model, "model_type", "")) in self.gas_containing_modeltypes:
				model.pres_atm = self.pres_atm

	def set_temperature(self, new_temp, sites=None):
		if sites is None:
			sites = ["OUT", "MOUTH"]
		if not isinstance(sites, (list, tuple)):
			sites = [sites]

		parsed_temp = float(new_temp)
		for site in sites:
			self.temp_settings[str(site)] = parsed_temp

		models = self._get_models_registry()
		if models is None:
			return

		for model_name, temp in self.temp_settings.items():
			model = models.get(model_name)
			if model is None:
				continue
			model.temp = temp
			model.target_temp = temp

	def set_humidity(self, new_humidity, sites=None):
		if sites is None:
			sites = ["OUT", "MOUTH"]
		if not isinstance(sites, (list, tuple)):
			sites = [sites]

		parsed_humidity = float(new_humidity)
		for site in sites:
			self.humidity_settings[str(site)] = parsed_humidity

		models = self._get_models_registry()
		if models is None:
			return

		for model_name, humidity in self.humidity_settings.items():
			model = models.get(model_name)
			if model is None:
				continue
			model.humidity = humidity

	def set_fio2(self, new_fio2, sites=None):
		self.fio2 = float(new_fio2)

		if sites is None:
			sites = ["OUT", "MOUTH"]
		if not isinstance(sites, (list, tuple)):
			sites = [sites]

		models = self._get_models_registry()
		if models is None:
			return

		for site in sites:
			model = models.get(str(site))
			if model is None:
				continue
			calc_gas_composition(model, self.fio2, model.temp, model.humidity)
