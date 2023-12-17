from explain_core.ModelEngine import ModelEngine
from explain_core.interfaces.BaseInterface import BaseInterface

import random as rand
import csv
import os
import datetime
from time import perf_counter


class DatasetBuilder:
    # get a reference to the whole model
    model: ModelEngine = {}
    model_interface: BaseInterface = {}

    # define the properties of the dataset builder
    model_runs: int = 100  # number of desired model runs
    pre_analysis_duration = 1  # number of seconds the model will run before analysis
    analysis_duration = 10  # number of seconds the model will run for analysis

    duration_update = 100  # number of runs after which

    # worklist
    _features = []
    _dependents = []
    dataset = {}
    sample_interval = 0.005

    def __init__(self, model) -> None:
        self.model = model
        self.model_interface = BaseInterface(self.model)

    def initialize_dataset(
        self, features: list, dependents: list, sample_interval=0.005
    ) -> None:
        # reset the worklist
        self._features = []
        self.sample_interval = 0.005
        # process the features (independent parameters which will be randomly changed)
        for feature in features:
            feature_name, feature_prop = feature["prop"].split(".")
            feature_object = {
                "model": self.model.models[feature_name],
                "name": feature["prop"],
                "prop": feature_prop,
                "current_value": getattr(self.model.models[feature_name], feature_prop),
                "ll": feature["ll"],
                "ul": feature["ul"],
                "mode": feature["mode"],
            }
            self._features.append(feature_object)

        # store the dependents list
        self._dependents = dependents

        # generate the dataset dictionary
        for _f in self._features:
            self.dataset[_f["name"]] = []

        # initialize the analyzer
        self.model_interface.analyze_init(
            self._dependents, sampleinterval=self.sample_interval
        )

        # do a first analyzer run to get the initial values
        result = self.model_interface.analyze_fast(
            time_to_calculate=1.0,
            sampleinterval=self.sample_interval,
            suppress_output=True,
        )

        # complete the dataset dictionary
        for _r_name in result.keys():
            self.dataset[_r_name] = []

    def generate_dataset(
        self,
        model_runs=10000,
        analysis_duration=10,
        pre_analysis_duration=5,
        duration_update=1000,
    ) -> None:
        self.model_runs = model_runs
        self.pre_analysis_duration = int(pre_analysis_duration)
        self.analysis_duration = int(analysis_duration)
        import datetime

        # Get the current date and time
        current_datetime = datetime.datetime.now()

        print(f"Starting model runs at {current_datetime}")

        # set the starting values if ramp up
        for _f in self._features:
            if _f["mode"] == "ramp_up":
                setattr(_f["model"], _f["prop"], _f["ll"])
            if _f["mode"] == "ramp_down":
                setattr(_f["model"], _f["prop"], _f["ul"])

        info_printed = True
        info_update_counter = 0
        first_update = 5

        for i in range(model_runs + 1):
            # Start the performance counter
            perf_start = perf_counter()

            # randomly change the features
            for _f in self._features:
                new_value = getattr(_f["model"], _f["prop"])

                if _f["mode"] == "ramp_up":
                    step_size = (_f["ul"] - _f["ll"]) / (model_runs + 1.0)
                    new_value = new_value + step_size
                if _f["mode"] == "ramp_down":
                    step_size = (_f["ll"] - _f["ul"]) / (model_runs + 1.0)
                    new_value = new_value + step_size
                if _f["mode"] == "random":
                    new_value = _f["ll"] + (_f["ul"] - _f["ll"]) * rand.random()

                setattr(_f["model"], _f["prop"], new_value)
                # do a pre-analysis run
                self.model_interface.fast_forward(
                    time_to_calculate=self.pre_analysis_duration,
                    performance=False,
                    suppress_output=True,
                )
                # do a analysis run
                result = self.model_interface.analyze_fast(
                    time_to_calculate=self.analysis_duration,
                    sampleinterval=self.sample_interval,
                )
                # store the features
                self.dataset[_f["name"]].append(new_value)
                # store the dependents
                for _r_name, _r_value in result.items():
                    self.dataset[_r_name].append(_r_value)

            # stop the performance counter
            perf_stop = perf_counter()

            # Store the performance metrics
            duration_in_seconds = (perf_stop - perf_start) * (model_runs - i)

            # Calculate hours, minutes, and second
            hours = duration_in_seconds // 3600
            remaining_seconds = duration_in_seconds % 3600
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60

            if not info_printed:
                info_printed = True
                # Get the current date and time
                current_datetime = datetime.datetime.now()
                # new time
                new_expected_time = current_datetime + datetime.timedelta(
                    seconds=int(duration_in_seconds)
                )
                # Display expected time the model runs will take
                # print("---------------------------------------------------------------------------------------")
                # print(f"Expected duration: {int(hours)}:{int(minutes)}:{int(seconds)}")
                print(f"Expected time finished: {new_expected_time}")

            info_update_counter += 1
            if info_update_counter > first_update:
                first_update = duration_update
                info_printed = False
                info_update_counter = 0

        # Get the current date and time
        current_datetime = datetime.datetime.now()
        print(f"Dataset builder finished at {current_datetime}")

    def save_dataset(self, file_name="dataset.csv") -> None:
        # The file path where the CSV will be saved
        if ".csv" not in file_name:
            file_name = f"parameter_estimation/datasets/" + file_name + ".csv"
        else:
            file_name = f"parameter_estimation/datasets/" + file_name

        current_project_path = os.getcwd()
        csv_file_path = os.path.join(current_project_path, file_name)

        # Writing to the CSV file
        with open(csv_file_path, mode="w", newline="") as file:
            # Create a writer object from csv module
            csv_writer = csv.writer(file)

            # Write the header (keys of the dictionary)
            csv_writer.writerow(self.dataset.keys())

            # Write the data rows as tuples
            csv_writer.writerows(zip(*self.dataset.values()))

        print(f"Dataset saved to {csv_file_path}.")
