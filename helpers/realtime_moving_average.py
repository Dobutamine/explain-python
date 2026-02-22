class RealTimeMovingAverage:
	"""Fixed-window real-time moving average accumulator."""

	def __init__(self, window_size):
		"""Initialize moving-average buffer with a minimum window of 1."""
		self.window_size = max(int(window_size), 1)
		self.values = []
		self.sum = 0.0
		self.current_average = 0.0

	def add_value(self, new_value):
		"""Add a sample and return the updated moving average."""
		value = float(new_value)
		self.values.append(value)
		self.sum += value

		if len(self.values) > self.window_size:
			oldest_value = self.values.pop(0)
			self.sum -= oldest_value

		self.current_average = self.sum / len(self.values)
		return self.current_average

	def get_current_average(self):
		"""Return the current moving average value."""
		return self.current_average

	def reset(self):
		"""Clear buffered values and reset accumulator state."""
		self.values = []
		self.sum = 0.0
		self.current_average = 0.0

	# JS-style compatibility aliases
	def addValue(self, newValue):
		"""Compatibility alias for `add_value`."""
		return self.add_value(newValue)

	def getCurrentAverage(self):
		"""Compatibility alias for `get_current_average`."""
		return self.get_current_average()
