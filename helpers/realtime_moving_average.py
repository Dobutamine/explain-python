class RealTimeMovingAverage:
	def __init__(self, window_size):
		self.window_size = max(int(window_size), 1)
		self.values = []
		self.sum = 0.0
		self.current_average = 0.0

	def add_value(self, new_value):
		value = float(new_value)
		self.values.append(value)
		self.sum += value

		if len(self.values) > self.window_size:
			oldest_value = self.values.pop(0)
			self.sum -= oldest_value

		self.current_average = self.sum / len(self.values)
		return self.current_average

	def get_current_average(self):
		return self.current_average

	def reset(self):
		self.values = []
		self.sum = 0.0
		self.current_average = 0.0

	# JS-style compatibility aliases
	def addValue(self, newValue):
		return self.add_value(newValue)

	def getCurrentAverage(self):
		return self.get_current_average()
