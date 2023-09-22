
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from pathlib import Path

# import warnings
# warnings.filterwarnings("ignore")


class Interface:
    def __init__(self, model):
        # store a reference to the model instance
        self.model = model

        # get the modeling stepsize from the model
        self._t = model.modeling_stepsize

        # plot line colors
        self.lines = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-', 'w-']

        # define a list holding the prop changes
        self.propChanges = []
        self.prop_update_interval = 0.015
        self.prop_update_counter = 0

        self.output_path = str(os.path.join(Path().absolute())) + r'/'

        self.plot_background_color = '#1E2029'
        self.plot_height = 3
        self.plot_dpi = 300
        self.plot_fontsize = 8
        self.plot_axis_color = 'darkgray'

        # realtime variables
        self.plot_rt_background_color = 'black'
        self.plot_rt_height = 4
        self.plot_rt_dpi = 300
        self.plot_rt_fontsize = 8
        self.plot_rt_axis_color = 'darkgray'

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

  # realtime plotters
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

    def plot_rt(self, properties=["AA.pres"], update_interval=0.2, autoscale=True, autoscale_interval=2.0, combined=True, time_window=5.0, sample_interval=0.005, y_min=0, y_max=100, xy=False):
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
            self.fig_rt, self.animate_rt_graph, init_func=self.init_rt_graph, interval=self.rt_update_interval * 1000.0, blit=True, save_count=50)

        # show the plot
        plt.show()

    def start_rt_graph(self, properties, sampleinterval=0.005):
        # first clear the watchllist and this also clears all data
        self.model._datacollector.clear_watchlist()

        # set the sample interval
        self.model._datacollector.set_sample_interval(sampleinterval)

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
                if (prop != None):
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
                self.x_rt = np.append(self.x_rt, t['time'])
                for idx, parameter in enumerate(self.parameters_rt):
                    self.y_rt[idx][self.no_dp - 1] = t[parameter]
                    self.y_rt[idx] = np.roll(self.y_rt[idx], -1)

    # plotters
    def plot_heart_pv_rt(self):
        self.plot_rt(["LV.vol", "LV.pres"], autoscale=True, autoscale_interval=1.0,
                     time_window=1.0, sample_interval=0.001, xy=True, update_interval=0.1)

    def plot_vitals(self, time_to_calculate=30):
        self.plot_time_graph(["AA.pres", "Heart.heart_rate", "Breathing.resp_rate", "AA.aboxy.so2"], time_to_calculate=time_to_calculate,
                             combined=True, sharey=False, autoscale=True, ylowerlim=0, yupperlim=200, fill=False, fill_between=False)

    def plot_bloodgas(self, time_to_calculate=30):
        self.plot_time_graph(["AA.aboxy.ph", "AA.aboxy.pco2", "AA.aboxy.po2", "AA.aboxy.so2"], time_to_calculate=time_to_calculate,
                             combined=False, sharey=False, fill=False)

    def plot_ans(self, time_to_calculate=10):
        self.plot_time_graph(["AA.aboxy.pco2", "Breathing.target_minute_volume", "Breathing.target_tidal_volume", "Breathing.resp_rate", "Breathing.exp_tidal_volume"], time_to_calculate=time_to_calculate,
                             combined=False, sharey=False, fill=False)

    # lung plotters

    def plot_lung_pressures(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["DS.pres", "ALL.pres", "ALR.pres", "THORAX.pres"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_volumes(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["ALL.vol", "ALR.vol"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_flows(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["MOUTH_DS.flow", "DS_ALL.flow", "DS_ALR.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_pressures_left(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["DS.pres", "ALL.pres"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_volumes_left(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["ALL.vol"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_flows_left(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["MOUTH_DS.flow", "DS_ALL.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_pressures_right(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["DS.pres", "ALR.pres"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_volumes_right(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["ALR.vol"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_lung_flows_right(self, time_to_calculate=10, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["MOUTH_DS.flow", "DS_ALR.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    # heart plotters
    def plot_heart_pressures(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, fill_between=False, analyze=False):
        self.plot_time_graph(["LV.pres", "RV.pres", "LA.pres", "RA.pres", "AA.pres", "PA.pres"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_volumes(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LV.vol", "RV.vol", "LA.vol", "RA.vol"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_flows(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA_LV.flow", "LV_AA.flow", "RA_RV.flow", "RV_PA.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_pressures_left(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LV.pres", "LA.pres", "AA.pres"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_flows_left(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA_LV.flow", "LV_AA.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_volumes_left(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA.vol", "LV.vol"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_flows_right(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RA_RV.flow", "RV_PA.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_volumes_right(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RA.vol", "RV.vol"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_pressures_right(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RV.pres", "RA.pres", "PA.pres"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_left(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["LA.pres", "LV.pres", "LA_LV.flow", "LV_AA.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_heart_right(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["RA.pres", "RV.pres", "RA_RV.flow", "RV_PA.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined,
                             sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_da(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["DA.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_ofo(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["FO.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_shunts(self, time_to_calculate=2, combined=True, sharey=True, autoscale=True, ylowerlim=0, yupperlim=100, fill=True, analyze=False):
        self.plot_time_graph(["DA.flow", "FO.flow"], time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey,
                             sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    def plot_ventilator_curves(self, time_to_calculate=5, combined=False, sharey=False, autoscale=True, ylowerlim=0, yupperlim=100, fill=False, analyze=False):
        self.plot_time_graph(["Ventilator.pres", "Ventilator.flow", "Ventilator.vol", "Ventilator.co2"],
                             time_to_calculate=time_to_calculate, autoscale=True, combined=combined, sharey=sharey, sampleinterval=0.0005, ylowerlim=ylowerlim, yupperlim=yupperlim, fill=fill, fill_between=False, analyze=analyze)

    # getters
    def get_vitals(self, time_to_calculate=10):
        result = self.analyze(["AA.pres", "PA.pres", "IVCI.pres"])

        vitals = {
            "heartrate": self.model.models['Heart'].heart_rate,
            "spo2_pre": self.model.models['AA'].aboxy['so2'],
            "abp_systole": result["AA.pres.max"],
            "abp_diastole": result["AA.pres.min"],
            "pap_systole": result["PA.pres.max"],
            "pap_diastole": result["PA.pres.min"],
            "cvp": result["IVCI.pres.min"] + 0.3333 * (result["IVCI.pres.max"] - result["IVCI.pres.min"]),
            "resp_rate": self.model.models['Breathing'].resp_rate
        }

        return vitals

    def get_gas_flows(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "GasResistor"):
                properties.append(component + ".flow")

        self.analyze(properties, time_to_calculate)

    def get_blood_flows(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "BloodResistor" or component_type == "BloodValve"):
                properties.append(component + ".flow")

        self.analyze(properties, time_to_calculate, sampleinterval=0.0005)

    def get_bloodgas(self, component='AA'):
        bg = self.model.get_bloodgas(component)
        return bg

    def get_blood_pressures(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

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
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "BloodCapacitance" or component_type == "BloodTimeVaryingElastance"):
                properties.append(component + ".vol")

        self.analyze(properties, time_to_calculate)

    def get_gas_pressures(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "GasCapacitance" or component_type == "GasTimeVaryingElastance"):
                properties.append(component + ".pres")

        self.analyze(properties, time_to_calculate)

    def get_gas_volumes(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (component_type == "GasCapacitance" or component_type == "GasTimeVaryingElastance"):
                properties.append(component + ".vol")

        self.analyze(properties, time_to_calculate)

    def analyze(self, properties, time_to_calculate=10, sampleinterval=0.005, calculate=True):
        # define a result object
        result = {}

        # add the ncc ventricular
        properties.insert(0, "Heart.ncc_ventricular")

        # make sure properties is a list
        if (isinstance(properties, str)):
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

        print("")

        no_dp = len(self.model.model_data)
        x = np.zeros(no_dp)
        y = []
        heartbeats = 0

        for parameter in enumerate(properties):
            y.append(np.zeros(no_dp))

        for index, t in enumerate(self.model.model_data):
            x[index] = t['time']

            for idx, parameter in enumerate(properties):
                y[idx][index] = t[parameter]

        sv_message = False
        is_blood = False
        is_gas = False
        is_ventilator = False

        for idx, parameter in enumerate(properties):
            prop_category = parameter.split(sep=".")
            
            # find the modeltype of the property which is needed to be analyzed
            model_type:str = self.model.models[prop_category[0]].model_type
            if "Blood" in model_type:
                is_blood = True

            if model_type == "GasCapacitance" or model_type == "Breathing":
                is_gas = True

            if model_type == "Ventilator":
                is_ventilator = True
            

            if prop_category[1] == "pres":
                data = np.array(y[idx])
                max = round(np.amax(data), 5)
                min = round(np.amin(data), 5)

                # if the modeltype is a blood model type then the unit is mmHg
                # if the modeltype is a gas model type then the unit is cmH2O

                print("{:<16}: max {:10}, min {:10} mmHg". format(
                    parameter, max, min))
                result[parameter + ".max"] = max
                result[parameter + ".min"] = min
                continue

            if prop_category[1] == "vol":
                data = np.array(y[idx])
                max = round(np.amax(data) * 1000, 5)
                min = round(np.amin(data) * 1000, 5)

                print(
                    "{:<16}: max {:10}, min {:10} ml". format(parameter, max, min))
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

                sum = np.sum(data)
                sum_forward = np.sum(data_forward)
                sum_backward = np.sum(data_backward)

                flow = (sum * sampleinterval / (t_end - t_start)) * 60.0
                if is_ventilator:
                    flow = (sum * sampleinterval / (t_end - t_start))
                flow = round(flow, 5)
                flow_forward = 0
                flow_backward = 0

                if (flow != 0.0):
                    flow_forward = (sum_forward / sum) * flow
                    flow_forward = round(flow_forward, 5)

                    flow_backward = (sum_backward / sum) * flow
                    flow_backward = round(flow_backward, 5)

                if is_blood:
                    if (sampleinterval == self.model.modeling_stepsize):
                        # use the no of heartbeats
                        bpm = (heartbeats / (t_end - t_start)) * 60
                    else:
                        if not sv_message:
                            print(f"Stroke volume calculation might be inaccurate. Try using a sampleinterval of {self.model.modeling_stepsize}")
                            sv_message = True
                        bpm = self.model.models['Heart'].heart_rate

                    sv = round(flow / bpm, 5)
                    print("{:16}: net {:10}, forward {:10}, backward {:10} l/min, stroke volume: {:10} l/heartbeat, ". format(
                        parameter, flow, flow_forward, flow_backward, sv))
                
                    result[parameter + ".sv"] = sv
                else:
                    print("{:16}: net {:10}, forward {:10}, backward {:10} l/min".format(
                        parameter, flow, flow_forward, flow_backward))
                
                result[parameter + ".net"] = flow
                result[parameter + ".forward"] = flow_forward
                result[parameter + ".backward"] = flow_backward

                continue

            if prop_category[1] == "ncc_atrial":
                continue

            data = np.array(y[idx])
            max = round(np.amax(data), 5)
            min = round(np.amin(data), 5)
            print("{:<16}: max {:10} min {:10}". format(parameter, max, min))

        return result

    def plot_time_graph(self, properties, time_to_calculate=10,  combined=True, sharey=True, ylabel='',  autoscale=True, ylowerlim=0, yupperlim=100, fill=True, fill_between=False, zeroline=False, sampleinterval=0.005, analyze=True):
        # first clear the watchllist and this also clears all data
        self.model.clear_watchlist()

        # set the sample interval
        self.model.set_sample_interval(sampleinterval)

        # add the property to the watchlist
        if (isinstance(properties, str)):
            properties = [properties]

        # add the properties to the watch_list
        for prop in properties:
            self.model.add_to_watchlist(prop)

        # calculate the model steps
        collected_data = self.model.calculate(time_to_calculate)

        # plot the properties
        self.draw_time_graph(collected_data, properties, sharey, combined, ylabel, autoscale,
                             ylowerlim, yupperlim, fill, fill_between, zeroline)

        # analyze
        if analyze:
            self.analyze(properties, time_to_calculate,
                         sampleinterval, calculate=False)

    def plot_xy_graph(self, property_x, property_y, time_to_calculate=2, sampleinterval=0.0005):
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

    def draw_time_graph(self, collected_data, properties, sharey=False, combined=True, ylabel='', autoscale=True, ylowerlim=0, yupperlim=100, fill=True, fill_between=False, zeroline=False):
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
            x[index] = t['time']

            for idx, parameter in enumerate(parameters):
                y[idx][index] = t[parameter]

        # determine number of needed plots
        plt.style.use('dark_background')
        # set the background color and erase the labels and headers

        if (no_parameters == 1):
            combined = True

        if (combined == False):

            fig, axs = plt.subplots(nrows=no_parameters, ncols=1, figsize=(
                14, self.plot_height * 0.75 * no_parameters), sharex=True, sharey=sharey, constrained_layout=True, dpi=self.plot_dpi/3)
            # Change to the desired color
            fig.patch.set_facecolor(self.plot_background_color)
            fig.set_label('')
            fig.canvas.header_visible = False

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
            fig = plt.figure(figsize=(14, self.plot_height), dpi=self.plot_dpi/3,
                             facecolor=self.plot_background_color, tight_layout=True)
            plt.tick_params(axis='both', which='both',
                            labelsize=self.plot_fontsize)
            fig.patch.set_facecolor(self.plot_background_color)
            fig.set_label('')
            fig.canvas.header_visible = False

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

    def calculate(self, time_to_calculate=30, performance=True):
        t = self.model.calculate(
            time_to_calculate=time_to_calculate, performance=performance)

        print(
            f'Ready in {self.model.run_duration:.1f} sec. Average model step in {self.model.step_duration:.4f} ms.')

    def fastforward(self, time_to_calculate=30, performance=True):
        t = self.model.fastforward(
            time_to_calculate=time_to_calculate, performance=performance)

        print(
            f'Ready in {self.model.run_duration:.1f} sec. Average model step in {self.model.step_duration:.4f} ms.')


class propChange:
    def __init__(self, prop, new_value, in_time, at_time=0, update_interval=0.015):

        self.prop = prop
        self.current_value = getattr(prop['model'], prop['prop'])
        self.initial_value = self.current_value
        self._target_value = new_value
        self.at_time = at_time
        self.in_time = in_time

        if (in_time > 0):
            self.step_size = (
                (self._target_value - self.current_value) / self.in_time) * update_interval
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
                if abs(self.current_value - self._target_value) < abs(self.step_size):
                    self.current_value = self._target_value
                    self.step_size = 0
                    self.running = False
                    self.completed = True

                if (self.step_size == 0):
                    self.current_value = self._target_value
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
        self.current_value = self._target_value
        self.completed = True
        setattr(self.prop['model'], self.prop['prop'], self.current_value)


    # def write_to_excel(self, properties, filename='data', time_to_calculate=10, sampleinterval=0.005, calculate=True):
    #     self.analyze(properties, time_to_calculate=time_to_calculate,
    #                  sampleinterval=sampleinterval, calculate=calculate)
    #     # build a parameter list
    #     parameters = ['time']
    #     for p in properties:
    #         parameters.append(p)

    #     data = []
    #     for index, t in enumerate(self.model.model_data):
    #         dataline = []
    #         for idx, parameter in enumerate(parameters):
    #             dataline.append(t[parameter])
    #         data.append(dataline)

    #     df = pd.DataFrame(data, columns=parameters)
    #     path = self.output_path + filename + '.xlsx'
    #     df.to_excel(path)