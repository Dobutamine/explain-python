import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from pathlib import Path


class BaseInterface:
    def __init__(self, model):
        # store a reference to the model instance
        self.model = model

        # get the modeling stepsize from the model
        self._t = model.modeling_stepsize

        # plot line colors
        self.lines = ["r-", "b-", "g-", "c-", "m-", "y-", "k-", "w-"]
        self.plot_background_color = "#1E2029"
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

    # non realtime functions
    def calculate(self, time_to_calculate=30, performance=True):
        t = self.model.calculate(
            time_to_calculate=time_to_calculate, performance=performance
        )

        print(
            f" Ready in {self.model.run_duration:.1f} sec. Average model step in {self.model.step_duration:.4f} ms."
        )

    def fast_forward(self, time_to_calculate=30, performance=True):
        t = self.model.fast_forward(
            time_to_calculate=time_to_calculate, performance=performance
        )

        print(
            f" Ready in {self.model.run_duration:.1f} sec. Average model step in {self.model.step_duration:.4f} ms."
        )

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

                # if the modeltype is a blood model type then the unit is mmHg
                # if the modeltype is a gas model type then the unit is cmH2O
                if not suppress_output:
                    print(
                        "{:<16}: max {:10}, min {:10} mmHg".format(parameter, max, min)
                    )
                result[parameter + ".max"] = max
                result[parameter + ".min"] = min
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
            if not suppress_output:
                print("{:<16}: max {:10} min {:10}".format(parameter, max, min))

        return result

    # functions for realtime graphs
    def build_rt_graph(self, y_min=0.0, y_max=100.0):
        # get the number of parameters to show in the graph
        no_params = len(self.parameters_rt)

        # set the style of the plotter
        plt.style.use("dark_background")

        # if the type is an xy graph then set the flag to combined
        if self.xy:
            self.combined = True

        # build the plot
        if not self.combined:
            self.fig_rt, self.axs_rt = plt.subplots(
                nrows=no_params,
                ncols=1,
                figsize=(14, self.plot_height / 2.0 * no_params),
                sharex=True,
                sharey=False,
                constrained_layout=True,
                dpi=self.plot_dpi / 3,
            )

        if self.combined:
            if self.xy:
                self.fig_rt, self.axs_rt = plt.subplots(
                    nrows=1,
                    ncols=1,
                    figsize=(5, self.plot_height / 1.5),
                    sharex=True,
                    sharey=False,
                    constrained_layout=True,
                    dpi=self.plot_dpi / 3,
                )
            else:
                self.fig_rt, self.axs_rt = plt.subplots(
                    nrows=1,
                    ncols=1,
                    figsize=(14, self.plot_height / 1.5),
                    sharex=True,
                    sharey=False,
                    constrained_layout=True,
                    dpi=self.plot_dpi / 3,
                )

        # set the background color and erase the labels and headers
        self.fig_rt.patch.set_facecolor(self.plot_rt_background_color)
        self.fig_rt.set_label("")
        self.fig_rt.canvas.header_visible = False

        if no_params < 2 or self.combined:
            self.axs_rt = [self.axs_rt]

        for i, ax in enumerate(self.axs_rt):
            ax.tick_params(axis="x", labelsize=self.plot_rt_fontsize, color="white")
            ax.tick_params(axis="y", labelsize=self.plot_rt_fontsize, color="white")
            ax.set_xticks([])
            ax.set_ylim(y_min, y_max)
            ax.set_facecolor("black")
            ax.spines["right"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_color(self.plot_rt_axis_color)
            ax.spines["left"].set_color(self.plot_rt_axis_color)
            ax.margins(x=0)
            if self.xy:
                ax.set_xlabel(
                    self.x_prop, fontsize=self.plot_rt_fontsize, color="white"
                )
            else:
                ax.set_xlabel(
                    "timeframe " + str(self.rt_time_window) + " (s)",
                    fontsize=self.plot_rt_fontsize,
                    color="white",
                )
            ax.set_ylabel(
                self.parameters_rt[i], fontsize=self.plot_rt_fontsize, color="white"
            )
            # Set the color of tick labels
            ax.tick_params(axis="x", colors=self.plot_rt_axis_color)
            ax.tick_params(axis="y", colors=self.plot_rt_axis_color)

    def init_rt_graph(self, combined=False):
        self.lines_rt = []
        self.x = np.arange(0, self.no_dp)
        if not self.combined:
            for i, ax in enumerate(self.axs_rt):
                (line_rt,) = ax.plot(
                    self.x, np.random.rand(self.no_dp), self.lines[i], linewidth=1
                )
                self.lines_rt.append(line_rt)
        else:
            for i, param in enumerate(self.parameters_rt):
                (line_rt,) = self.axs_rt[0].plot(
                    self.x, np.random.rand(self.no_dp), self.lines[i], linewidth=1
                )
                self.lines_rt.append(line_rt)

        return self.lines_rt

    def rescale_rt_graph(self):
        max_c = -1000
        min_c = 1000
        if self.xy:
            for i, ax in enumerate(self.axs_rt):
                max = np.max(self.x_rt)
                min = np.min(self.x_rt)
                ax.set_xlim(min - 0.1 * min, max + 0.1 * max)
                for i, ax in enumerate(self.axs_rt):
                    max = np.max(self.y_rt[i])
                    min = np.min(self.y_rt[i])
                    ax.set_ylim(min - 0.1 * min, max + 0.1 * max)
            return

        if self.combined:
            for i, l in enumerate(self.lines_rt):
                max = np.max(self.y_rt[i])
                min = np.min(self.y_rt[i])
                if max > max_c:
                    max_c = max
                if min < min_c:
                    min_c = min
                self.axs_rt[0].set_ylim(min_c - 0.1 * min_c, max_c + 0.1 * max_c)
        else:
            for i, ax in enumerate(self.axs_rt):
                max = np.max(self.y_rt[i])
                min = np.min(self.y_rt[i])
                ax.set_ylim(min - 0.1 * min, max + 0.1 * max)

    def animate_rt_graph(self, i):
        self.model_step_rt()
        self.rescale_counter += self.rt_update_interval
        if self.rescale_counter > self.rescale_interval:
            self.rescale_counter = 0
            if self.rescale_enabled:
                self.rescale_rt_graph()

        for i, line in enumerate(self.lines_rt):
            line.set_ydata(self.y_rt[i])  # update the data.

        if self.xy:
            line.set_xdata(self.x_rt)

        return self.lines_rt

    def plot_rt(
        self,
        properties=["AA.pres"],
        update_interval=0.2,
        autoscale=True,
        autoscale_interval=2.0,
        combined=True,
        time_window=5.0,
        sample_interval=0.005,
        y_min=0,
        y_max=100,
        xy=False,
    ):
        self.remove_rt()
        self.ani = {}
        self.rt_time_window = time_window
        self.model._datacollector.sample_interval = sample_interval
        self.rescale_enabled = autoscale
        self.rescale_interval = autoscale_interval
        self.rt_update_interval = update_interval
        self.combined = combined
        self.xy = xy

        # calculate the number of datapoints on the x-axis
        self.no_dp = int(time_window / sample_interval)
        self.x_prop = ""
        # save the watched parameters to the parameter list
        self.parameters_rt = properties.copy()

        if self.xy:
            if len(properties) != 2:
                print("Error: Provide an x and y property.")
                return
            else:
                self.x_prop = properties[0]
                del properties[0]

        # initialize the datacollector
        self.start_rt_graph(properties, sample_interval)

        # build the realtime plot
        self.build_rt_graph(y_min=y_min, y_max=y_max)

        # start the animation timer
        self.ani = animation.FuncAnimation(
            self.fig_rt,
            self.animate_rt_graph,
            init_func=self.init_rt_graph,
            interval=self.rt_update_interval * 1000.0,
            blit=True,
            save_count=50,
        )

        # show the plot
        plt.show()

    def start_rt_graph(self, properties, sampleinterval=0.005):
        # first clear the watchllist and this also clears all data
        self.model._datacollector.clear_watchlist()

        # set the sample interval
        self.model._datacollector.set_sample_interval(sampleinterval)

        # add the property to the watchlist
        if isinstance(properties, str):
            properties = [properties]

        # build the plot data structure
        # self.x_rt = np.zeros(self.no_dp)
        self.x_rt = np.arange(0, self.no_dp)
        self.y_rt = []
        self.no_parameters_rt = 0

        # add the properties to the watch_list
        if not self.xy:
            for prop in properties:
                if prop != None:
                    self.y_rt.append(np.random.rand(self.no_dp))
                    self.no_parameters_rt += 1
                    self.model._datacollector.add_to_watchlist(prop)
        else:
            self.model._datacollector.add_to_watchlist(self.x_prop)
            self.model._datacollector.add_to_watchlist(properties[0])
            self.y_rt.append(np.random.rand(self.no_dp))
            self.no_parameters_rt = 1

        if self.xy:
            del self.parameters_rt[0]

    def remove_rt(self):
        try:
            self.ani.event_source.stop()
            del self.ani
        except:
            pass

    def stop_rt(self):
        self.ani.pause()

    def restart_rt(self):
        self.ani.resume()

    def model_step_rt(self):
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
        )

        # analyze
        if analyze:
            self.analyze(properties, time_to_calculate, sampleinterval, calculate=False)

    def plot_xy_graph(
        self, property_x, property_y, time_to_calculate=2, sampleinterval=0.0005
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

        self.draw_xy_graph(collected_data, property_x, property_y)

    def draw_xy_graph(self, collected_data, property_x, property_y):
        no_dp = len(collected_data)
        x = np.zeros(no_dp)
        y = np.zeros(no_dp)

        for index, t in enumerate(collected_data):
            x[index] = t[property_x]
            y[index] = t[property_y]

        # determine number of needed plots
        plt.style.use("dark_background")

        plt.figure(
            figsize=(2, 2),
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
        plt.style.use("dark_background")
        # set the background color and erase the labels and headers

        if no_parameters == 1:
            combined = True

        if combined == False:
            fig, axs = plt.subplots(
                nrows=no_parameters,
                ncols=1,
                figsize=(14, self.plot_height * 0.75 * no_parameters),
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
                figsize=(14, self.plot_height),
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
