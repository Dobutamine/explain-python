class DataCollector:
	"""Collects time-series snapshots from selected model properties."""

	def __init__(self, model):
		"""Initialize collector state, default watch items, and sample intervals."""
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
		"""Clear fast-sampled buffered data."""
		self.collected_data = []

	def clear_data_slow(self):
		"""Clear slow-sampled buffered data."""
		self.collected_data_slow = []

	def clear_watchlist(self):
		"""Reset fast watchlist to core cardiac cycle counters."""
		self.clear_data()
		self.watch_list = [self.ncc_atrial, self.ncc_ventricular]

	def clear_watchlist_slow(self):
		"""Reset slow watchlist to an empty set."""
		self.clear_data_slow()
		self.watch_list_slow = []

	def get_model_data(self):
		"""Return and clear buffered fast-sampled data."""
		data = list(self.collected_data)
		self.collected_data = []
		return data

	def get_model_data_slow(self):
		"""Return and clear buffered slow-sampled data."""
		data = list(self.collected_data_slow)
		self.collected_data_slow = []
		return data

	def set_sample_interval(self, new_interval=0.005):
		"""Set fast sampling interval in seconds."""
		self.sample_interval = float(new_interval)

	def set_sample_interval_slow(self, new_interval=0.005):
		"""Set slow sampling interval in seconds."""
		self.sample_interval_slow = float(new_interval)

	def add_to_watchlist(self, properties):
		"""Add one or more property paths to the fast watchlist."""
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
		"""Add one or more property paths to the slow watchlist."""
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
		"""Remove disabled or unresolved entries from the fast watchlist."""
		self.watch_list = [
			item
			for item in self.watch_list
			if item.get("model") is not None and bool(getattr(item.get("model"), "is_enabled", False))
		]

	def clean_up_slow(self):
		"""Remove disabled or unresolved entries from the slow watchlist."""
		self.watch_list_slow = [
			item
			for item in self.watch_list_slow
			if item.get("model") is not None and bool(getattr(item.get("model"), "is_enabled", False))
		]

	def collect_data(self, model_clock):
		"""Sample watched properties at configured intervals and buffer records."""
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
		"""Resolve a dotted property path into a watchlist descriptor."""
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
