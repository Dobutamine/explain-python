import math
from explain_core.base_models.BaseModel import BaseModel


class Gas(BaseModel):

    # local constant
    _gas_constant: float = 62.36367

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # set the atmospheric pressure, temperatures and humidities of the gas capacitances
        self.set_atmospheric_pressure()
        self.set_temperatures()
        self.set_humidity()

        # we need a pressure to calculate the composition of the air in the gas capacitances
        for model in self._model.models.values():
            if model.model_type == "GasCapacitance":
                # calculate the pressure
                model.calc_model()

                # calculate the gas composition
                self.set_air_composition(
                    model, self.dry_air['fo2'], self.dry_air['fco2'], self.dry_air['fn2'], self.dry_air['fother'])

        return self._is_initialized

    def set_atmospheric_pressure(self):
        for model in self._model.models.values():
            if model.model_type == "GasCapacitance":
                model.pres_atm = self.pres_atm

    def set_temperatures(self):
        for key, temp in self.temp_settings.items():
            self._model.models[key].temp = temp
            self._model.models[key].target_temp = temp

    def set_humidity(self):
        for key, hum in self.humidity_settings.items():
            self._model.models[key].humidity = hum

    def set_air_composition(self, comp, fo2_dry, fco2_dry, fn2_dry, fother_dry):
        # calculate the concentration at this pressure and temperature in mmol/l using the gas law
        comp.ctotal = (
            comp.pres / (self._gas_constant * (273.15 + comp.temp))) * 1000.0

        # calculate the water vapour pressure, concentration and fraction for this temperature and humidity (0 - 1)
        comp.ph2o = math.pow(math.e, 20.386 - 5132 /
                             (comp.temp + 273)) * comp.humidity
        comp.fh2o = comp.ph2o / comp.pres
        comp.ch2o = comp.fh2o * comp.ctotal

        # calculate the o2 partial pressure, fraction and concentration
        comp.po2 = fo2_dry * (comp.pres - comp.ph2o)
        comp.fo2 = comp.po2 / comp.pres
        comp.co2 = comp.fo2 * comp.ctotal

        # calculate the co2 partial pressure, fraction and concentration
        comp.pco2 = fco2_dry * (comp.pres - comp.ph2o)
        comp.fco2 = comp.pco2 / comp.pres
        comp.cco2 = comp.fco2 * comp.ctotal

        # calculate the n2 partial pressure, fraction and concentration
        comp.pn2 = fn2_dry * (comp.pres - comp.ph2o)
        comp.fn2 = comp.pn2 / comp.pres
        comp.cn2 = comp.fn2 * comp.ctotal

        # calculate the other gas partial pressure, fraction and concentration
        comp.pother = fother_dry * (comp.pres - comp.ph2o)
        comp.fother = comp.pother / comp.pres
        comp.cother = comp.fother * comp.ctotal
