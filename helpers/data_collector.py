class DataCollector:
	def __init__(self, model):
		self.model = model

		self.watch_list = []
		self.watch_list_slow = []

		self.sample_interval = 0.005
		self.sample_interval_slow = 1.0

		self._interval_counter = 0.0
		self._interval_counter_slow = 0.0

		self.modeling_stepsize = float(getattr(self.model, "modeling_stepsize", 0.0) or 0.0)

		heart_model = getattr(self.model, "models", {}).get("Heart") if hasattr(self.model, "models") else None
		self.ncc_ventricular = {
			"label": "Heart.ncc_ventricular",
			"model": heart_model,
			"prop1": "ncc_ventricular",
			"prop2": None,
		}
		self.ncc_atrial = {
			"label": "Heart.ncc_atrial",
			"model": heart_model,
			"prop1": "ncc_atrial",
			"prop2": None,
		}

		self.watch_list.append(self.ncc_atrial)
		self.watch_list.append(self.ncc_ventricular)

		self.collected_data = []
		self.collected_data_slow = []

	def clear_data(self):
		self.collected_data = []

	def clear_data_slow(self):
		self.collected_data_slow = []

	def clear_watchlist(self):
		self.clear_data()
		self.watch_list = [self.ncc_atrial, self.ncc_ventricular]

	def clear_watchlist_slow(self):
		self.clear_data_slow()
		self.watch_list_slow = []

	def get_model_data(self):
		data = list(self.collected_data)
		self.collected_data = []
		return data

	def get_model_data_slow(self):
		data = list(self.collected_data_slow)
		self.collected_data_slow = []
		return data

	def set_sample_interval(self, new_interval=0.005):
		self.sample_interval = float(new_interval)

	def set_sample_interval_slow(self, new_interval=0.005):
		self.sample_interval_slow = float(new_interval)

	def add_to_watchlist(self, properties):
		success = True
		self.clear_data()

		if isinstance(properties, str):
			properties = [properties]

		for prop in properties:
			duplicate = any(item.get("label") == prop for item in self.watch_list)
			if duplicate:
				continue

			processed_prop = self._find_model_prop(prop)
			if processed_prop is not None:
				self.watch_list.append(processed_prop)
			else:
				success = False

		return success

	def add_to_watchlist_slow(self, properties):
		success = True
		self.clear_data_slow()

		if isinstance(properties, str):
			properties = [properties]

		for prop in properties:
			duplicate = any(item.get("label") == prop for item in self.watch_list_slow)
			if duplicate:
				continue

			processed_prop = self._find_model_prop(prop)
			if processed_prop is not None:
				self.watch_list_slow.append(processed_prop)
			else:
				success = False

		return success

	def clean_up(self):
		self.watch_list = [
			item
			for item in self.watch_list
			if item.get("model") is not None and bool(getattr(item.get("model"), "is_enabled", False))
		]

	def clean_up_slow(self):
		self.watch_list_slow = [
			item
			for item in self.watch_list_slow
			if item.get("model") is not None and bool(getattr(item.get("model"), "is_enabled", False))
		]

	def collect_data(self, model_clock):
		if self._interval_counter >= self.sample_interval:
			self._interval_counter = 0.0
			data_object = {"time": round(float(model_clock), 4)}

			for parameter in self.watch_list:
				model = parameter.get("model")
				if model is None or not bool(getattr(model, "is_enabled", False)):
					continue

				value = getattr(model, parameter.get("prop1"), 0)
				prop2 = parameter.get("prop2")
				if prop2 is not None:
					if isinstance(value, dict):
						value = value.get(prop2, 0)
					else:
						value = getattr(value, prop2, 0)

				data_object[parameter.get("label")] = value

			self.collected_data.append(data_object)

		if self._interval_counter_slow >= self.sample_interval_slow:
			self._interval_counter_slow = 0.0
			data_object_slow = {"time": round(float(model_clock), 4)}

			for parameter in self.watch_list_slow:
				model = parameter.get("model")
				if model is None:
					continue

				value = getattr(model, parameter.get("prop1"), 0)
				prop2 = parameter.get("prop2")
				if prop2 is not None:
					if isinstance(value, dict):
						value = value.get(prop2, 0)
					else:
						value = getattr(value, prop2, 0)

				data_object_slow[parameter.get("label")] = value

			self.collected_data_slow.append(data_object_slow)

		self._interval_counter += self.modeling_stepsize
		self._interval_counter_slow += self.modeling_stepsize

	def _find_model_prop(self, prop):
		tokens = str(prop).split(".")
		if len(tokens) not in (2, 3):
			return None

		model_name = tokens[0]
		prop1 = tokens[1]
		prop2 = tokens[2] if len(tokens) == 3 else None

		models = getattr(self.model, "models", {})
		if model_name not in models:
			return None

		model = models[model_name]
		if not hasattr(model, prop1):
			return None

		result = {
			"label": prop,
			"model": model,
			"prop1": prop1,
			"prop2": prop2,
		}
		if prop2 is None:
			result["ref"] = getattr(model, prop1)
		return result


Datacollector = DataCollector
