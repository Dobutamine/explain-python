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
                                    'model': self.model.models['Heart'], 'prop1': 'ncc_ventricular', 'prop2': None}
            self.ncc_atrial = {'label': 'Heart.ncc_atrial',
                               'model': self.model.models['Heart'], 'prop1': 'ncc_atrial', 'prop2': None}
        except:
            self.ncc_ventricular = {'label': '',
                                    'model': None, 'prop1': '', 'prop2': None}
            self.ncc_atrial = {'label': '',
                               'model': None, 'prop1': '', 'prop2': None}

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

    def set_sample_interval(self, new_interval=0.005):
        self.sample_interval = new_interval

    def add_to_watchlist(self, properties) -> bool:
        # define an return object
        success = True

        # first clear all data
        self.clear_data()

        # check whether property is a string
        if isinstance(properties, str):
            # convert string to a list
            properties = [properties]

        # add to the watchlist
        for prop in properties:
            # check whether the property is already in the watchlist
            duplicate: bool = False
            for wl_item in self.watch_list:
                if wl_item['label'] == prop:
                    duplicate = True
                    break

            # if the property is not yet present then process it
            if not duplicate:
                # process the property as it has shape MODEL.prop1.prop2
                processed_prop = self.find_model_prop(prop)

                # check whether the property is found and if so, add it to the watchlist
                if processed_prop is not None:
                    self.watch_list.append(processed_prop)
                else:
                    success = False

        return success

    def find_model_prop(self, prop):
        # split the model from the prop
        t = prop.split(sep=".")

        # if only 1 property is present
        if (len(t) == 2):
            # try to find the parameter in the model
            if t[0] in self.model.models:
                if (hasattr(self.model.models[t[0]], t[1])):
                    return {'label': prop, 'model': self.model.models[t[0]], 'prop1': t[1], 'prop2': None}

        # if 2 properties are present
        if (len(t) == 3):
            # try to find the parameter in the model
            if t[0] in self.model.models:
                if (hasattr(self.model.models[t[0]], t[1])):
                    return {'label': prop, 'model': self.model.models[t[0]], 'prop1': t[1], 'prop2': t[2]}

        return None

    def collect_data(self, model_clock: float) -> None:
        # collect data at specific intervals set by the sample_interval
        if self._interval_counter >= self.sample_interval:
            # reset the interval counter
            self._interval_counter = 0
            # declare a data object holding the current model time
            data_object: object = {'time': round(model_clock, 4)}
            # process the watch_list
            for parameter in self.watch_list:
                # get the value of the model variable as stated in the watchlist
                prop1 = parameter['prop1']
                prop2 = parameter.get('prop2')
                value = getattr(parameter['model'], prop1)
                if prop2 is not None:
                    value = value.get(prop2, 0)

                # at the value to the data object
                data_object[parameter['label']] = value
            # at the data object to the collected data list
            self.collected_data.append(data_object)
        # increase the interval counter
        self._interval_counter += self.modeling_stepsize
