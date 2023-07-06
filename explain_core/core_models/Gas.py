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
                    model, self.dry_air['f_o2'], self.dry_air['f_co2'], self.dry_air['f_n2'], self.dry_air['f_other'])

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
        comp.c_total = (
            comp.pres / (self._gas_constant * (273.15 + comp.temp))) * 1000.0

        # calculate the water vapour pressure, concentration and fraction for this temperature and humidity (0 - 1)
        comp.p_h2o = math.pow(math.e, 20.386 - 5132 /
                              (comp.temp + 273)) * comp.humidity
        comp.f_h2o = comp.p_h2o / comp.pres
        comp.c_h2o = comp.f_h2o * comp.c_total

        # calculate the o2 partial pressure, fraction and concentration
        comp.p_o2 = fo2_dry * (comp.pres - comp.p_h2o)
        comp.f_o2 = comp.p_o2 / comp.pres
        comp.c_o2 = comp.f_o2 * comp.c_total

        # calculate the co2 partial pressure, fraction and concentration
        comp.p_co2 = fco2_dry * (comp.pres - comp.p_h2o)
        comp.f_co2 = comp.p_co2 / comp.pres
        comp.c_co2 = comp.f_co2 * comp.c_total

        # calculate the n2 partial pressure, fraction and concentration
        comp.p_n2 = fn2_dry * (comp.pres - comp.p_h2o)
        comp.f_n2 = comp.p_n2 / comp.pres
        comp.c_n2 = comp.f_n2 * comp.c_total

        # calculate the other gas partial pressure, fraction and concentration
        comp.p_other = fother_dry * (comp.pres - comp.p_h2o)
        comp.f_other = comp.p_other / comp.pres
        comp.c_other = comp.f_other * comp.c_total
