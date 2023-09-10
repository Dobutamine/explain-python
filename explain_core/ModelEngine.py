import json
import pickle
import importlib
import copy
import multitimer
import math
import random
import os
from time import perf_counter
from cffi import FFI

from explain_core.helpers.DataCollector import DataCollector
from explain_core.helpers.TaskScheduler import TaskScheduler
from explain_core.base_models.BaseModel import BaseModel
from explain_core.functions.BloodComposition import set_blood_composition


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

    # realtime object
    _rt_clock = None
    _rt_running = False
    _rt_interval = 0.015
    _rt_no_of_steps = 30

    # define the constructor
    def __init__(self, model_definition_filename: str):
        # initialize all model components with the parameters from the JSON file
        self.initialized = self.init_model(model_definition_filename)

        # store the current model definition filename
        self.model_definition_filename = model_definition_filename

        # compile the c modules
        self.build_c_modules()

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
            self.update_log(
                f"The JSON model definition file: {model_definition_filename} failed to load or can not be found!", "error")
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
                    self.update_log(
                        f"Load error: {model_type} model not found OR the model has a syntax error. Error {error}", "error")
                    error_counter += 1

            else:
                # get the model class from the module
                model_class = getattr(model_module, model_type)

                # instantiate the model class with the properties stored in the model_definition file and a reference to the other components and add it to the components dictionary
                try:
                    self.models[model['name']] = model_class(**model)
                except Exception as error:
                    # a module holding the desired model class is producing an error while instantiating
                    self.update_log(
                        f"Instantiation error: {model_type} model failed to instantiate. Error: {error}", "error")
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
                    self.update_log(
                        f"Initialization error: {model.name}: {model.model_type} model failed to initialize with error: {error}", "error")
                    init_errors += 1

            if init_errors > 0 or dep_errors > 0:
                self.initialized = False
            else:
                self.update_log(
                    f" Model '{self.name}' loaded and initialized correctly.")
                self.initialized = True

        else:
            self.initialized = False

        self.status['initialized'] = self.initialized

    def build_c_modules(self):
        # instantiate the ffi engine
        ffibuilder = FFI()
        
        # get current working directory
        cwd = os.getcwd()

        # get the filepaths to the c and h files
        filepath_c_module = os.path.join(cwd, "explain_core", "modules", "blood_composition.c")
        filepath_h_module = os.path.join(cwd, "explain_core", "modules", "blood_composition.h")

        # read the header file and inject it into the ffibuilder
        with open(filepath_h_module, 'r') as f:
            header = f.read()
        ffibuilder.cdef(header)

        # read the source file and inject it into the ffibuilder
        with open(filepath_c_module, 'r') as f:
            source = f.read()
        ffibuilder.set_source("_blood_composition", source)

        # set the working directory to make sure the c compiler can find the files
        os.chdir(cwd + "/explain_core/modules")

        # build the module
        output_filename = ffibuilder.compile(verbose=False)

        # remove the intermediate c and h files
        output_filename = output_filename.split('.')[0]
        intermediate_c_file = output_filename + ".c"
        intermediate_h_file = output_filename + ".h"

        if os.path.exists(intermediate_c_file):
            os.remove(intermediate_c_file)
        if os.path.exists(intermediate_h_file):
            os.remove(intermediate_h_file)

        # Change back the current working directory
        os.chdir(cwd)


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
                    self.update_log(
                        f'Dependency error: model {model.name} depends on {dep} which is not present.', "error")
                    dep_errors += 1
        if dep_errors > 0:
            self.initialized = False
        return dep_errors

    def update_log(self, message, log_type="log"):
        if log_type == "log":
            self.status['log'].append(message)

        if len(self.status['log']) > 5:
            self.status['log'].pop(0)

        if log_type == "error":
            self.status['error_log'].append(message)

        if len(self.status['error_log']) > 5:
            self.status['error_log'].pop(0)

    def start(self, rt_interval=0.015):
        # set the realtime interval
        self._rt_interval = rt_interval

        # calculate the number of steps of the model
        self._rt_no_of_steps: int = int(
            self._rt_interval / self.modeling_stepsize)

        # empty the datacollector
        self._datacollector.clear_data()

        # declare the realtime counter
        self._rt_clock = multitimer.RepeatingTimer(
            rt_interval, self._calculate_rt)

        # start the realtime clock
        self._rt_clock.start()
        self._rt_running = True
        self.update_log(
            f"Model '{self.name}' is running in realtime with a {self._rt_interval} sec. resolution.")

    def stop(self):
        try:
            self.update_log(f"Model '{self.name}' is stopped.")
            self._rt_clock.stop()
            self._rt_clock = None
            self._rt_running = False
        except:
            pass

    def _calculate_rt(self):
        # this performance optimized routine will quickly calculate a model run
        # but does not use the datacollector module record any data
        # so only instantaneous data is available by explicit request
        # for example models['AA'].pres  for the pressure in AA

        # Cache the attributes for faster access during the model loop
        run_tasks = self._task_scheduler.run_tasks
        model_time_total = self.model_time_total
        modeling_stepsize = self.modeling_stepsize

        # Do all model steps
        for _ in range(self._rt_no_of_steps):
            # Execute the model step method of all models
            for model in self.models.values():
                model.step_model()

             # call the task scheduler
            run_tasks(model_time_total)

            # Increase the model clock
            model_time_total += modeling_stepsize

    def calculate(self, time_to_calculate: float = 10.0, performance: bool = True) -> list:

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
        # make sure the properties object is of lilst type
        if isinstance(properties, str):
            properties = [properties]

        # add properties to watch list of the datacollector
        self._datacollector.add_to_watchlist(properties)

    def set_sample_interval(self, interval: float = 0.005):
        if interval > 0.0005:
            self._datacollector.set_sample_interval(interval)

    def call_function(self, f, **kwargs):
        # execute function with a custom number of arguments
        f(**kwargs)

    def add_tasks(self, properties: list, new_value: float, in_time: float = 1.0, at_time: float = 0.0):
        # make sure the properties are of a list type
        if isinstance(properties, str):
            properties = [properties]

        # add the task to the task scheduler
        for p in properties:
            self.set_property(p, new_value=new_value,
                              in_time=in_time, at_time=at_time)

    def get_all_tasks(self):
        return self._task_scheduler.get_all_tasks()

    def remove_all_tasks(self):
        self._task_scheduler.remove_all_tasks()

    def pause_all_tasks(self):
        self._task_scheduler.pause_all_tasks()

    def restart_all_tasks(self):
        self._task_scheduler.restart_all_tasks()

    def stop_task(self, task_id):
        self._task_scheduler.remove_task(task_id)

    def set_property(self, property: str, new_value: float, in_time: float = 1.0, at_time: float = 0.0) -> str:
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
            "at_time": at_time
        }

        # pass the task to the scheduler
        self._task_scheduler.add_task(task)

        # return the task id
        return task_id

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

    def enable_model_component(self, model_component, at_time=0):
        self.set_property(model_component + ".is_enabled",
                          True, at_time=at_time)

    def disable_model_component(self, model_component, at_time=0):
        self.set_property(model_component + ".is_enabled",
                          True, at_time=at_time)

    def save_model_state(self, filename):
        # use the binary mode 'wb' to save the model engine in this current state
        filename += ".xpl"
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    def load_model_state(self, filename):
        # use the binary mode 'rb' to load a model engine state
        with open(filename, "rb") as file:
            return pickle.load(file)

    def save_model_state_json(self, filename):
        if ".json" not in filename:
            filename += ".json"

        new_model_def = self.model_definition.copy()

        # first copy all main properties
        for key in self.model_definition.keys():
            if key != 'models':
                new_model_def[key] = getattr(self, key)

        # now process the models
        for m_name, m in self.model_definition['models'].items():
            # process the model
            for km in m.keys():
                # now get the current value in the model
                value = getattr(self.models[m['name']], km)
                if isinstance(value, dict) or isinstance(value, list):
                    new_value = value.copy()
                else:
                    new_value = value

                new_model_def['models'][m_name][km] = value

        # Convert the python object to a json string
        json_data = json.dumps(new_model_def, indent=4)

        # Write the JSON data to the file
        with open(filename, "w") as file:
            file.write(json_data)

        return new_model_def

    def restart_model(self, filename=None):
        if filename is None:
            self.initialized = self.init_model(self.model_definition_filename)
        else:
            self.initialized = self.init_model(filename)

    def get_bloodgas(self, component) -> object:
        # define a dictionary which is going to hold the bloodgas
        bg = {}

        # find the component type as we only can calculate the bloodgas in a blood or time-varying elastance component
        component_type = self.models[component].model_type

        # check whether the desired component is of an appropriate type and contains blood.
        if (component_type == "BloodCapacitance" or component_type == "BloodTimeVaryingElastance"):
            # calculate the acidbase and oxygenation
            set_blood_composition(self.models[component])

            # build the bloodgas dictionnary
            bg['ph'] = self.models[component].aboxy['ph']
            bg['po2'] = self.models[component].aboxy['po2']
            bg['pco2'] = self.models[component].aboxy['pco2']
            bg['hco3'] = self.models[component].aboxy['hco3']
            bg['be'] = self.models[component].aboxy['be']
            bg['so2'] = self.models[component].aboxy['so2']

        return bg
    
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


