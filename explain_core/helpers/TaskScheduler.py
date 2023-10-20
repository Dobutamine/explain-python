import math


class TaskScheduler:
    # local parameters
    is_enabled = True
    _model = {}
    _t = 0.0005
    _is_initialized = False

    _tasks: dict = {}
    _task_interval: float = 0.015
    _task_interval_counter: float = 0.0

    def __init__(self, model):
        # store a reference to the model
        self._model = model

        # store the modeling stepsize for easy referencing
        self._t = model.modeling_stepsize

        # signal that the component has been initialized
        self._is_initialized = True

    def add_task(self, new_task):
        id = "task_" + str(new_task["id"])
        del new_task["id"]
        new_task["stepsize"] = 0.0
        new_task["running"] = False
        new_task["completed"] = False

        current_value = getattr(new_task["model"], new_task["prop1"])
        if new_task["prop2"] is not None:
            current_value = current_value.get(new_task["prop2"])
        new_task["current_value"] = current_value

        if isinstance(current_value, float) or isinstance(current_value, int):
            new_task["type"] = 0

        if isinstance(current_value, bool) or isinstance(current_value, str):
            new_task["type"] = 1

        self._tasks[id] = new_task

    def configure_task(self, new_task):
        # get the current value
        current_value = getattr(new_task["model"], new_task["prop1"])
        if new_task["prop2"] is not None:
            current_value = current_value.get(new_task["prop2"])
        new_task["current_value"] = current_value

        # get the type of the current value
        if new_task["type"] < 1:
            # calculate the stepsize
            if new_task["in_time"] > 0:
                new_task["stepsize"] = (new_task["new_value"] - current_value) / (
                    new_task["in_time"] / self._task_interval
                )
            else:
                new_task["type"] = 1
                new_task["stepsize"] = 0.0

        if new_task["type"] > 0:
            # calculate the stepsize
            new_task["stepsize"] = 0.0

    def remove_task(self, task_id) -> bool:
        if task_id in self._tasks.keys():
            del self._tasks[task_id]
            return True

        return False

    def remove_all_tasks(self):
        self._tasks = []

    def get_all_tasks(self):
        return self._tasks

    def pause_all_tasks(self):
        self.is_enabled = False

    def restart_all_tasks(self):
        self.is_enabled = True

    def run_tasks(self, model_time_total):
        if self._task_interval_counter > self._task_interval:
            finished_tasks = []
            # reset the counter
            self._task_interval_counter = 0.0
            # run the tasks
            for id, task in self._tasks.items():
                # check if the task should be executed
                if task["at_time"] < self._task_interval and not task["running"]:
                    task["at_time"] = 0
                    # only do this for types which can not slowly change like booleans or strings
                    if task["type"] > 0:
                        task["current_value"] = task["new_value"]
                        self._set_value(task)
                        task["completed"] = True
                        finished_tasks.append(id)
                    else:
                        # calculate the stepsize and determine current value
                        self.configure_task(task)
                        # get the task running
                        task["running"] = True
                else:
                    # decrease the time at
                    task["at_time"] -= self._task_interval

                # check whether the new value is already at the target value
                if task["type"] < 1 and task["running"]:
                    if abs(task["current_value"] - task["new_value"]) < abs(
                        task["stepsize"]
                    ):
                        task["current_value"] = task["new_value"]
                        self._set_value(task)
                        task["stepsize"] = 0
                        task["completed"] = True
                        finished_tasks.append(id)
                    else:
                        task["current_value"] += task["stepsize"]
                        self._set_value(task)

            for ft in finished_tasks:
                del self._tasks[ft]

        if self.is_enabled:
            self._task_interval_counter += self._t

    def _set_value(self, task):
        if task["prop2"] is None:
            setattr(task["model"], task["prop1"], task["current_value"])
        else:
            p = getattr(task["model"], task["prop1"])
            p[task["prop2"]] = task["current_value"]
