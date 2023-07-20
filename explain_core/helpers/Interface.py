
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from pathlib import Path
from explain_core.functions.Acidbase import calc_acidbase_from_tco2
from explain_core.functions.Oxygenation import calc_oxygenation_from_to2
from explain_core.helpers.DataCollector import DataCollector

import warnings
warnings.filterwarnings("ignore")


class Interface:
    def __init__(self, model):
        # store a reference to the model instance
        self.model = model

        # get the modeling stepsize from the model
        self.t = model.modeling_stepsize

        # initialize a datacollector
        self.dc = DataCollector(model)

        # plot line colors
        self.lines = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-', 'w-']

        # define a list holding the prop changes
        self.propChanges = []
        self.prop_update_interval = 0.015
        self.prop_update_counter = 0

        self.output_path = str(os.path.join(Path().absolute())) + r'/'

        self.plot_background_color = '#1E2029'
        self.plot_height = 4
        self.plot_dpi = 300
        self.plot_fontsize = 12
        self.plot_axis_color = 'darkgray'

        # realtime variables
        self.plot_rt_background_color = 'black'
        self.plot_rt_height = 4
        self.plot_rt_dpi = 300
        self.plot_rt_fontsize = 8
        self.plot_rt_axis_color = 'darkgray'

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

    def build_rt_graph(self, y_min=0.0, y_max=100.0):
        # get the number of parameters to show in the graph
        no_params = len(self.parameters_rt)

        # set the style of the plotter
        plt.style.use('dark_background')

        # if the type is an xy graph then set the flag to combined
        if self.xy:
            self.combined = True

        # build the plot
        if not self.combined:
            self.fig_rt, self.axs_rt = plt.subplots(nrows=no_params, ncols=1, figsize=(
                14, self.plot_height / 2.0 * no_params), sharex=True, sharey=False, constrained_layout=True, dpi=self.plot_dpi / 3)

        if self.combined:
            if self.xy:
                self.fig_rt, self.axs_rt = plt.subplots(nrows=1, ncols=1, figsize=(
                    5, self.plot_height / 1.5), sharex=True, sharey=False, constrained_layout=True, dpi=self.plot_dpi / 3)
            else:
                self.fig_rt, self.axs_rt = plt.subplots(nrows=1, ncols=1, figsize=(
                    14, self.plot_height / 1.5), sharex=True, sharey=False, constrained_layout=True, dpi=self.plot_dpi / 3)

        # set the background color and erase the labels and headers
        self.fig_rt.patch.set_facecolor(self.plot_rt_background_color)
        self.fig_rt.set_label('')
        self.fig_rt.canvas.header_visible = False

        if (no_params < 2 or self.combined):
            self.axs_rt = [self.axs_rt]

        for i, ax in enumerate(self.axs_rt):
            ax.tick_params(
                axis='x', labelsize=self.plot_rt_fontsize, color='white')
            ax.tick_params(
                axis='y', labelsize=self.plot_rt_fontsize, color='white')
            ax.set_xticks([])
            ax.set_ylim(y_min, y_max)
            ax.set_facecolor('black')
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_color(self.plot_rt_axis_color)
            ax.spines['left'].set_color(self.plot_rt_axis_color)
            ax.margins(x=0)
            if self.xy:
                ax.set_xlabel(
                    self.x_prop, fontsize=self.plot_rt_fontsize, color='white')
            else:
                ax.set_xlabel(
                    'timeframe ' + str(self.rt_time_window) + ' (s)', fontsize=self.plot_rt_fontsize, color='white')
            ax.set_ylabel(
                self.parameters_rt[i], fontsize=self.plot_rt_fontsize, color='white')
            # Set the color of tick labels
            ax.tick_params(axis='x', colors=self.plot_rt_axis_color)
            ax.tick_params(axis='y', colors=self.plot_rt_axis_color)

    def init_rt_graph(self, combined=False):
        self.lines_rt = []
        self.x = np.arange(0, self.no_dp)
        if not self.combined:
            for i, ax in enumerate(self.axs_rt):
                line_rt, = ax.plot(self.x, np.random.rand(
                    self.no_dp), self.lines[i], linewidth=1)
                self.lines_rt.append(line_rt)
        else:
            for i, param in enumerate(self.parameters_rt):
                line_rt, = self.axs_rt[0].plot(self.x, np.random.rand(
                    self.no_dp), self.lines[i], linewidth=1)
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
                self.axs_rt[0].set_ylim(
                    min_c - 0.1 * min_c, max_c + 0.1 * max_c)
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

    def plot_rt(self, properties=["AA.pres"], update_interval = 0.2, autoscale=True, autoscale_interval = 2.0, combined=True, time_window=5.0, sample_interval=0.005, y_min=0, y_max=100, xy=False):
        # get the properties
        self.rt_time_window = time_window
        self.dc.sample_interval = sample_interval
        self.rescale_enabled = autoscale
        self.rescale_interval = autoscale_interval
        self.rt_update_interval = update_interval
        self.combined = combined
        self.xy = xy

        # calculate the number of datapoints on the x-axis
        self.no_dp = int(self.rt_time_window / self.dc.sample_interval)

        self.model._model_rt_interval = self.rt_update_interval
        self.x_prop = ""
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
            self.fig_rt, self.animate_rt_graph, init_func=self.init_rt_graph, interval=self.rt_update_interval * 1000.0, blit=True, save_count=50)

        # show the plot
        plt.show()

    def start_rt_graph(self, properties, sampleinterval=0.005):
        # first clear the watchllist and this also clears all data
        self.dc.clear_watchlist()

        # set the sample interval
        self.dc.set_sample_interval(sampleinterval)

        # add the property to the watchlist
        if (isinstance(properties, str)):
            properties = [properties]

        # build the plot data structure
        # self.x_rt = np.zeros(self.no_dp)
        self.x_rt = np.arange(0, self.no_dp)
        self.y_rt = []
        self.no_parameters_rt = 0

        # add the properties to the watch_list
        if not self.xy:
            for prop in properties:
                prop_reference = self.find_model_prop(prop)
                if (prop_reference != None):
                    self.y_rt.append(np.random.rand(self.no_dp))
                    self.no_parameters_rt += 1
                    self.dc.add_to_watchlist(prop_reference)
        else:
            prop_reference_x = self.find_model_prop(self.x_prop)
            if (prop_reference_x != None):
                self.dc.add_to_watchlist(prop_reference_x)
            prop_reference_y = self.find_model_prop(properties[0])
            if (prop_reference_y != None):
                self.dc.add_to_watchlist(prop_reference_y)
            self.y_rt.append(np.random.rand(self.no_dp))
            self.no_parameters_rt = 1

        # save the watched parameters to the parameter list
        self.parameters_rt = []
        for watched_parameter in self.dc.watch_list:
            if (watched_parameter['label'] != "Heart.ncc_ventricular" and watched_parameter['label'] != "Heart.ncc_atrial"):
                self.parameters_rt.append(watched_parameter['label'])

        if self.xy:
            del self.parameters_rt[0]

        print("Realtime model ready.")

    def remove_rt(self):
        self.ani.event_source.stop()
        del self.ani

    def stop_rt(self):
        self.ani.pause()
        print("Realtime model stopped.")

    def restart_rt(self):
        self.ani.resume()
        print("Realtime model resumed.")

    def model_step_rt(self):
        # calculate a number of seconds of the model
        _no_of_steps: float = int(
            self.model._model_rt_interval / self.model.modeling_stepsize)

        # do all model steps
        for _ in range(_no_of_steps):
            # execute the model step method of all models
            for model in self.model.models.values():
                model.step_model()

            # call the user interface
            self.model.interface.step_model(self.model.model_time_total)

            # increase the model clock
            self.model.model_time_total += self.model.modeling_stepsize

        # update the realtime data structure
        for _, t in enumerate(self.dc.collected_data):
            self.x_rt = self.x_rt[1:]
            if self.xy:
                self.x_rt = np.append(self.x_rt, t[self.x_prop])
                self.y_rt[0][self.no_dp - 1] = t[self.parameters_rt[0]]
                self.y_rt[0] = np.roll(self.y_rt[0], -1)
            else:
                self.x_rt = np.append(self.x_rt, t['time'])
                for idx, parameter in enumerate(self.parameters_rt):
                    self.y_rt[idx][self.no_dp - 1] = t[parameter]
                    self.y_rt[idx] = np.roll(self.y_rt[idx], -1)

        # clear the data collector
        self.dc.clear_data()

    def calculate(self, time_to_calculate):
        # calculate the model steps
        no_steps: int = int(time_to_calculate / self.model.modeling_stepsize)
        print(
            f'Calculating model run of {time_to_calculate} sec. in {no_steps} steps.')
        self.prop_update_counter = 0
        self.model.calculate(time_to_calculate)
        run_duration = round(self.model.run_duration, 3)
        step_duration = round(self.model.step_duration, 4)
        print(
            f'Ready in {run_duration} sec. Average model step in {step_duration} ms.')

    def step_model(self, model_clock):
        self.dc.collect_data(model_clock)
        # process the propchanges
        if (self.prop_update_counter >= self.prop_update_interval):
            self.prop_update_counter = 0
            for change in self.propChanges:
                change.update()
                if change.completed:
                    self.propChanges.remove(change)

        self.prop_update_counter += self.t

    # property setters and getters
    def set_property(self, prop, new_value, in_time=0, at_time=0):
        prop = self.find_model_prop(prop)
        if (prop != None):
            # check whether the type of new_value is the same as the model type
            if type(new_value) == type(getattr(prop['model'], prop['prop'])):
                new_prop_change = propChange(prop, new_value, in_time, at_time)
                self.propChanges.append(new_prop_change)
                print(f"{prop['label']} is scheduled to change from {new_prop_change.initial_value} to {new_value} in {in_time} sec. at {at_time} sec. during next model run.")
            else:
                current_value_type = type(getattr(prop['model'], prop['prop']))
                new_value_type = type(new_value)
                print(
                    f'property type mismatch. model property type = {current_value_type}, new value type = {new_value_type}')
        else:
            print("property not found in model")

    def get_property(self, prop):
        prop = self.find_model_prop(prop)
        if (prop != None):
            value = getattr(prop['model'], prop['prop'])
        return value

    # plotters
    def plot_vitals(self, time=30):
        self.plot_time_graph(["AA.mean", "Heart.heart_rate", "Breathing.resp_rate", "AA.aboxy.so2"], time_to_calculate=time,
                             combined=True, sharey=False, autoscale=False, ylowerlim=0, yupperlim=200, fill=False, fill_between=False)

    def plot_bloodgas(self, time=30):
        self.plot_time_graph(["AA.aboxy.ph", "AA.aboxy.pco2", "AA.aboxy.po2", "AA.aboxy.so2"], time_to_calculate=time,
                             combined=False, sharey=False, fill=False)

    def plot_ans(self, time=10):
        self.plot_time_graph(["AA.aboxy.pco2", "Breathing.target_minute_volume", "Breathing.target_tidal_volume", "Breathing.resp_rate", "Breathing.exp_tidal_volume"], time_to_calculate=time,
                             combined=False, sharey=False, fill=False)

    # lung plotters
    def plot_lung_pressures(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["DS.pres", "ALL.pres", "ALR.pres"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_volumes(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["ALL.vol", "ALR.vol"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_flows(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["MOUTH_DS.flow", "DS_ALL.flow", "DS_ALR.flow"], time_to_calculate=time, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_pressures_left(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["DS.pres", "ALL.pres"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_volumes_left(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["ALL.vol"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_flows_left(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["MOUTH_DS.flow", "DS_ALL.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_pressures_right(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["DS.pres", "ALR.pres"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_volumes_right(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["ALR.vol"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_flows_right(self, time=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["MOUTH_DS.flow", "DS_ALR.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    # heart plotters
    def plot_heart_pressures(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, fill_between=False, analyze=False):
        self.plot_time_graph(["LV.pres", "RV.pres", "LA.pres", "RA.pres", "AA.pres", "PA.pres"], time_to_calculate=time, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_volumes(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LV.vol", "RV.vol", "LA.vol", "RA.vol"], time_to_calculate=time, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_flows(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA_LV.flow", "LV_AA.flow", "RA_RV.flow", "RV_PA.flow"], time_to_calculate=time, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_pressures_left(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LV.pres", "LA.pres", "AA.pres"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_flows_left(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA_LV.flow", "LV_AA.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_volumes_left(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA.vol", "LV.vol"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_flows_right(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RA_RV.flow", "RV_PA.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_volumes_right(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RA.vol", "RV.vol"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_pressures_right(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RV.pres", "RA.pres", "PA.pres"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_left(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA.pres", "LV.pres", "LA_LV.flow", "LV_AA.flow"], time_to_calculate=time, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_right(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RA.pres", "RV.pres", "RA_RV.flow", "RV_PA.flow"], time_to_calculate=time, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_da(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["DA.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_ofo(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["FO.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_shunts(self, time=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["DA.flow", "FO.flow"], time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_ventilator_curves(self, time=5, combined=False, sharey=False, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=True):
        self.plot_time_graph(["Ventilator.vent_pres", "Ventilator.vent_flow", "Ventilator.vent_vol", "Ventilator.co2"],
                             time_to_calculate=time, autoscale=True, combined=combined, sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    # getters
    def get_vitals(self, time_to_calculate=10):
        vitals = {
            "heartrate": self.model.models['Heart'].heart_rate,
            "spo2_pre": self.model.models['AA'].aboxy['so2'],
            "abp_systole": self.model.models['AA'].systole,
            "abp_diastole": self.model.models['AA'].diastole,
            "pap_systole": self.model.models['PA'].systole,
            "pap_diastole": self.model.models['PA'].diastole,
            "cvp": self.model.models['RA'].mean,
            "resp_rate": self.model.models['Breathing'].resp_rate
        }

        return vitals

    def get_gas_flows(self, time_to_calculate=10):
        self.dc.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "GasResistor"):
                properties.append(component + ".flow")

        self.analyze(properties, time_to_calculate)

    def get_blood_flows(self, time_to_calculate=10):
        self.dc.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "BloodResistor" or component_type == "BloodValve"):
                properties.append(component + ".flow")

        self.analyze(properties, time_to_calculate, sampleinterval=0.0005)

    def get_bloodgas(self, component='AA'):
        # define a dictionary which is going to hold the bloodgas
        bg = {}

        # find the component type as we only can calculate the bloodgas in a blood or time-varying elastance component
        component_type = self.model.models[component].model_type

        # check whether the desired component is of an appropriate type and contains blood.
        if (component_type == "BloodCapacitance" or component_type == "BloodTimeVaryingElastance"):
            # calculate the acidbase and oxygenation
            result_ab = calc_acidbase_from_tco2(self.model.models[component])
            result_oxy = calc_oxygenation_from_to2(
                self.model.models[component])

            # build the bloodgas dictionnary
            bg['ph'] = result_ab['ph']
            bg['po2'] = result_oxy['po2']
            bg['pco2'] = result_ab['pco2']
            bg['hco3'] = result_ab['hco3']
            bg['be'] = result_ab['be']
            bg['so2'] = result_oxy['so2']

        return bg

    def get_blood_pressures(self, time_to_calculate=10):
        self.dc.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type
            if (component_type == "BloodCapacitance" or component_type == "BloodTimeVaryingElastance"):
                properties.append(component + ".pres")

        self.analyze(properties, time_to_calculate)

    def get_total_blood_volume(self):
        total_volume = 0
        pulm_blood_volume = 0
        pulm_cap_volume = 0
        syst_blood_volume = 0
        heart_volume = 0
        cap_volume = 0
        ven_volume = 0
        art_volume = 0
        upper_body = 0
        lower_body = 0

        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "BloodCapacitance" or component_type == "BloodTimeVaryingElastance"):
                total_volume += self.model.models[component].vol
            if component == 'PA' or component == 'PV':
                pulm_blood_volume += self.model.models[component].vol
            if component == 'LL' or component == 'RL':
                pulm_blood_volume += self.model.models[component].vol
                pulm_cap_volume += self.model.models[component].vol

            # heart
            if component == 'RA' or component == 'RV' or component == 'LA' or component == 'LV' or component == 'COR':
                heart_volume += self.model.models[component].vol
            # capillaries
            if component == 'RLB' or component == 'RUB' or component == 'BR' or component == 'INT' or component == 'LS' or component == 'KID':
                cap_volume += self.model.models[component].vol
            # venous
            if component == 'IVCI' or component == 'IVCE' or component == 'SVC':
                ven_volume += self.model.models[component].vol
            if component == 'AA' or component == 'AAR' or component == 'AD':
                art_volume += self.model.models[component].vol
            if component == 'RUB' or component == 'BR' or component == 'SVC':
                upper_body += self.model.models[component].vol
            if component == 'RLB' or component == 'AAR' or component == 'AA' or component == 'AD' or component == 'IVCI' or component == 'IVCE' or component == 'INT' or component == 'LS' or component == 'KID':
                lower_body += self.model.models[component].vol

        syst_blood_volume = total_volume - pulm_blood_volume

        print(
            f"Total blood volume: {total_volume * 1000 / self.model.weight} ml/kg = {total_volume / total_volume * 100}%")
        print(
            f"Systemic blood volume: {syst_blood_volume * 1000 / self.model.weight} ml/kg = {syst_blood_volume / total_volume * 100}%")
        print(
            f"Pulmonary total blood volume: {pulm_blood_volume * 1000 / self.model.weight} ml/kg = {pulm_blood_volume / total_volume * 100}%")
        print(
            f"Pulmonary capillary blood volume: {pulm_cap_volume * 1000 / self.model.weight} ml/kg = {pulm_cap_volume / pulm_blood_volume * 100}% of total pulmonary blood volume")
        print(
            f"Heart blood volume: {heart_volume * 1000 / self.model.weight} ml/kg = {heart_volume / total_volume * 100}%")
        print(
            f"Capillary blood volume: {cap_volume * 1000 / self.model.weight} ml/kg = {cap_volume / total_volume * 100}%")
        print(
            f"Venous blood volume: {ven_volume * 1000 / self.model.weight} ml/kg = {ven_volume / total_volume * 100}%")
        print(
            f"Arterial blood volume: {art_volume * 1000 / self.model.weight} ml/kg = {art_volume / total_volume * 100}%")
        print(
            f"Upper body blood volume: {upper_body * 1000 / self.model.weight} ml/kg = {upper_body / total_volume * 100}%")
        print(
            f"Lower body blood volume: {lower_body * 1000 / self.model.weight} ml/kg = {lower_body / total_volume * 100}%")

        return total_volume

    def get_blood_volumes(self, time_to_calculate=10):
        self.dc.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "BloodCapacitance" or component_type == "BloodTimeVaryingElastance"):
                properties.append(component + ".vol")

        self.analyze(properties, time_to_calculate)

    def get_gas_pressures(self, time_to_calculate=10):
        self.dc.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "GasCapacitance" or component_type == "GasTimeVaryingElastance"):
                properties.append(component + ".pres")

        self.analyze(properties, time_to_calculate)

    def get_gas_volumes(self, time_to_calculate=10):
        self.dc.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "GasCapacitance" or component_type == "GasTimeVaryingElastance"):
                properties.append(component + ".vol")

        self.analyze(properties, time_to_calculate)

    # inspectors
    def inspect_model(self):
        model = {}
        for component_name, component in self.model.models.items():
            model[component_name] = component.description

        return model

    def inspect_model_component(self, component):
        content = {}
        for attribute in dir(self.model.models[component]):
            if not attribute.startswith('__'):
                attr_type = type(
                    getattr(self.model.models[component], attribute))
                if (attr_type is str) or (attr_type is float) or (attr_type is bool) or (attr_type is int):
                    content[attribute] = getattr(
                        self.model.models[component], attribute)
        return content

    def analyze(self, properties, time_to_calculate=10, sampleinterval=0.005, calculate=True):
        if calculate:
            # first clear the watchllist and this also clears all data
            self.dc.clear_watchlist()

            # set the sample interval
            self.dc.set_sample_interval(sampleinterval)

            # add the property to the watchlist
            if (isinstance(properties, str)):
                properties = [properties]

            # add the properties to the watch_list
            for prop in properties:
                prop_reference = self.find_model_prop(prop)
                if (prop_reference != None):
                    self.dc.add_to_watchlist(prop_reference)

            # calculate the model steps
            self.calculate(time_to_calculate)

        print("")

        parameters = []
        no_parameters = 0
        # get the watch list of the datacollector
        for watched_parameter in self.dc.watch_list:
            parameters.append(watched_parameter['label'])

        no_dp = len(self.dc.collected_data)
        x = np.zeros(no_dp)
        y = []
        heartbeats = 0

        for parameter in enumerate(parameters):
            y.append(np.zeros(no_dp))
            no_parameters += 1

        for index, t in enumerate(self.dc.collected_data):
            x[index] = t['time']

            for idx, parameter in enumerate(parameters):
                y[idx][index] = t[parameter]

        for idx, parameter in enumerate(parameters):
            prop_category = parameter.split(sep=".")

            if prop_category[1] == "pres":
                data = np.array(y[idx])
                max = round(np.amax(data), 5)
                min = round(np.amin(data), 5)

                print("{:<16}: max {:10}, min {:10} mmHg". format(
                    parameter, max, min))
                continue

            if prop_category[1] == "vol":
                data = np.array(y[idx])
                max = round(np.amax(data) * 1000, 5)
                min = round(np.amin(data) * 1000, 5)

                print(
                    "{:<16}: max {:10}, min {:10} ml/kg". format(parameter, max, min))
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

                sum = np.sum(data)
                sum_forward = np.sum(data_forward)
                sum_backward = np.sum(data_backward)

                flow = (sum * sampleinterval / (t_end - t_start))
                flow = round(flow * 1000, 5)
                flow_forward = 0
                flow_backward = 0

                if (flow != 0.0):
                    flow_forward = (sum_forward / sum) * flow
                    flow_forward = round(flow_forward, 5)

                    flow_backward = (sum_backward / sum) * flow
                    flow_backward = round(flow_backward, 5)

                bpm = (heartbeats / (t_end - t_start)) * 60
                if (sampleinterval != self.model.modeling_stepsize):
                    print(
                        f"Stroke volume calculation might be inaccurate. Try using a sampleinterval of {self.model.modeling_stepsize}")
                    bpm = self.model.models['Heart'].heart_rate
                sv = round(flow / bpm, 5)
                print("{:16}: net {:10}, forward {:10}, backward {:10} ml/kg/min, stroke volume: {:10} ml/kg, ". format(
                    parameter, flow, flow_forward, flow_backward, sv))

                continue

            if prop_category[1] == "ncc_atrial":
                continue

            data = np.array(y[idx])
            max = round(np.amax(data), 5)
            min = round(np.amin(data), 5)
            print("{:<16}: max {:10} min {:10}". format(parameter, max, min))

    def plot_time_graph(self, properties, time_to_calculate=10,  combined=True, sharey=True, ylabel='',  autoscale=True, ylowerlim=0, yupperlim=100, fill=True, fill_between=False, zeroline=False, sampleinterval=0.005, analyze=True):
        # first clear the watchllist and this also clears all data
        self.dc.clear_watchlist()

        # set the sample interval
        self.dc.set_sample_interval(sampleinterval)

        # add the property to the watchlist
        if (isinstance(properties, str)):
            properties = [properties]

        # add the properties to the watch_list
        for prop in properties:
            prop_reference = self.find_model_prop(prop)
            if (prop_reference != None):
                self.dc.add_to_watchlist(prop_reference)

        # calculate the model steps
        self.calculate(time_to_calculate)

        # print status message
        print("Preparing data plot.")

        # plot the properties
        self.draw_time_graph(sharey, combined, ylabel, autoscale,
                             ylowerlim, yupperlim, fill, fill_between, zeroline)

        # analyze
        if analyze:
            self.analyze(properties, time_to_calculate,
                         sampleinterval, calculate=False)

    def plot_xy_graph(self, property_x, property_y, time_to_calculate=2, sampleinterval=0.0005):
        # first clear the watchllist and this also clears all data
        self.dc.clear_watchlist()

        # set the sample interval
        self.dc.set_sample_interval(sampleinterval)

        prop_reference_x = self.find_model_prop(property_x)
        if (prop_reference_x != None):
            self.dc.add_to_watchlist(prop_reference_x)

        prop_reference_y = self.find_model_prop(property_y)
        if (prop_reference_y != None):
            self.dc.add_to_watchlist(prop_reference_y)

        # calculate the model steps
        self.calculate(time_to_calculate)

        self.draw_xy_graph(property_x, property_y)

    def write_to_excel(self, properties, filename='data', time_to_calculate=10, sampleinterval=0.005, calculate=True):
        self.analyze(properties, time_to_calculate=time_to_calculate,
                     sampleinterval=sampleinterval, calculate=calculate)
        # build a parameter list
        parameters = ['time']
        no_parameters = 0
        # get the watch list of the datacollector
        for watched_parameter in self.dc.watch_list:
            if (watched_parameter['label'] != "Heart.ncc_ventricular" and watched_parameter['label'] != "Heart.ncc_atrial"):
                parameters.append(watched_parameter['label'])

        data = []
        for index, t in enumerate(self.dc.collected_data):
            dataline = []
            for idx, parameter in enumerate(parameters):
                dataline.append(t[parameter])
            data.append(dataline)

        df = pd.DataFrame(data, columns=parameters)
        path = self.output_path + filename + '.xlsx'
        df.to_excel(path)

    def draw_xy_graph(self, property_x, property_y):
        no_dp = len(self.dc.collected_data)
        x = np.zeros(no_dp)
        y = np.zeros(no_dp)

        for index, t in enumerate(self.dc.collected_data):
            x[index] = t[property_x]
            y[index] = t[property_y]

        # determine number of needed plots
        plt.style.use('dark_background')

        plt.figure(figsize=(2, 2), dpi=self.plot_dpi / 1.5,
                   facecolor=self.plot_background_color, tight_layout=True)
        # Subplot of figure 1 with id 211 the data (red line r-, first legend = parameter)
        plt.plot(x, y, self.lines[0], linewidth=1)
        ax = plt.gca()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_color(self.plot_axis_color)
        ax.spines['left'].set_color(self.plot_axis_color)

        plt.xlabel(property_x, fontsize=self.plot_fontsize / 3, labelpad=0)
        plt.ylabel(property_y, fontsize=self.plot_fontsize /
                   3, rotation=90, labelpad=1)
        plt.xticks(fontsize=self.plot_fontsize / 3)
        plt.yticks(fontsize=self.plot_fontsize / 3)
        plt.show()

    def draw_time_graph(self, sharey=False, combined=True, ylabel='', autoscale=True, ylowerlim=0, yupperlim=100, fill=True, fill_between=False, zeroline=False):
        parameters = []
        no_parameters = 0
        # get the watch list of the datacollector
        for watched_parameter in self.dc.watch_list:
            if (watched_parameter['label'] != "Heart.ncc_ventricular" and watched_parameter['label'] != "Heart.ncc_atrial"):
                parameters.append(watched_parameter['label'])

        no_dp = len(self.dc.collected_data)
        self.counter = no_dp
        x = np.zeros(no_dp)
        y = []

        for parameter in enumerate(parameters):
            y.append(np.zeros(no_dp))
            no_parameters += 1

        for index, t in enumerate(self.dc.collected_data):
            x[index] = t['time']

            for idx, parameter in enumerate(parameters):
                y[idx][index] = t[parameter]

        # determine number of needed plots
        plt.style.use('dark_background')

        if (no_parameters == 1):
            combined = True

        if (combined == False):

            fig, axs = plt.subplots(nrows=no_parameters, ncols=1, figsize=(
                18, self.plot_height * 0.75 * no_parameters), sharex=True, sharey=sharey, constrained_layout=True, dpi=self.plot_dpi)
            # Change to the desired color
            fig.patch.set_facecolor(self.plot_background_color)

            # Change the fontsize as desired
            if (no_parameters > 1):
                for i, ax in enumerate(axs):
                    ax.tick_params(axis='both', which='both',
                                   labelsize=self.plot_fontsize)
                    ax.spines['right'].set_visible(False)
                    ax.spines['top'].set_visible(False)
                    ax.spines['bottom'].set_color(self.plot_axis_color)
                    ax.spines['left'].set_color(self.plot_axis_color)
                    ax.margins(x=0)
                    ax.plot(x, y[i], self.lines[i], linewidth=1)
                    ax.set_title(parameters[i], fontsize=self.plot_fontsize)
                    ax.set_xlabel('time (s)', fontsize=self.plot_fontsize)
                    ax.set_ylabel(ylabel, fontsize=self.plot_fontsize)
                    if not autoscale:
                        ax.set_ylim([ylowerlim, yupperlim])
                    if zeroline:
                        ax.hlines(0, np.amin(x), np.amax(
                            x), linestyles='dashed')
                    if fill:
                        ax.fill_between(x, y[i], color='blue', alpha=0.3)

        if (combined):
            plt.figure(figsize=(18, self.plot_height), dpi=self.plot_dpi,
                       facecolor=self.plot_background_color, tight_layout=True)
            plt.tick_params(axis='both', which='both',
                            labelsize=self.plot_fontsize)
            ax = plt.gca()
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_color(self.plot_axis_color)
            ax.spines['left'].set_color(self.plot_axis_color)
            plt.margins(x=0, y=0)
            if not autoscale:
                plt.ylim([ylowerlim, yupperlim])
            for index, parameter in enumerate(parameters):
                # Subplot of figure 1 with id 211 the data (red line r-, first legend = parameter)
                plt.plot(x, y[index], self.lines[index],
                         linewidth=1, label=parameter)
                if fill:
                    plt.fill_between(x, y[index], color='blue', alpha=0.3)
            if zeroline:
                plt.hlines(0, np.amin(x), np.amax(x), linestyles='dashed')
            plt.xlabel('time (s)', fontsize=self.plot_fontsize)
            plt.ylabel(ylabel, fontsize=self.plot_fontsize)
            plt.xticks(fontsize=self.plot_fontsize)
            plt.yticks(fontsize=self.plot_fontsize)
            # Add a legend
            plt.legend(loc='upper center', bbox_to_anchor=(
                0.5, 1.22), ncol=6, fontsize=self.plot_fontsize)
            if fill_between:
                plt.fill_between(x, y[0], y[1], color='blue', alpha=0.1)

        plt.show()

    def find_model_prop(self, prop):
        # split the model from the prop
        t = prop.split(sep=".")
        if (len(t) == 2):
            # try to find the parameter in the model
            if t[0] in self.model.models:
                if (hasattr(self.model.models[t[0]], t[1])):
                    return {'label': prop, 'model': self.model.models[t[0]], 'prop': t[1], 'prop2': None}
        if (len(t) == 3):
            # try to find the parameter in the model
            if t[0] in self.model.models:
                if (hasattr(self.model.models[t[0]], t[1])):
                    return {'label': prop, 'model': self.model.models[t[0]], 'prop': t[1], 'prop2': t[2]}

        return None


class propChange:
    def __init__(self, prop, new_value, in_time, at_time=0, update_interval=0.015):

        self.prop = prop
        self.current_value = getattr(prop['model'], prop['prop'])
        self.initial_value = self.current_value
        self.target_value = new_value
        self.at_time = at_time
        self.in_time = in_time

        if (in_time > 0):
            self.step_size = (
                (self.target_value - self.current_value) / self.in_time) * update_interval
        else:
            self.step_size = 0

        self.update_interval = update_interval
        self.running = False
        self.completed = False
        self.running_time = 0

    def update(self):
        if self.completed == False:
            # check whether the property should start changing (if the at_time has passed)
            if self.running_time >= self.at_time:
                if (self.running == False):
                    print(
                        f"- {self.prop['label']} change started at {self.running_time}. Inital value: {self.initial_value}")
                self.running = True
            else:
                self.running = False

            self.running_time += self.update_interval

            if (self.running):
                self.current_value += self.step_size
                if abs(self.current_value - self.target_value) < abs(self.step_size):
                    self.current_value = self.target_value
                    self.step_size = 0
                    self.running = False
                    self.completed = True

                if (self.step_size == 0):
                    self.current_value = self.target_value
                    self.completed = True
                    print(
                        f"- {self.prop['label']} change stopped at {self.running_time}. New value: {self.current_value}")

                setattr(self.prop['model'],
                        self.prop['prop'], self.current_value)

    def cancel(self):
        self.step_size = 0
        self.current_value = self.initial_value
        self.completed = True
        setattr(self.prop['model'], self.prop['prop'], self.current_value)

    def complete(self):
        self.step_size = 0
        self.current_value = self.target_value
        self.completed = True
        setattr(self.prop['model'], self.prop['prop'], self.current_value)
