import math
from explain_core.base_models.Capacitance import Capacitance


class GasCapacitance(Capacitance):
    # independent variables
    fixed_composition: bool = False
    target_temp: float = 37.0
    humidity: float = 0.0
    pres_atm: float = 760

    # dependent variables
    c_total: float = 0.0
    c_o2: float = 0.0
    c_co2: float = 0.0
    c_n2: float = 0.0
    c_h2o: float = 0.0
    c_other: float = 0.0
    p_o2: float = 0.0
    p_co2: float = 0.0
    p_n2: float = 0.0
    p_h2o: float = 0.0
    p_other: float = 0.0
    f_o2: float = 0.0
    f_co2: float = 0.0
    f_n2: float = 0.0
    f_h2o: float = 0.0
    f_other: float = 0.0
    temp: float = 0.0
    pres_max: float = -1000.0
    pres_min: float = 1000.0
    pres_mean: float = 0.0
    vol_max: float = -1000.0
    vol_min: float = 1000.0
    tidal_volume = 0.0

    # local parameters
    _gas_constant: float = 62.36367

    # local variables
    _temp_max_pres: float = -1000.0
    _temp_min_pres: float = 1000.0
    _temp_max_vol: float = -1000.0
    _temp_min_vol: float = 1000.0

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # add heat to the gas
        self.add_heat()

        # add water vapour to the gas
        self.add_watervapour()

        # do the cap actions
        super().calc_model()

        # calculate the current gas composition
        self.calc_gas_composition()

        # determine systole and diastole
        if self.pres > self._temp_max_pres:
            self._temp_max_pres = self.pres
        if self.pres < self._temp_min_pres:
            self._temp_min_pres = self.pres

        if self.vol > self._temp_max_vol:
            self._temp_max_vol = self.vol
        if self.vol < self._temp_min_vol:
            self._temp_min_vol = self.vol

        # store min and max
        if self._model.models['Heart'].ncc_ventricular == 0:
            self.pres_max = self._temp_max_pres
            self.pres_min = self._temp_min_pres
            self.pres_mean = self.pres_min + 1 / \
                3 * (self.pres_max - self.pres_min)
            self._temp_min_pres = 1000.0
            self._temp_max_pres = -1000.0

            self.vol_max = self._temp_max_vol
            self.vol_min = self._temp_min_vol
            self.tidal_volume = self.vol_max - self.vol_min
            self._temp_max_vol = -1000
            self._temp_min_vol = 1000

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        # if self gas capacitance has a fixed composition then return
        if self.fixed_composition:
            return

        # execute the parent class method
        super().volume_in(dvol)

        # change the gas composition
        if self.vol <= 0:
            self.vol = 0.0
            self.c_o2 = 0.0
            self.c_co2 = 0.0
            self.c_n2 = 0.0
            self.c_h2o = 0.0
            self.c_other = 0.0
            self.c_total = 0.0
        else:
            # change the gas concentrations
            dc_o2: float = (model_from.c_o2 - self.c_o2) * dvol
            self.c_o2 = (self.c_o2 * self.vol + dc_o2) / self.vol

            dc_co2: float = (model_from.c_co2 - self.c_co2) * dvol
            self.c_co2: float = (self.c_co2 * self.vol + dc_co2) / self.vol

            dc_n2 = (model_from.c_n2 - self.c_n2) * dvol
            self.c_n2 = (self.c_n2 * self.vol + dc_n2) / self.vol

            dc_h2o = (model_from.c_h2o - self.c_h2o) * dvol
            self.c_h2o = (self.c_h2o * self.vol + dc_h2o) / self.vol

            dc_other = (model_from.c_other - self.c_other) * dvol
            self.c_other = (self.c_other * self.vol + dc_other) / self.vol

            # change temperature due to influx of gas
            dtemp = (model_from.temp - self.temp) * dvol
            self.temp = (self.temp * self.vol + dtemp) / self.vol

    def calc_gas_composition(self) -> None:
        # calculate Ctotal sum of all concentrations
        self.c_total = self.c_h2o + self.c_o2 + self.c_co2 + self.c_n2 + self.c_other

        # protect against division by zero
        if self.c_total == 0:
            return

        # calculate the partial pressures
        self.p_h2o = (self.c_h2o / self.c_total) * self.pres
        self.p_o2 = (self.c_o2 / self.c_total) * self.pres
        self.p_co2 = (self.c_co2 / self.c_total) * self.pres
        self.p_n2 = (self.c_n2 / self.c_total) * self.pres
        self.p_other = (self.c_other / self.c_total) * self.pres

        # calculate the fractions
        self.f_h2o = self.c_h2o / self.c_total
        self.f_o2 = self.c_o2 / self.c_total
        self.f_co2 = self.c_co2 / self.c_total
        self.f_n2 = self.c_n2 / self.c_total
        self.f_other = self.c_other / self.c_total

    def calc_watervapour_pressure(self) -> float:
        # calculate the water vapour pressure in air depending on the temperature
        return math.pow(math.e, 20.386 - 5132 / (self.temp + 273))

    def add_watervapour(self) -> None:
        # Calculate water vapour pressure at compliance temperature
        pH2Ot: float = self.calc_watervapour_pressure()

        # do the diffusion from water vapour depending on the tissue water vapour and gas water vapour pressure
        dH2O: float = 0.00001 * (pH2Ot - self.p_h2o) * self._t
        if self.vol > 0:
            self.c_h2o = (self.c_h2o * self.vol + dH2O) / self.vol

        # as the water vapour also takes volume this is added to the compliance
        if self.pres != 0:
            # as dH2O is in mmol/l we have convert it as the gas constant is in mol
            self.vol += ((self._gas_constant * (273.15 + self.temp)
                          ) / self.pres) * (dH2O / 1000.0)

    def add_heat(self) -> None:
        # calculate a temperature change depending on the target temperature and the current temperature
        dT: float = (self.target_temp - self.temp) * 0.0005
        self.temp += dT

        # change the volume as the temperature changes
        if self.pres != 0:
            # as Ctotal is in mmol/l we have convert it as the gas constant is in mol
            dV: float = (self.c_total * self.vol *
                         self._gas_constant * dT) / self.pres
            self.vol += dV / 1000.0

        # guard against negative volumes
        if self.vol < 0:
            self.vol = 0
