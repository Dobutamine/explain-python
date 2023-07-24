import math


class TaskScheduler:
    # local parameters
    _model = {}
    _t = 0.0005
    _is_initialized = False

    _tasks: dict = {}
    _task_interval: float = 1.0
    _task_interval_counter: float = 0.0

    def __init__(self, model):
        # store a reference to the model
        self._model = model

        # store the modeling stepsize for easy referencing
        self._t = model.modeling_stepsize

        # signal that the component has been initialized
        self._is_initialized = True

    def add_task(self, new_task):
        id = 'task_' + str(new_task['id'])
        del new_task['id']
        new_task['stepsize'] = 0.0
        new_task['running'] = False
        new_task['completed'] = False

        # get the current value
        current_value = getattr(new_task['model'], new_task['prop1'])
        if new_task['prop2'] is not None:
            current_value = current_value.get(new_task['prop2'])
        new_task['current_value'] = current_value

        # get the type of the current value
        if isinstance(current_value, float) or isinstance(current_value, int):
            new_task['type'] = 0
            # calculate the stepsize
            if new_task['in_time'] > 0:
                new_task['stepsize'] = (
                    new_task['new_value'] - current_value) / new_task['in_time']
            self._tasks[id] = new_task

        if isinstance(current_value, bool) or isinstance(current_value, str):
            new_task['type'] = 1
            # calculate the stepsize
            new_task['stepsize'] = 0.0
            self._tasks[id] = new_task

        print(self._tasks)

    def clear_task(self, task_id):
        pass

    def run_tasks(self, model_time_total):
        if self._task_interval_counter > self._task_interval:
            finished_tasks = []
            # reset the counter
            self._task_interval_counter = 0.0
            # run the tasks
            for id, task in self._tasks.items():
                # check if the task should be executed
                if task['at_time'] < self._task_interval:
                    task['at_time'] = 0
                    if task['type'] > 0:
                        task['current_value'] = task['new_value']
                        self._set_value(task)
                        task['completed'] = True
                        finished_tasks.append(id)
                        task['running'] = False
                else:
                    task['at_time'] -= self._task_interval

                # check whether the new value is already at the target value
                if task['type'] < 1:
                    if abs(task['current_value'] - task['new_value']) < abs(task['stepsize']):
                        task['current_value'] = task['new_value']
                        self._set_value(task)
                        task['stepsize'] = 0
                        task['completed'] = True
                        finished_tasks.append(id)
                        task['running'] = False
                    else:
                        task['current_value'] += task['stepsize']
                        self._set_value(task)

            for ft in finished_tasks:
                del self._tasks[ft]

        self._task_interval_counter += self._t

    def _set_value(self, task):
        if task['prop2'] is None:
            setattr(task['model'], task['prop1'], task['current_value'])
        else:
            p = getattr(task['model'], task['prop1'])
            p[task['prop2']] = task['current_value']
