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
