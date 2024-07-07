import math
from explain_core.helpers.GasComposition import set_gas_composition


class Gas:
    # static properties
    model_type: str = "Gas"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.gas_containing_components: list = []
        self.humidity_settings = None
        self.temp_settings = None
        self.pres_atm = 760.0
        self.fio2 = 0.21
        self.humidity = 0.5
        self.temp = 20.0

        # dependent properties
        self.total_gas_volume = 0.0
        self.po2_alv = self.pco2_alv = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._gas_constant = 62.36367
        self._update_interval = 2.0
        self._update_counter = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # set the atmospheric pressure in all gas capacitances
        for model_name in self.gas_containing_components:
            self._model_engine.models[model_name].pres_atm = self.pres_atm

        # set the temperatures
        for model_name, temp in self.temp_settings.items():
            if self._model_engine.models[model_name].temp == 0.0:
                self._model_engine.models[model_name].temp = temp
                self._model_engine.models[model_name].target_temp = temp

        # set the humidity
        for model_name, humidity in self.humidity_settings.items():
            if self._model_engine.models[model_name].humidity == 0.0:
                self._model_engine.models[model_name].humidity = humidity

        # calculate the gas composition if not done set already
        for model_name in self.gas_containing_components:
            if self._model_engine.models[model_name].co2 == 0.0:
                set_gas_composition(
                    self._model_engine.models[model_name],
                    self.fio2,
                    self._model_engine.models[model_name].temp,
                    self._model_engine.models[model_name].humidity,
                )

        # get the current total gas volume
        self.total_gas_volume = self.get_total_gas_volume()

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        if self._update_counter > self._update_interval:
            self._update_counter = 0.0

            self.temp = self._model_engine.models["OUT"].temp
            self.humidity = self._model_engine.models["OUT"].humidity

            self.get_total_gas_volume()

        self._update_counter += self._t

    # calculate the total gas volume
    def get_total_gas_volume(self):
        total_volume = 0.0
        for model_name in self.gas_containing_components:
            if self._model_engine.models[model_name].is_enabled:
                total_volume += self._model_engine.models[model_name].vol

        return total_volume

    def set_total_gas_volume(self, new_gas_volume):
        current_volume = self.get_total_gas_volume()
        gas_volume_change = new_gas_volume / current_volume

        for model in self.gas_containing_components:
            m = self._model_engine.models[model]
            if m.is_enabled and not m.fixed_composition:
                m.vol = m.vol * gas_volume_change
                m.u_vol = m.u_vol * gas_volume_change

    def set_new_atmospheric_pressure(self, new_p_atm):
        if new_p_atm > 0.0:
            self.pres_atm = new_p_atm
            for model in self.gas_containing_components:
                self._model_engine.models[model].pres_atm = self.pres_atm

    def set_new_temperature(self, new_temp, sites=["OUT", "MOUTH"]):
        if type(sites) == str:
            sites = [sites]

        if new_temp >= 0.0 and new_temp <= 100.0:
            for site in sites:
                self.temp_settings[site] = new_temp
                self._model_engine.models[site].temp = self.temp
                self._model_engine.models[site].target_temp = self.temp
                set_gas_composition(
                    self._model_engine.models[site],
                    self.fio2,
                    new_temp,
                    self._model_engine.models[site].humidity,
                )

    def set_new_fio2(self, new_fio2, sites=["OUT", "MOUTH"]):
        if type(sites) == str:
            sites = [sites]

        if new_fio2 >= 0.21 and new_fio2 <= 1.0:
            for site in sites:
                self.fio2 = new_fio2
                set_gas_composition(
                    self._model_engine.models[site],
                    self.fio2,
                    self._model_engine.models[site].temp,
                    self._model_engine.models[site].humidity,
                )

    def set_new_humidity(self, new_humidity, sites=["OUT", "MOUTH"]):
        if type(sites) == str:
            sites = [sites]

        if new_humidity >= 0.0 and new_humidity <= 1.0:
            for site in sites:
                self.humidity_settings[site] = new_humidity
                self._model_engine.models[site].humidity = self.new_humidity
                set_gas_composition(
                    self._model_engine.models[site],
                    self.fio2,
                    self._model_engine.models[site].temp,
                    new_humidity,
                )
