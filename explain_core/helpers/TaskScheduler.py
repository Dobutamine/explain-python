class TaskScheduler:
    # local parameters
    _model = {}
    _t = 0.0005
    _is_initialized = False

    _tasks: list = []
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
            # calculate the stepsize
            if new_task['in_time'] > 0:
                new_task['stepsize'] = (
                    new_task['new_value'] - current_value) / new_task['in_time']
            self._tasks.append(new_task)

        if isinstance(current_value, bool) or isinstance(current_value, str):
            # calculate the stepsize
            new_task['stepsize'] = 0.0
            self._tasks.append(new_task)

    def clear_task(self, task_id):
        pass

    def run_tasks(self, model_time_total):
        if self._task_interval > self._task_interval_counter:
            # reset the counter
            self._task_interval = 0.0
            # run the tasks
            for task in self._tasks:
                print(task)

        self._task_interval += self._t
