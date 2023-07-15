import json
import multitimer
import time
import importlib
from explain_core.helpers.Interface import Interface

# import the perfomance counter module to measure the model performance
from time import perf_counter


class ModelEngine:
    # define an object holding the entire model and submodels
    models: dict = {}

    # define an object holding the model engine properties
    model_engine: dict = {}

    # define an object holding the model properties of the current model
    model_definition: dict = {}

    # define an object holding the high resolution model data
    model_data: dict = {}

    # define an object holding the low resolution model data
    model_data_slow: dict = {}

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
    datacollector: dict = {}

    # define an obvject holding the  datacollector
    interface: dict = {}

    # define an object holding the task scheduler
    task_scheduler: dict = {}

    # performance
    run_duration: float = 0.0
    step_duration: float = 0.0

    # define local attributes
    _initialized: bool = False

    # define a model timer object
    _model_timer = {}
    _model_rt_interval = 1.0

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
                        'explain_core.custom_models.' + model_type)
                except:
                    print(
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
                    print(
                        f"Instantiation error: {model_type} model failed to instantiate. Error: {error}")
                    error_counter += 1

        # initialize a datacollector
        self.interface = Interface(self)

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
                    print(
                        f"Initialization error: {model.name}: {model.model_type} model failed to initialize with error: {error}")
                    init_errors += 1

            if init_errors > 0 or dep_errors > 0:
                self._initialized = False
            else:
                print(f"{self.name} model loaded and initialized correctly.")
                self._initialized = True

        else:
            self._initialized = False

        if not self._initialized:
            print("")
            print(f"The '{self.name}' model failed to run.")

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
                    print(
                        f'Dependency error: model {model.name} depends on {dep} which is not present.')
                    dep_errors += 1
        if dep_errors > 0:
            self._initialized = False
        return dep_errors

    def start(self):
        # Create a Timer object to schedule the function execution
        self._model_timer = multitimer.MultiTimer(
            interval=self._model_rt_interval, function=self.model_step_rt)

        # Start the timer
        self._model_timer.start()

        print("Realtime model running.")

    def stop(self):
        # stop the realtime model
        self._model_timer.stop()
        print("Realtime model stopped.")

    def calculate(self, time_to_calculate: float = 10.0):
        # calculate a number of seconds of the model
        _no_of_steps: float = int(time_to_calculate / self.modeling_stepsize)

        # start the performance counter
        perf_start = perf_counter()

        # do all model steps
        for _ in range(_no_of_steps):
            # execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # call the user interface
            self.interface.step_model(self.model_time_total)

            # increase the model clock
            self.model_time_total += self.modeling_stepsize

        # stop the performance counter
        perf_stop = perf_counter()

        # store the performance metrics
        self.run_duration = perf_stop - perf_start
        self.step_duration = (self.run_duration / _no_of_steps) * 1000

    def model_step_rt(self):
        # calculate a number of seconds of the model
        _no_of_steps: float = int(
            self._model_rt_interval / self.modeling_stepsize)

        # do all model steps
        for _ in range(_no_of_steps):
            # execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # call the user interface
            self.interface.step_model(self.model_time_total)

            # increase the model clock
            self.model_time_total += self.modeling_stepsize
