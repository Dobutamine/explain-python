import json
import time
import importlib
from explain_core.helpers.DataCollector import DataCollector

# import the perfomance counter module to measure the model performance
from time import perf_counter


class ModelEngine:
    # define an object holding the entire model and submodels
    models: dict = {}

    # define an object holding the model properties of the current model
    model_definition: dict = {}

    # define an object holding the high resolution model data
    model_data: dict = {}

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

    def init_model(self, model_definition_filename: str):
        # set the error counter = 0
        error_counter = 0
        self.status = {
            "log": [],
            "error_log": [],
            "initialized": False
        }

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

    def calculate(self, time_to_calculate: float = 10.0, performance: bool = True) -> list:
        # Calculate the number of steps of the model
        _no_of_steps: int = int(time_to_calculate / self.modeling_stepsize)

        # reset the data collector
        self._datacollector.clear_data()

        # Start the performance counter
        if performance:
            perf_start: float = perf_counter()

        # Do all model steps
        for _ in range(_no_of_steps):
            # Execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # Call the datacollector
            self._datacollector.collect_data(self.model_time_total)

            # Increase the model clock
            self.model_time_total += self.modeling_stepsize

        # Stop the performance counter
        if performance:
            # stop the performance counter
            perf_stop: float = perf_counter()

            # Store the performance metrics
            self.run_duration: float = perf_stop - perf_start
            self.step_duration: float = (
                self.run_duration / _no_of_steps) * 1000

        # store a reference to the collected data in model_data and return it
        self.model_data = self._datacollector.collected_data
        return self.model_data
