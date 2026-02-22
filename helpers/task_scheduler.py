import random


class TaskScheduler:
	def __init__(self, model_ref):
		self._model_engine = model_ref
		self._t = float(getattr(model_ref, "modeling_stepsize", 0.0) or 0.0)
		self._is_initialized = False
		self.is_enabled = True

		self._tasks = {}
		self._task_interval = 0.015
		self._task_interval_counter = 0.0

	def _new_task_id(self):
		while True:
			task_id = f"task_{random.randint(0, 9999)}"
			if task_id not in self._tasks:
				return task_id

	def add_function_call(self, new_function_call):
		task = dict(new_function_call)
		id_ = self._new_task_id()

		task["id"] = id_
		task["running"] = False
		task["completed"] = False
		task["type"] = 2
		task["stepsize"] = 0.0

		func_ref = str(task.get("func", ""))
		result = func_ref.split(".")
		if len(result) != 2:
			raise ValueError("Function call must be in the format 'MODEL.func'")

		model = self._model_engine.models[result[0]]
		task["model"] = model
		task["func"] = getattr(model, result[1])
		task.setdefault("args", [])
		task.setdefault("at", 0.0)

		self._tasks[id_] = task

	def add_task(self, new_task):
		task = dict(new_task)
		id_ = self._new_task_id()

		task["id"] = id_
		task["running"] = False
		task["completed"] = False
		task.setdefault("prop2", None)
		task.setdefault("at", 0.0)
		task.setdefault("it", 0.0)

		model_name = task.get("model")
		task["model"] = self._model_engine.models[model_name]

		current_value = getattr(task["model"], task["prop1"])
		if task["prop2"] is not None:
			if isinstance(current_value, dict):
				current_value = current_value[task["prop2"]]
			else:
				current_value = getattr(current_value, task["prop2"])

		task["current_value"] = current_value

		if isinstance(current_value, (int, float)) and not isinstance(current_value, bool):
			task["type"] = 0
		elif isinstance(current_value, (bool, str)):
			task["type"] = 1
		else:
			task["type"] = 1

		if task["it"] > 0 and task["type"] == 0:
			stepsize = (task["t"] - current_value) / (task["it"] / self._task_interval)
			task["stepsize"] = stepsize
			if stepsize != 0.0:
				self._tasks[id_] = task
		else:
			task["type"] = 1 if task["type"] != 2 else task["type"]
			task["stepsize"] = 0.0
			self._tasks[id_] = task

		if task["type"] > 0:
			task["stepsize"] = 0.0
			self._tasks[id_] = task

	def remove_task(self, task_id):
		id_ = f"task_{task_id}"
		if id_ in self._tasks:
			del self._tasks[id_]
			return True
		return False

	def remove_all_tasks(self):
		self._tasks = {}

	def run_tasks(self):
		if self._task_interval_counter > self._task_interval:
			finished_tasks = []
			self._task_interval_counter = 0.0

			for id_, task in list(self._tasks.items()):
				if task["at"] < self._task_interval and not task["running"]:
					task["at"] = 0.0

					if task["type"] == 0:
						task["running"] = True
					elif task["type"] == 1:
						task["current_value"] = task["t"]
						self._set_value(task)
						task["completed"] = True
						finished_tasks.append(id_)
					elif task["type"] == 2:
						task["func"](*task.get("args", []))
						task["completed"] = True
						finished_tasks.append(id_)
				else:
					task["at"] -= self._task_interval

				if task["type"] < 1 and task["running"]:
					if abs(task["current_value"] - task["t"]) < abs(task["stepsize"]):
						task["current_value"] = task["t"]
						self._set_value(task)
						task["stepsize"] = 0.0
						task["completed"] = True
						finished_tasks.append(id_)
					else:
						task["current_value"] += task["stepsize"]
						self._set_value(task)

			for finished_id in finished_tasks:
				self._tasks.pop(finished_id, None)

		if self.is_enabled:
			self._task_interval_counter += self._t

	def _set_value(self, task):
		if task["prop2"] is None:
			setattr(task["model"], task["prop1"], task["current_value"])
			return

		target = getattr(task["model"], task["prop1"])
		if isinstance(target, dict):
			target[task["prop2"]] = task["current_value"]
		else:
			setattr(target, task["prop2"], task["current_value"])


Taskscheduler = TaskScheduler
