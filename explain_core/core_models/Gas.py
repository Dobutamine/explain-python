import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.functions.GasComposition import calc_gas_composition


class Gas(BaseModel):
    # local constant
    _gas_constant: float = 62.36367

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # set the atmospheric pressure, temperatures and humidities of the gas capacitances
        self.set_atmospheric_pressure()
        self.set_temperatures()
        self.set_humidity()

        # we need a pressure to calculate the composition of the gas in the gas capacitances
        for model in self._model.models.values():
            if model.model_type == "GasCapacitance":
                # calculate the pressure
                model.calc_model()

                # calculate the gas composition
                result = calc_gas_composition(
                    model, self.fio2, model.temp, model.humidity
                )

                # process the result
                for key, value in result.items():
                    setattr(model, key, value)

        return self._is_initialized

    # return the total blood volume
    def get_total_gas_volume(self, output=True) -> float:
        total_gas_volume: float = 0.0

        for model in self._model.models.values():
            if model.model_type == "GasCapacitance":
                if model.is_enabled and not model.fixed_composition:
                    try:
                        total_gas_volume += model.vol
                        print(f"{model.name}: {model.vol}")
                    except:
                        total_gas_volume += 0.0

        if output:
            print(
                f"Total gas volume = {total_gas_volume * 1000.0} ml ({total_gas_volume * 1000.0 / self._model.weight} ml/kg)"
            )

        return total_gas_volume

    def calc_model(self) -> None:
        pass

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
