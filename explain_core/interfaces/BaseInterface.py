import os, requests, getpass
import matplotlib.pyplot as plt
import numpy as np

# import pandas as pd

from pathlib import Path


class BaseInterface:
    def __init__(self, model):
        # store an object holding a complete explain object 
        self.explain_model = None

        # store a reference to the model instance
        self.model = model

        # get the modeling stepsize from the model
        self._t = model.modeling_stepsize

        # dark mode flag
        self.dark_mode = False

        # plot line colors
        self.lines = ["r-", "b-", "g-", "c-", "m-", "y-", "k-", "w-"]
        self.plot_background_color = "#1E2029"
        self.plot_background_color = "#FFFFFF"
        self.plot_height = 3
        self.plot_dpi = 300
        self.plot_fontsize = 8
        self.plot_axis_color = "darkgray"

        # realtime variables
        self.plot_rt_background_color = "black"
        self.plot_rt_height = 4
        self.plot_rt_dpi = 300
        self.plot_rt_fontsize = 8
        self.plot_rt_axis_color = "darkgray"

        # define realtime intermediates
        self.x_rt = []
        self.y_rt = []
        self.ani = {}
        self.no_dp = 1200
        self.rt_time_window = 10.0
        self.rt_update_interval = 0.2
        self.combined = False
        self.rescale_counter = 0.0
        self.rescale_interval = 2.0
        self.rescale_enabled = False
        self.parameters_rt = []
        self.fig_rt = {}
        self.ax_rt = []
        self.axs_rt = []
        self.x = {}
        self.y = {}
        self.line_rt = []
        self.lines_rt = []
        self.xy = False
        self.x_prop = ""

        self.fast_analyzer_keys = []
        self.fast_analyzer_data = {}
        self.fast_analyzer_sample_interval = 0.005
        self.analysis_object = {}
        self.user_name = ""
        self.user_token = ""

    def _log_in(self, user_name):
        # get the password
        password = getpass.getpass("Enter your password:")
        response_auth = requests.post("https://explain-user.com/api/auth", json={ "name": user_name, "password": password})
        if response_auth.status_code == 200:
            return response_auth.json()["token"]
        else:
            return False

    def get_user_state(self, state_name):
        if not self.user_name:
            self.user_name = input("Enter your username:")
        if not self.user_token:
            self.user_token = self._log_in(self.user_name)
        if self.user_token:
            response = requests.post("https://explain-user.com/api/states/get_user_state?token=" + self.user_token, json={ "user": self.user_name, "name": state_name })
            if response.status_code == 200:
                # store a dictionary
                self.explain_model = response.json()
                # initialize this model
                self.model.process_model_definition(self.explain_model["model_definition"])
            else:
                return False
    
    def get_all_user_states(self):
        if not self.user_name:
            self.user_name = input("Enter your username:")
        if not self.user_token:
            self.user_token = self._log_in(self.user_name)
        if self.user_token:
            response = requests.post("https://explain-user.com/api/states/get_all_user_states?token=" + self.user_token, json={ "user": self.user_name, "name": "all" })
            if response.status_code == 200:
                state = response.json()
                print(state)

    def get_all_shared_states(self):
        if not self.user_name:
            self.user_name = input("Enter your username:")
        if not self.user_token:
            self.user_token = self._log_in(self.user_name)
        if self.user_token:
            response = requests.post("https://explain-user.com/api/states/get_all_shared_states?token=" + self.user_token, json={ "user": self.user_name})
            if response.status_code == 200:
                state = response.json()
                print(state)

    def get_default_state(self):
        if not self.user_name:
            self.user_name = input("Enter your username:")
        if not self.user_token:
            self.user_token = self._log_in(self.user_name)
        if self.user_token:
            response = requests.post("https://explain-user.com/api/states/get_user_state?token=" + self.user_token, json={ "user": self.user_name, "name": "baseline neonate" })
            if response.status_code == 200:
                state = response.json()
                print(state)

    def scale_to_gestational_age(self, gestational_age: float):
        self.model.scale_to_gestational_age(gestational_age)

    def scale_patient(
        self,
        weight: float,
        height: float,
        blood_volume: float,
        lung_volume: float,
        res_circ_factor: float,
        el_base_circ_factor: float,
        el_min_circ_factor: float,
        el_max_circ_factor: float,
        res_resp_factor: float,
        el_base_resp_factor: float,
        u_vol_factor: float,
        hr_ref: float,
        syst_ref: float,
        diast_ref: float,
        map_ref: float,
        resp_rate: float,
        vt_rr_ratio: float,
        mv_ref: float,
    ):
        self.model.scale_patient(
            weight=weight,
            height=height,
            blood_volume=blood_volume,
            lung_volume=lung_volume,
            res_circ_factor=res_circ_factor,
            el_base_circ_factor=el_base_circ_factor,
            el_min_circ_factor=el_min_circ_factor,
            el_max_circ_factor=el_max_circ_factor,
            res_resp_factor=res_resp_factor,
            el_base_resp_factor=el_base_resp_factor,
            u_vol_factor=u_vol_factor,
            hr_ref=hr_ref,
            syst_ref=syst_ref,
            diast_ref=diast_ref,
            map_ref=map_ref,
            resp_rate=resp_rate,
            vt_rr_ratio=vt_rr_ratio,
            mv_ref=mv_ref,
        )

    def set_weight(self, weight):
        self.model.set_weight(weight)

    def set_total_blood_volume(self, new_blood_volume):
        self.model.models["Blood"].set_total_blood_volume(new_blood_volume)

    # non realtime functions
    def calculate(self, time_to_calculate=30, performance=True, suppress_output=False):
        t = self.model.calculate(
            time_to_calculate=time_to_calculate, performance=performance
        )

        if not suppress_output:
            print(
                f" Ready in {self.model.run_duration:.1f} sec. Average model step in {self.model.step_duration:.4f} ms."
            )

    def fast_forward(
        self, time_to_calculate=30, performance=True, suppress_output=False
    ):
        t = self.model.fast_forward(
            time_to_calculate=time_to_calculate, performance=performance
        )

        if not suppress_output:
            print(
                f" Ready in {self.model.run_duration:.1f} sec. Average model step in {self.model.step_duration:.4f} ms."
            )

    def analyze_init(self, properties, sampleinterval=0.005) -> None:
        # reset the fast analyzer data structures
        self.fast_analyzer_data = {}
        self.fast_analyzer_keys = []

        # make sure properties is a list
        if isinstance(properties, str):
            properties = [properties]

        # first clear the watchllist and this also clears all data
        self.model.clear_watchlist()

        # set the sample interval
        self.model.set_sample_interval(sampleinterval)
        self.fast_analyzer_sample_interval = sampleinterval

        # add the properties to the watch_list
        for prop in properties:
            self.model.add_to_watchlist(prop)
            self.fast_analyzer_data[prop] = []
            self.fast_analyzer_keys.append(prop)

    def analyze_fast(
        self, time_to_calculate=10, sampleinterval=0.005, suppress_output=True
    ):
        # clear the analyzer data
        for fak in self.fast_analyzer_keys:
            self.fast_analyzer_data[fak] = []

        # calculate the model steps
        self.model.calculate(time_to_calculate)

        # iterate over the model data list and store the data in the fast analyzer data structure
        for data in self.model.model_data:
            for fak in self.fast_analyzer_keys:
                self.fast_analyzer_data[fak].append(data[fak])

        # count the number of heartbeats
        hr = self.model.models["Heart"].heart_rate

        # analyse the  model data and store results in the analysis object
        self.analysis_object = {}

        for fak in self.fast_analyzer_keys:
            # calculate the sums for flow calculation
            if "flow" in fak:
                sum_all = 0.0
                sum_pos = 0.0
                sum_neg = 0.0
                stroke_volume = 0.0

                for f in self.fast_analyzer_data[fak]:
                    sum_all += f
                    if f > 0:
                        sum_pos += f

                sum_all = (
                    sum_all
                    * self.fast_analyzer_sample_interval
                    / time_to_calculate
                    * 60.0
                )
                sum_pos = (
                    sum_pos
                    * self.fast_analyzer_sample_interval
                    / time_to_calculate
                    * 60.0
                )
                sum_neg = sum_all - sum_pos

                fak_sv = "".join([fak, ".sv"])
                fak_net = "".join([fak, ".net"])
                fak_for = "".join([fak, ".forward"])
                fak_back = "".join([fak, ".backward"])

                self.analysis_object[fak_sv] = sum_all / hr
                self.analysis_object[fak_net] = sum_all
                self.analysis_object[fak_for] = sum_pos
                self.analysis_object[fak_back] = sum_neg
            else:
                # calculate the min and max
                minimum = min(self.fast_analyzer_data[fak])
                maximum = max(self.fast_analyzer_data[fak])
                fak_min = "".join([fak, ".min"])
                fak_max = "".join([fak, ".max"])
                self.analysis_object[fak_min] = minimum
                self.analysis_object[fak_max] = maximum

        return self.analysis_object

    def analyze(
        self,
        properties,
        time_to_calculate=10,
        sampleinterval=0.005,
        calculate=True,
        weight_based=False,
        suppress_output=False,
    ):
        # define a result object
        result = {}

        # find the weight factor
        weight = 1.0
        if weight_based:
            weight = self.model.weight

        # add the ncc ventricular
        properties.insert(0, "Heart.ncc_ventricular")

        # make sure properties is a list
        if isinstance(properties, str):
            properties = [properties]

        # if calculation is necessary then do it
        if calculate:
            # first clear the watchllist and this also clears all data
            self.model.clear_watchlist()

            # set the sample interval
            self.model.set_sample_interval(sampleinterval)

            # add the properties to the watch_list
            for prop in properties:
                self.model.add_to_watchlist(prop)

            # calculate the model steps
            self.model.calculate(time_to_calculate)

        no_dp = len(self.model.model_data)
        x = np.zeros(no_dp)
        y = []
        heartbeats = 0

        for parameter in enumerate(properties):
            y.append(np.zeros(no_dp))

        for index, t in enumerate(self.model.model_data):
            x[index] = t["time"]

            for idx, parameter in enumerate(properties):
                y[idx][index] = t[parameter]

        sv_message = False
        is_blood = False
        is_gas = False
        is_ventilator = False

        for idx, parameter in enumerate(properties):
            prop_category = parameter.split(sep=".")

            # find the modeltype of the property which is needed to be analyzed
            model_type: str = self.model.models[prop_category[0]].model_type
            if model_type == "Resistor":
                if (
                    "Blood"
                    in self.model.models[prop_category[0]]._model_comp_from.model_type
                ):
                    is_blood = True

            if model_type == "GasCapacitance" or model_type == "Breathing":
                is_gas = True

            if model_type == "Ventilator":
                is_ventilator = True

            if (
                prop_category[1] == "pres"
                or prop_category[1] == "pres_in"
                or prop_category[1] == "pres_tm"
            ):
                data = np.array(y[idx])
                max = round(np.amax(data), 5)
                min = round(np.amin(data), 5)
                mean = round((2 * min + max) / 3, 5)

                # if the modeltype is a blood model type then the unit is mmHg
                # if the modeltype is a gas model type then the unit is cmH2O
                if not suppress_output:
                    print(
                        "{:<16}: max {:10}, min {:10}, mean {:10} mmHg".format(
                            parameter, max, min, mean
                        )
                    )
                result[parameter + ".max"] = max
                result[parameter + ".min"] = min
                result[parameter + ".mean"] = round((2 * min + max) / 3, 5)
                continue

            if prop_category[1] == "vol":
                data = np.array(y[idx])
                max = round(np.amax(data) * 1000 / weight, 5)
                min = round(np.amin(data) * 1000 / weight, 5)

                if weight_based:
                    if not suppress_output:
                        print(
                            "{:<16}: max {:10}, min {:10} ml/kg".format(
                                parameter, max, min
                            )
                        )
                else:
                    if not suppress_output:
                        print(
                            "{:<16}: max {:10}, min {:10} ml".format(
                                parameter, max, min
                            )
                        )

                result[parameter + ".max"] = max
                result[parameter + ".min"] = min
                continue

            if prop_category[1] == "ncc_ventricular":
                data = np.array(y[idx])
                heartbeats = np.count_nonzero(data == 1)
                continue

            if prop_category[1] == "flow":
                data = np.array(y[idx])
                data_forward = np.where(data > 0, data, 0)
                data_backward = np.where(data < 0, data, 0)

                t_start = x[0]
                t_end = x[-1]

                sum = np.sum(data) * 1000.0 / weight
                sum_forward = np.sum(data_forward) * 1000.0 / weight
                sum_backward = np.sum(data_backward) * 1000.0 / weight

                flow = (sum * sampleinterval / (t_end - t_start)) * 60.0
                if is_ventilator:
                    flow = sum * sampleinterval / (t_end - t_start)
                flow = round(flow, 5)
                flow_forward = 0
                flow_backward = 0

                if flow != 0.0:
                    flow_forward = (sum_forward / sum) * flow
                    flow_forward = round(flow_forward, 5)

                    flow_backward = (sum_backward / sum) * flow
                    flow_backward = round(flow_backward, 5)

                if is_blood:
                    if sampleinterval == self.model.modeling_stepsize:
                        # use the no of heartbeats
                        bpm = (heartbeats / (t_end - t_start)) * 60
                    else:
                        if not sv_message:
                            if not suppress_output:
                                print(
                                    f"Stroke volume calculation might be inaccurate. Try using a sampleinterval of {self.model.modeling_stepsize}"
                                )
                            sv_message = True
                        bpm = self.model.models["Heart"].heart_rate

                    sv = round(flow / bpm, 5)
                    if weight_based:
                        if not suppress_output:
                            print(
                                "{:16}: net {:10}, forward {:10}, backward {:10} ml/kg/min, stroke volume: {:10} ml/kg, ".format(
                                    parameter, flow, flow_forward, flow_backward, sv
                                )
                            )
                    else:
                        if not suppress_output:
                            print(
                                "{:16}: net {:10}, forward {:10}, backward {:10} ml/min, stroke volume: {:10} ml, ".format(
                                    parameter, flow, flow_forward, flow_backward, sv
                                )
                            )

                    result[parameter + ".sv"] = sv
                else:
                    if weight_based:
                        if not suppress_output:
                            print(
                                "{:16}: net {:10}, forward {:10}, backward {:10} ml/kg/min".format(
                                    parameter, flow, flow_forward, flow_backward
                                )
                            )
                    else:
                        if not suppress_output:
                            print(
                                "{:16}: net {:10}, forward {:10}, backward {:10} ml/min".format(
                                    parameter, flow, flow_forward, flow_backward
                                )
                            )

                result[parameter + ".net"] = flow
                result[parameter + ".forward"] = flow_forward
                result[parameter + ".backward"] = flow_backward

                continue

            if prop_category[1] == "ncc_atrial":
                continue

            data = np.array(y[idx])
            max = round(np.amax(data), 5)
            min = round(np.amin(data), 5)

            result[parameter + ".max"] = max
            result[parameter + ".min"] = min

            if not suppress_output:
                print("{:<16}: max {:10} min {:10}".format(parameter, max, min))

        return result

        # calculate the model step
        collected_data = self.model.calculate(self.rt_update_interval, False)

        # update the realtime data structure
        for _, t in enumerate(collected_data):
            self.x_rt = self.x_rt[1:]
            if self.xy:
                self.x_rt = np.append(self.x_rt, t[self.x_prop])
                self.y_rt[0][self.no_dp - 1] = t[self.parameters_rt[0]]
                self.y_rt[0] = np.roll(self.y_rt[0], -1)
            else:
                self.x_rt = np.append(self.x_rt, t["time"])
                for idx, parameter in enumerate(self.parameters_rt):
                    self.y_rt[idx][self.no_dp - 1] = t[parameter]
                    self.y_rt[idx] = np.roll(self.y_rt[idx], -1)

    # functions to get, set and change model properties
    def set_model_property(
        self, prop, new_value, in_time: float = 5.0, at_time: float = 0.0
    ):
        # set the model property to a new value in 'in_time' seconds at 'at_time' seconds
        if prop is not None and new_value is not None:
            self.model.add_tasks(
                properties=prop, new_value=new_value, in_time=in_time, at_time=at_time
            )

    def get_model_property(self, prop):
        if prop is not None:
            return self.model.get_property(prop=prop)

    def change_model_property(
        self, prop, prop_change, in_time: float = 5.0, at_time: float = 0.0
    ):
        if prop is not None and prop_change is not None:
            current_value = self.get_model_property(prop)
            new_value = current_value * prop_change
            self.model.add_tasks(
                properties=prop, new_value=new_value, in_time=in_time, at_time=at_time
            )

    # functions for inspecting models
    def inspect_model(self, model_component):
        return self.model.inspect_component(model_component)

    def print_scaling_to_json(self, filename):
        if filename is not None:
            self.model.print_scaling_to_json(filename)

    def save_model_state_json(self, filename):
        if filename is not None:
            self.model.save_model_state_json(filename)

    # functions for saving and loading
    def save_model_state(self, filename):
        if filename is not None:
            self.model.save_model_state(filename)

    def load_model_state(self, filename):
        if filename is not None:
            self.model = self.load_model_state(filename)

    # functions for plotting time and xy graphs
    def plot_time_graph(
        self,
        properties,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        ylabel="",
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        fill_between=False,
        zeroline=False,
        sampleinterval=0.005,
        analyze=True,
        weight_based=False,
        fig_size_x=14,
        fig_size_y=2,
    ):
        # first clear the watchllist and this also clears all data
        self.model.clear_watchlist()

        # set the sample interval
        self.model.set_sample_interval(sampleinterval)

        # add the property to the watchlist
        if isinstance(properties, str):
            properties = [properties]

        # add the properties to the watch_list
        for prop in properties:
            self.model.add_to_watchlist(prop)

        # calculate the model steps
        collected_data = self.model.calculate(time_to_calculate)

        # plot the properties
        self.draw_time_graph(
            collected_data,
            properties,
            sharey,
            combined,
            ylabel,
            autoscale,
            ylowerlim,
            yupperlim,
            fill,
            fill_between,
            zeroline,
            fig_size_x,
            fig_size_y,
        )

        # analyze
        if analyze:
            self.analyze(
                properties,
                time_to_calculate,
                sampleinterval,
                calculate=False,
                weight_based=weight_based,
            )

        return collected_data

    def plot_xy_graph(
        self,
        property_x,
        property_y,
        time_to_calculate=2,
        sampleinterval=0.0005,
        fig_size_x=2,
        fig_size_y=2,
    ):
        # first clear the watchllist and this also clears all data
        self.model.clear_watchlist()

        # set the sample interval
        self.model.set_sample_interval(sampleinterval)

        # add the properties to the watchlist
        self.model.add_to_watchlist(property_x)
        self.model.add_to_watchlist(property_y)

        # calculate the model steps
        collected_data = self.model.calculate(time_to_calculate)

        self.draw_xy_graph(
            collected_data, property_x, property_y, fig_size_x, fig_size_y
        )

    def draw_xy_graph(
        self, collected_data, property_x, property_y, fig_size_x=2, fig_size_y=2
    ):
        no_dp = len(collected_data)
        x = np.zeros(no_dp)
        y = np.zeros(no_dp)

        for index, t in enumerate(collected_data):
            x[index] = t[property_x]
            y[index] = t[property_y]

        # determine number of needed plots
        if self.dark_mode:
            plt.style.use("dark_background")

        plt.figure(
            figsize=(fig_size_x, fig_size_y),
            dpi=self.plot_dpi / 1.5,
            facecolor=self.plot_background_color,
            tight_layout=True,
        )
        # Subplot of figure 1 with id 211 the data (red line r-, first legend = parameter)
        plt.plot(x, y, self.lines[0], linewidth=1)
        ax = plt.gca()
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_color(self.plot_axis_color)
        ax.spines["left"].set_color(self.plot_axis_color)

        plt.xlabel(property_x, fontsize=self.plot_fontsize / 3, labelpad=0)
        plt.ylabel(property_y, fontsize=self.plot_fontsize / 3, rotation=90, labelpad=1)
        plt.xticks(fontsize=self.plot_fontsize / 3)
        plt.yticks(fontsize=self.plot_fontsize / 3)
        plt.show()

    def draw_time_graph(
        self,
        collected_data,
        properties,
        sharey=False,
        combined=True,
        ylabel="",
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        fill_between=False,
        zeroline=False,
        fig_size_x=14,
        fig_size_y=3,
    ):
        parameters = properties
        no_parameters = 0

        no_dp = len(collected_data)
        self.counter = no_dp
        x = np.zeros(no_dp)
        y = []

        for parameter in enumerate(parameters):
            y.append(np.zeros(no_dp))
            no_parameters += 1

        for index, t in enumerate(collected_data):
            x[index] = t["time"]

            for idx, parameter in enumerate(parameters):
                y[idx][index] = t[parameter]

        # determine number of needed plots
        if self.dark_mode:
            plt.style.use("dark_background")

        # set the background color and erase the labels and headers

        if no_parameters == 1:
            combined = True

        if combined == False:
            fig, axs = plt.subplots(
                nrows=no_parameters,
                ncols=1,
                figsize=(fig_size_x, fig_size_y * 0.75 * no_parameters),
                sharex=True,
                sharey=sharey,
                constrained_layout=True,
                dpi=self.plot_dpi / 3,
            )
            # Change to the desired color
            fig.patch.set_facecolor(self.plot_background_color)
            fig.set_label("")
            fig.canvas.header_visible = False

            # Change the fontsize as desired
            if no_parameters > 1:
                for i, ax in enumerate(axs):
                    ax.tick_params(
                        axis="both", which="both", labelsize=self.plot_fontsize
                    )
                    ax.spines["right"].set_visible(False)
                    ax.spines["top"].set_visible(False)
                    ax.spines["bottom"].set_color(self.plot_axis_color)
                    ax.spines["left"].set_color(self.plot_axis_color)
                    ax.margins(x=0)
                    ax.plot(x, y[i], self.lines[i], linewidth=1)
                    ax.set_title(parameters[i], fontsize=self.plot_fontsize)
                    ax.set_xlabel("time (s)", fontsize=self.plot_fontsize)
                    ax.set_ylabel(ylabel, fontsize=self.plot_fontsize)
                    if not autoscale:
                        ax.set_ylim([ylowerlim, yupperlim])
                    if zeroline:
                        ax.hlines(0, np.amin(x), np.amax(x), linestyles="dashed")
                    if fill:
                        ax.fill_between(x, y[i], color="blue", alpha=0.3)

        if combined:
            fig = plt.figure(
                figsize=(fig_size_x, fig_size_y),
                dpi=self.plot_dpi / 3,
                facecolor=self.plot_background_color,
                tight_layout=True,
            )
            plt.tick_params(axis="both", which="both", labelsize=self.plot_fontsize)
            fig.patch.set_facecolor(self.plot_background_color)
            fig.set_label("")
            fig.canvas.header_visible = False

            ax = plt.gca()
            ax.spines["right"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_color(self.plot_axis_color)
            ax.spines["left"].set_color(self.plot_axis_color)
            plt.margins(x=0, y=0)
            if not autoscale:
                plt.ylim([ylowerlim, yupperlim])
            for index, parameter in enumerate(parameters):
                # Subplot of figure 1 with id 211 the data (red line r-, first legend = parameter)
                plt.plot(x, y[index], self.lines[index], linewidth=1, label=parameter)
                if fill:
                    plt.fill_between(x, y[index], color="blue", alpha=0.3)
            if zeroline:
                plt.hlines(0, np.amin(x), np.amax(x), linestyles="dashed")
            plt.xlabel("time (s)", fontsize=self.plot_fontsize)
            plt.ylabel(ylabel, fontsize=self.plot_fontsize)
            plt.xticks(fontsize=self.plot_fontsize)
            plt.yticks(fontsize=self.plot_fontsize)
            # Add a legend
            plt.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.22),
                ncol=6,
                fontsize=self.plot_fontsize,
            )
            if fill_between:
                plt.fill_between(x, y[0], y[1], color="blue", alpha=0.1)

        plt.show()

    def scale_patient_by_gestational_age(self, gestational_age: float, output=False):
        self.model.scale_patient_by_gestational_age(gestational_age, output=output)
