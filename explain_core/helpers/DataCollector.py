import math


class DataCollector:
    def __init__(self, model):

        # store a reference to the model instance
        self.model = model

        # define the watch list
        self.watch_list = []

        # define the data sample interval
        self.sample_interval = 0.005
        self._interval_counter = 0

        # get the modeling stepsize from the model
        self.modeling_stepsize = model.modeling_stepsize

        # try to add two always needed ecg properties to the watchlist
        try:
            self.ncc_ventricular = {'label': 'Heart.ncc_ventricular',
                                    'model': self.model.models['Heart'], 'prop': 'ncc_ventricular', 'prop2': None}
            self.ncc_atrial = {'label': 'Heart.ncc_atrial',
                               'model': self.model.models['Heart'], 'prop': 'ncc_atrial', 'prop2': None}
        except:
            self.ncc_ventricular = {'label': '',
                                    'model': None, 'prop': '', 'prop2': None}
            self.ncc_atrial = {'label': '',
                               'model': None, 'prop': '', 'prop2': None}

        # add the two always there
        self.watch_list.append(self.ncc_atrial)
        self.watch_list.append(self.ncc_ventricular)

        # define the data list
        self.collected_data = []

    def clear_data(self):
        self.collected_data = []

    def clear_watchlist(self):
        # first clear all data
        self.clear_data()

        # empty the watch list
        self.watch_list = []

        # add the two always there
        self.watch_list.append(self.ncc_atrial)
        self.watch_list.append(self.ncc_ventricular)

    def set_sample_interval(self, new_interval):
        self.sample_interval = new_interval

    def add_to_watchlist(self, property):

        # first clear all data
        self.clear_data()

        # add to the watchlist
        self.watch_list.append(property)

    def collect_data(self, model_clock):
        # self._interval_counter += self.modeling_stepsize
        if self._interval_counter >= self.sample_interval:
            self._interval_counter = 0
            data_object = {'time': model_clock}

            for parameter in self.watch_list:
                prop = parameter['prop']
                prop2 = parameter.get('prop2')
                weight = self.model.weight if prop in ('flow', 'vol') else 1
                time = 60 if prop == 'flow' else 1

                if parameter['model'] is not None:
                    value = getattr(parameter['model'], prop)
                    if prop2 is not None:
                        value = value.get(prop2, 0)

                    data_object[parameter['label']] = value / weight * time

            self.collected_data.append(data_object)

        self._interval_counter += self.modeling_stepsize
