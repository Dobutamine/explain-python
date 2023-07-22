import json
import time
import pickle
import importlib
from explain_core.helpers.DataCollector import DataCollector
from explain_core.helpers.TaskScheduler import TaskScheduler
from explain_core.base_models.BaseModel import BaseModel

# import the perfomance counter module to measure the model performance
from time import perf_counter


class ModelEngine:
    # define an object holding the entire model and submodels
    models: dict = {}

    # define an object holding the model properties of the current model
    model_definition: dict = {}
    model_definition_filename: str = ""

    # define an object holding the high resolution model data
    model_data: list = []

    # define an attribute holding the name of the model
    name: str = ""

    # define an attribute holding the description of the model
    description: str = ""

    # define an attribute holding the weight
    weight: float = 0.0

    # define an attribute holding the modeling stepsize
    modeling_stepsize: float = 0.0005

    # define an attribute holding the model time
    model_time_total: float = 0.0

    # define an obvject holding the  datacollector
    _datacollector: dict = {}

    # define an object holding the task scheduler
    _task_scheduler: dict = {}

    # performance
    run_duration: float = 0.0
    step_duration: float = 0.0

    # define local attributes
    initialized: bool = False

    # define a status message object
    status = {
        "log": [],
        "error_log": [],
        "initialized": False
    }

    # define the constructor
    def __init__(self, model_definition_filename: str):
        # initialize all model components with the parameters from the JSON file
        self.initialized = self.init_model(model_definition_filename)

        # store the current model definition filename
        self.model_definition_filename = model_definition_filename

    def init_model(self, model_definition_filename: str):
        # set the error counter = 0
        error_counter = 0
        self.status = {
            "log": [],
            "error_log": [],
            "initialized": False
        }

        # make sure the objects are empty
        self.models: dict = {}
        self.model_data: list = []
        self._datacollector: dict = {}
        self._task_scheduler: dict = {}
        self.initialized = False

        # try to open the json file
        try:
            # open the json file
            json_file = open(model_definition_filename)

            # convert the json file to a python dictionary
            self.model_definition = json.load(json_file)

            # get the model attributes
            self.name = self.model_definition['name']
            self.description = self.model_definition['description']
            self.weight = self.model_definition['weight']
            self.modeling_stepsize = self.model_definition['modeling_stepsize']
            self.model_time_total = self.model_definition['model_time_total']

        except:
            # signal that the json file failed to load
            self.status["error_log"].append(
                f"The JSON model definition file: {model_definition_filename} failed to load or can not be found!")
            self.initialized = False

            # terminate function
            return

        # initialize all model components and put a reference to them in the components list
        for key, model in self.model_definition['models'].items():
            # try to find the desired model class from the core_models or custom_models folder
            model_type = model["model_type"]

            # try to import the module holding the model class from the core_models folder
            try:
                model_module = importlib.import_module(
                    'explain_core.core_models.' + model_type)
            except:
                try:
                    # try to import the module holding the model class from the custom models folder
                    model_module = importlib.import_module(
                        'explain_core.custom_models.' + model_type)
                except:
                    self.status["error_log"].append(
                        f"Load error: {model_type} model not found OR the model has a syntax error. Error {error}")
                    error_counter += 1

            else:
                # get the model class from the module
                model_class = getattr(model_module, model_type)

                # instantiate the model class with the properties stored in the model_definition file and a reference to the other components and add it to the components dictionary
                try:
                    self.models[model['name']] = model_class(**model)
                except Exception as error:
                    # a module holding the desired model class is producing an error while instantiating
                    self.status["error_log"].append(
                        f"Instantiation error: {model_type} model failed to instantiate. Error: {error}")
                    error_counter += 1

        # initialize a datacollector
        self._datacollector = DataCollector(self)

        # initialize a task scheduler
        self._task_scheduler = TaskScheduler(self)

        # check the dependencies
        dep_errors: int = self.check_dependencies()

        # initialize all the models
        if (error_counter == 0):
            init_errors = 0
            # initialize all components
            for _, model in self.models.items():
                try:
                    model.init_model(self)
                except Exception as error:
                    # a module holding the desired model class is producing an error while initiallizing
                    self.status["error_log"].append(
                        f"Initialization error: {model.name}: {model.model_type} model failed to initialize with error: {error}")
                    init_errors += 1

            if init_errors > 0 or dep_errors > 0:
                self.initialized = False
            else:
                self.status["log"].append(
                    f" Model '{self.name}' loaded and initialized correctly.")
                self.initialized = True

        else:
            self.initialized = False

        self.status['initialized'] = self.initialized

    def check_dependencies(self) -> int:
        dep_errors = 0
        # iterate over all models
        for _, model in self.models.items():
            # iterate over the dependencies
            for dep in model.dependencies:
                # check if dependeny is in the models dictionary
                present = False
                for _, dep_model in self.models.items():
                    if dep_model.name == dep:
                        present = True
                if not present:
                    self.status["error_log"].append(
                        f'Dependency error: model {model.name} depends on {dep} which is not present.')
                    dep_errors += 1
        if dep_errors > 0:
            self.initialized = False
        return dep_errors

    def calculate_perf(self, time_to_calculate: float = 1.0):
        # this routine will quickly calculate a model run but the caller needs to take care of
        # all data processing and cleanup of the datacollector as the data stays in the data collector
        # and the data collector watchlist will not be reset
        # this routine is especially suitable for realtime running model applications

        # Cache the attributes for faster access during the model loop
        collect_data = self._datacollector.collect_data
        model_time_total = self.model_time_total
        modeling_stepsize = self.modeling_stepsize

        # Calculate the number of steps of the model
        no_of_steps: int = int(time_to_calculate / modeling_stepsize)

        # Do all model steps
        for _ in range(no_of_steps):
            # Execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # Call the data collector
            collect_data(model_time_total)

            # Increase the model clock
            model_time_total += modeling_stepsize

    def calculate(self, time_to_calculate: float = 10.0, performance: bool = True) -> list:
        # Calculate the number of steps of the model
        no_of_steps: int = int(time_to_calculate / self.modeling_stepsize)

        # reset the data collector
        self._datacollector.clear_data()

        # Start the performance counter
        if performance:
            perf_start = perf_counter()

        # Cache the attributes for faster access during the model loop
        collect_data = self._datacollector.collect_data
        model_time_total = self.model_time_total
        modeling_stepsize = self.modeling_stepsize

        # Do all model steps
        for _ in range(no_of_steps):
            # Execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # Call the data collector
            collect_data(model_time_total)

            # Increase the model clock
            model_time_total += modeling_stepsize

        # Stop the performance counter
        if performance:
            # stop the performance counter
            perf_stop = perf_counter()

            # Store the performance metrics
            run_duration = perf_stop - perf_start
            step_duration = (run_duration / no_of_steps) * 1000
            print(
                f'Ready in {run_duration:.1f} sec. Average model step in {step_duration:.4f} ms.')

        # store a reference to the collected data in model_data and return it
        self.model_data = self._datacollector.collected_data
        return self.model_data

    def clear_watchlist(self):
        self._datacollector.clear_watchlist()

    def add_to_watchlist(self, properties: list):
        # make sure the properties object is of lilst type
        if isinstance(properties, str):
            properties = [properties]

        # add properties to watch list of the datacollector
        self._datacollector.add_to_watchlist(properties)

    def set_sample_interval(self, interval: float = 0.005):
        if interval > 0.0005:
            self._datacollector.set_sample_interval(interval)

    def set_property(self, property: str, new_value: float, in_time: float = 1.0, at_time: float = 0.0) -> bool:
        # define some placeholders
        m: BaseModel = None
        p1: str = None
        p2: str = None
        p3: str = None

        # build a task scheduler object
        t = property.split(".")

        if len(t) < 5 and len(t) > 1:
            if len(t) == 2:
                m = t[0]
                p1 = t[1]
            if len(t) == 3:
                m = t[0]
                p1 = t[1]
                p2 = t[2]
            if len(t) == 4:
                m = t[0]
                p1 = t[1]
                p2 = t[2]
                p3 = t[3]
        else:
            return False

        # define a task for the task scheduler
        task = {
            "model": self.models[m],
            "prop1": p1,
            "prop2": p2,
            "prop3": p3,
            "new_value": new_value,
            "in_time": in_time,
            "at_time": at_time
        }

        # pass the task to the scheduler
        self._task_scheduler.add_task(task)

        return True

    def get_property(self, property: str):
        # declare an object to hold the values
        processed_prop = self._find_model_prop(property)
        prop1 = processed_prop['prop1']
        prop2 = processed_prop.get('prop2')
        value = getattr(processed_prop['model'], prop1)
        if prop2 is not None:
            value = value.get(prop2, 0)
        return value

    def inspect_model(self, property=None):
        inspect = {}
        for component_name, component in self.models.items():
            if property is None:
                inspect[component_name] = self.inspect_model_component(
                    component_name)
            else:
                try:
                    inspect[component_name] = self.inspect_model_component(
                        component_name)[property]
                except:
                    pass

        return inspect

    def inspect_model_component(self, model_component):
        content = {}
        for attribute in dir(self.models[model_component]):
            if not attribute.startswith('__'):
                attr_type = type(
                    getattr(self.models[model_component], attribute))
                if (attr_type is str) or (attr_type is float) or (attr_type is bool) or (attr_type is int):
                    content[attribute] = getattr(
                        self.models[model_component], attribute)
        return content

    def enable_model_component(self, model_component):
        self.model[model_component].is_enabled = True

    def disable_model_component(self, model_component):
        self.model[model_component].is_enabled = False

    def save_model_state(self, filename):
        # use the binary mode 'wb' to save the model engine in this current state
        filename += ".xpl"
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    def load_model_state(self, filename):
        # use the binary mode 'rb' to load a model engine state
        with open(filename, "rb") as file:
            return pickle.load(file)

    def restart_model(self):
        self.initialized = self.init_model(self.model_definition_filename)

    def _find_model_prop(self, prop):
        # split the model from the prop
        t = prop.split(sep=".")

        # if only 1 property is present
        if (len(t) == 2):
            # try to find the parameter in the model
            if t[0] in self.models:
                if (hasattr(self.models[t[0]], t[1])):
                    return {'label': prop, 'model': self.models[t[0]], 'prop1': t[1], 'prop2': None}

        # if 2 properties are present
        if (len(t) == 3):
            # try to find the parameter in the model
            if t[0] in self.models:
                if (hasattr(self.models[t[0]], t[1])):
                    return {'label': prop, 'model': self.models[t[0]], 'prop1': t[1], 'prop2': t[2]}

        return None
