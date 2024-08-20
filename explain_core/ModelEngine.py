import json
import pickle
import importlib
import random
import math
import datetime
from time import perf_counter

from explain_core.helpers.DataCollector import DataCollector
from explain_core.helpers.TaskScheduler import TaskScheduler
from explain_core.cpp_models.CppModelsBuilder import compile_modules


class ModelEngine:
    # ---------------------- updated -----------------------------------------------
    def __init__(self):
        # define an object holding the entire model and submodels
        self.models: dict = {}

        # define an object holding the model properties of the current model
        self.model_definition: dict = {}
        self.model_definition_filename: str = ""

        # define an object holding the high resolution model data
        self.model_data: list = []

        # define an attribute holding the name of the model
        self.name: str = ""

        # define an attribute holding the description of the model
        self.description: str = ""

        # define an attribute holding the weight
        self.weight: float = 3.3

        # define an attribute holding the length in meters
        self.height: float = 0.50

        # define an attribute holding the body surface area
        self.bsa: float = 0.2

        # define a gestational age attribute
        self.gestational_age: float = 40.0

        # define a age attribute
        self.age: float = 0.0

        # define an attribute holding the modeling stepsize
        self.modeling_stepsize: float = 0.0005

        # define an attribute holding the model time
        self.model_time_total: float = 0.0

        # define an obvject holding the  datacollector
        self._datacollector: dict = {}

        # define an object holding the task scheduler
        self._task_scheduler: dict = {}

        # performance
        self.run_duration: float = 0.0
        self.step_duration: float = 0.0

        # define local attributes
        self.initialized: bool = False

        # define a status message object
        self.status = {"log": [], "error_log": [], "initialized": False}

        # define state variables for analysis purposes
        self.ncc_ventricular: int = 0.0

        # compile the c++ modules
        compile_modules()

    def load_model_definition(self, model_definition_filename: str):
        # store the definition filename
        self.model_definition_filename = model_definition_filename

        # set the error counter = 0
        error_counter = 0

        # reset the status log
        self.status = {"log": [], "error_log": [], "initialized": False}

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
            self.name = self.model_definition["name"]
            self.description = self.model_definition["description"]
            self.weight = self.model_definition["weight"]
            self.height = self.model_definition["height"]
            self.bsa = math.pow((self.weight * (self.height * 100.0) / 3600.0), 0.5)
            self.modeling_stepsize = self.model_definition["modeling_stepsize"]
            self.model_time_total = self.model_definition["model_time_total"]

        except:
            # signal that the json file failed to load
            print(
                f"The JSON model definition file: {model_definition_filename} failed to load or can not be found!"
            )
            self._update_log(
                f"The JSON model definition file: {model_definition_filename} failed to load or can not be found!",
                "error",
            )
            self.initialized = False

            # terminate function
            return

        # instantiate all model components and put a reference to them in the components list
        for key, model in self.model_definition["models"].items():
            # try to find the desired model class from the core_models or custom_models folder
            model_type = model["model_type"]

            # try to import the module holding the model class from the core_models folder
            try:
                model_module = importlib.import_module(
                    "explain_core.core_models." + model_type
                )
            except:
                try:
                    # try to import the module holding the model class from the custom models folder
                    model_module = importlib.import_module("models." + model_type)
                except:
                    try:
                        # try to import the module holding the model class from the custom models folder
                        model_module = importlib.import_module(
                            "explain_core.device_models." + model_type
                        )
                    except Exception as error:
                        print(
                            f"Load error: {model_type} model not found OR the model has a syntax error. Error {error}"
                        )
                        self._update_log(
                            f"Load error: {model_type} model not found OR the model has a syntax error. Error {error}",
                            "error",
                        )
                        error_counter += 1

            # get the model class from the module
            model_class = getattr(model_module, model_type)

            # instantiate the model class with the properties stored in the model_definition file and a reference to the other components and add it to the components dictionary
            try:
                self.models[model["name"]] = model_class(self)
            except Exception as error:
                print(
                    f"Instantiation error: {model_type} model failed to instantiate. Error: {error}"
                )
                # a module holding the desired model class is producing an error while instantiating
                self._update_log(
                    f"Instantiation error: {model_type} model failed to instantiate. Error: {error}",
                    "error",
                )
                error_counter += 1

        # initialize a datacollector
        self._datacollector = DataCollector(self)

        # initialize a task scheduler
        self._task_scheduler = TaskScheduler(self)



        # initialize all the models
        if error_counter == 0:
            init_errors = 0
            # initialize all components
            for model_name, model in self.models.items():
                model_args = self.model_definition["models"][model_name]
                try:
                    model.init_model(**model_args)
                except Exception as error:
                    print(
                        f"Initialization error: {model.name}: {model.model_type} model failed to initialize with error: {error}"
                    )
                    # a module holding the desired model class is producing an error while initiallizing
                    self._update_log(
                        f"Initialization error: {model.name}: {model.model_type} model failed to initialize with error: {error}",
                        "error",
                    )
                    init_errors += 1

            # check all models for dependency errors
            dep_errors: int = self._check_dependencies()

            if init_errors > 0 or dep_errors > 0:
                self.initialized = False
            else:
                print(f" Model '{self.name}' loaded and initialized correctly.")
                self._update_log(
                    f" Model '{self.name}' loaded and initialized correctly."
                )
                self.initialized = True

        else:
            self.initialized = False

        self.status["initialized"] = self.initialized

    def save_model_state_json(self, filename):
        # create basic json object
        new_json = {
            "explain_version": self.model_definition["explain_version"],
            "owner": self.model_definition["owner"],
            "date_created": self.model_definition["date_created"],
            "date_modified": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "shared": self.model_definition["shared"],
            "protected": self.model_definition["protected"],
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "height": self.height,
            "gestational_age": self.gestational_age,
            "age": self.age,
            "modeling_stepsize": self.modeling_stepsize,
            "model_time_total": self.model_time_total,
            "models": {}
        }
        # process the model definition file to find the necessary properties
        for model_name, model in self.models.items():
            # iterate over all attributes of the model
            new_json["models"][model_name] = {}
            for prop_name, prop in model.__dict__.items():
                if not prop_name.startswith("_"):
                    new_json["models"][model_name][prop_name] = prop

        # save the json file
        with open(filename, "w") as file:
            # Write the dictionary to the file as JSON
            json.dump(new_json, file, indent=4)

    def save_model_definition(self, filename):
        if ".json" not in filename:
            filename += ".json"

        new_model_def = self.model_definition.copy()

        # first copy all main properties
        for key in self.model_definition.keys():
            if key != "models":
                new_model_def[key] = getattr(self, key)

        # now process the models
        for m_name, m in self.model_definition["models"].items():
            # process the model
            for km in m.keys():
                # now get the current value in the model
                value = getattr(self.models[m["name"]], km)
                if isinstance(value, dict) or isinstance(value, list):
                    new_value = value.copy()
                else:
                    new_value = value

                new_model_def["models"][m_name][km] = value

        # Convert the python object to a json string
        json_data = json.dumps(new_model_def, indent=4)

        # Write the JSON data to the file
        with open(filename, "w") as file:
            file.write(json_data)

        return new_model_def

    def save_model_state(self, filename):
        # use the binary mode 'wb' to save the model engine in this current state
        if ".xpl" not in filename:
            filename += ".xpl"
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    def load_model_state(self, filename):
        # use the binary mode 'rb' to load a model engine state
        if ".xpl" not in filename:
            filename += ".xpl"
        with open(filename, "rb") as file:
            return pickle.load(file)

    def get_status(self):
        return self.status

    def get_log(self):
        return self.status["log"]

    def set_weight(self, weight: float):
        if weight > 0.0 and weight < 100.0:
            self.weight = weight
            self.bsa = math.pow((self.weight * (self.height * 100.0) / 3600.0), 0.5)

    def set_height(self, height: float):
        if height > 0.0 and height < 2.5:
            self.height = height
            self.bsa = math.pow((self.weight * (self.height * 100.0) / 3600.0), 0.5)

    def fast_forward(
        self, time_to_calculate: float = 10.0, performance: bool = True
    ) -> list:
        # no datacollecting or task scheduler

        # Cache the attributes for faster access during the model loop
        collect_data = self._datacollector.collect_data
        run_tasks = self._task_scheduler.run_tasks
        model_time_total = self.model_time_total
        modeling_stepsize = self.modeling_stepsize

        # Calculate the number of steps of the model
        no_of_steps: int = int(time_to_calculate / modeling_stepsize)

        # reset the data collector
        self._datacollector.clear_data()

        # Start the performance counter
        if performance:
            perf_start = perf_counter()

        # Do all model steps
        for _ in range(no_of_steps):
            # Execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # Increase the model clock
            model_time_total += modeling_stepsize

        # Stop the performance counter
        if performance:
            # stop the performance counter
            perf_stop = perf_counter()

            # Store the performance metrics
            self.run_duration = perf_stop - perf_start
            self.step_duration = (self.run_duration / no_of_steps) * 1000

        # store a reference to the collected data in model_data and return it
        self.model_data = self._datacollector.collected_data
        return self.model_data

    def calculate(
        self, time_to_calculate: float = 10.0, performance: bool = True
    ) -> list:
        # Cache the attributes for faster access during the model loop
        collect_data = self._datacollector.collect_data
        run_tasks = self._task_scheduler.run_tasks
        model_time_total = self.model_time_total
        modeling_stepsize = self.modeling_stepsize

        # Calculate the number of steps of the model
        no_of_steps: int = int(time_to_calculate / modeling_stepsize)

        # reset the data collector
        self._datacollector.clear_data()

        # Start the performance counter
        if performance:
            perf_start = perf_counter()

        # Do all model steps
        for _ in range(no_of_steps):
            # Execute the model step method of all models
            for model in self.models.values():
                model.step_model()

            # Call the data collector
            collect_data(model_time_total)

            # call the task scheduler
            run_tasks(model_time_total)

            # Increase the model clock
            model_time_total += modeling_stepsize

        # Stop the performance counter
        if performance:
            # stop the performance counter
            perf_stop = perf_counter()

            # Store the performance metrics
            self.run_duration = perf_stop - perf_start
            self.step_duration = (self.run_duration / no_of_steps) * 1000

        # store a reference to the collected data in model_data and return it
        self.model_data = self._datacollector.collected_data
        return self.model_data

    def clear_data(self):
        self.model_data = []
        self._datacollector.clear_data()

    def clear_watchlist(self):
        self._datacollector.clear_watchlist()

    def add_to_watchlist(self, properties: list):
        # make sure the properties object is of list type
        if isinstance(properties, str):
            properties = [properties]

        # add properties to watch list of the datacollector
        self._datacollector.add_to_watchlist(properties)

    def set_sample_interval(self, interval: float = 0.005):
        if interval >= 0.0005:
            self._datacollector.set_sample_interval(interval)

    def call_function(self, f, **kwargs):
        # execute function with a custom number of arguments
        f(**kwargs)

    def add_tasks(
        self,
        properties: list,
        new_value: float,
        in_time: float = 1.0,
        at_time: float = 0.0,
    ):
        # make sure the properties are of a list type
        if isinstance(properties, str):
            properties = [properties]

        # add the task to the task scheduler
        for p in properties:
            self.set_property(p, new_value=new_value, in_time=in_time, at_time=at_time)

    def get_tasks(self):
        return self._task_scheduler.get_all_tasks()

    def remove_tasks(self):
        self._task_scheduler.remove_all_tasks()

    def start_tasks(self):
        self._task_scheduler.restart_all_tasks()

    def stop_tasks(self, task_id):
        self._task_scheduler.remove_task(task_id)

    def set_property(
        self,
        property: str,
        new_value: float,
        in_time: float = 1.0,
        at_time: float = 0.0,
    ) -> str:
        # define some placeholders
        task_id: int = random.randint(0, 1000)
        m: BaseModel = None
        p1: str = None
        p2: str = None

        # build a task scheduler object
        t = property.split(".")

        if len(t) < 4 and len(t) > 1:
            if len(t) == 2:
                m = t[0]
                p1 = t[1]
            if len(t) == 3:
                m = t[0]
                p1 = t[1]
                p2 = t[2]
        else:
            return False

        # define a task for the task scheduler
        task = {
            "id": task_id,
            "model": self.models[m],
            "prop1": p1,
            "prop2": p2,
            "new_value": new_value,
            "in_time": in_time,
            "at_time": at_time,
        }

        # pass the task to the scheduler
        self._task_scheduler.add_task(task)

        # return the task id
        return task_id

    def get_property(self, prop: str):
        # declare an object to hold the values
        processed_prop = self._find_model_prop(prop)
        prop1 = processed_prop["prop1"]
        prop2 = processed_prop.get("prop2")
        value = getattr(processed_prop["model"], prop1)
        if prop2 is not None:
            value = value.get(prop2, 0)
        return value

    def inspect_model(self, property=None):
        inspect = {}
        for component_name, component in self.models.items():
            if property is None:
                inspect[component_name] = self.inspect_component(component_name)
            else:
                try:
                    inspect[component_name] = self.inspect_component(component_name)[
                        property
                    ]
                except:
                    pass

        return inspect

    def inspect_component(self, model_component):
        content = {}
        for attribute in dir(self.models[model_component]):
            if not attribute.startswith("__"):
                attr_type = type(getattr(self.models[model_component], attribute))
                if (
                    (attr_type is str)
                    or (attr_type is float)
                    or (attr_type is bool)
                    or (attr_type is int)
                ):
                    content[attribute] = getattr(
                        self.models[model_component], attribute
                    )
        return content

    def restart_model(self, filename=None):
        if filename is None:
            self.initialized = self.init_model(self.model_definition_filename)
        else:
            self.initialized = self.init_model(filename)

    def _check_dependencies(self) -> int:
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
                    print(f"Dependency error: model {model.name} depends on {dep} which is not present.")
                    self._update_log(
                        f"Dependency error: model {model.name} depends on {dep} which is not present.",
                        "error",
                    )
                    dep_errors += 1
        if dep_errors > 0:
            self.initialized = False
        return dep_errors

    def _find_model_prop(self, prop):
        # split the model from the prop
        t = prop.split(sep=".")

        # if only 1 property is present
        if len(t) == 2:
            # try to find the parameter in the model
            if t[0] in self.models:
                if hasattr(self.models[t[0]], t[1]):
                    return {
                        "label": prop,
                        "model": self.models[t[0]],
                        "prop1": t[1],
                        "prop2": None,
                    }

        # if 2 properties are present
        if len(t) == 3:
            # try to find the parameter in the model
            if t[0] in self.models:
                if hasattr(self.models[t[0]], t[1]):
                    return {
                        "label": prop,
                        "model": self.models[t[0]],
                        "prop1": t[1],
                        "prop2": t[2],
                    }

        return None

    def _update_log(self, message, log_type="log"):
        if log_type == "log":
            self.status["log"].append(message)

        if len(self.status["log"]) > 5:
            self.status["log"].pop(0)

        if log_type == "error":
            self.status["error_log"].append(message)

        if len(self.status["error_log"]) > 5:
            self.status["error_log"].pop(0)
