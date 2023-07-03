import json
import importlib
from explain_core.helpers.DataCollector import DataCollector
from explain_core.helpers.TaskScheduler import TaskScheduler


class ModelEngine:
    # define an object holding the entire model and submodels
    models = {}

    # define an object holding the model engine properties
    model_engine = {}

    # define an object holding the model properties of the current model
    model_definition = {}

    # define an object holding the high resolution model data
    model_data = {}

    # define an object holding the low resolution model data
    model_data_slow = {}

    # define an attribute holding the name of the model
    name = ""

    # define an attribute holding the description of the model
    description = ""

    # define an attribute holding the weight
    weight = 0.0

    # define an attribute holding the modeling stepsize
    modeling_stepsize = 0.0005

    # define an attribute holding the model time
    model_time_total = 0.0

    # define an obvject holding the  datacollector
    datacollector = {}

    # define an object holding the task scheduler
    task_scheduler = {}

    # define local attributes
    _initialized = False

    # define the constructor
    def __init__(self, model_definition_filename: str):
        # initialize all model components with the parameters from the JSON file
        self.initialized = self.init_model(model_definition_filename)

    def init_model(self, model_definition_filename: str):
        # set the error counter = 0
        error_counter = 0

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
            print(
                f"The JSON model definition file: {model_definition_filename} failed to load or can not be found!")
            self._initialized = False

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
                        'custom_models.' + model_type)
                except:
                    # a module holding the desired model class is not found in the core_models or custom_models folder
                    print(
                        f"Load error: {model_type} model not found in the core_models nor in the custom_models folder.")
                    error_counter += 1
            else:
                # get the model class from the module
                model_class = getattr(model_module, model_type)

                # instantiate the model class with the properties stored in the model_definition file and a reference to the other components and add it to the components dictionary
                try:
                    self.models[key] = model_class(**model)
                except:
                    # a module holding the desired model class is producing an error while instantiating
                    print(
                        f"Instantiation error: {model_type} model failed to instantiate.")
                    error_counter += 1

        # initialize a datacollector
        self.datacollector = DataCollector(self)

        # check the dependencies
        self.check_dependencies()

        # initialize all the models
        if (error_counter == 0):
            init_errors = 0
            # initialize all components
            for _, model in self.models.items():
                try:
                    model.init_model(self)
                except:
                    # a module holding the desired model class is producing an error while initiallizing
                    print(
                        f"Initialization error: {model_type} model failed to initialize.")
                    init_errors += 1

            if init_errors > 0:
                self._initialized = False
            else:
                print(f"{self.name} model loaded and initialized correctly.")
                self._initialized = True

        else:
            self._initialized = False

        if not self._initialized:
            print("")
            print(f"The '{self.name}' model failed to run.")

    def check_dependencies(self):
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
                    print(
                        f'Dependency error: model {model.Name} depends on {dep} which is not present.')
                    dep_errors += 1
        if dep_errors > 0:
            self._initialized = False

    def start(self):
        # start the realtime model
        pass

    def stop(self):
        # stop the realtime model
        pass

    def calculate(self, time_to_calculate=10.0):
        pass

    def model_step(self):
        pass

    def rt_model_step(self):
        pass

    def print_performance(self, perf):
        pass
