import math
from explain_core.base_models.Capacitance import Capacitance


class GasCapacitance(Capacitance):
    # independent variables
    fixed_composition: bool = False
    target_temp: float = 37.0
    humidity: float = 0.0
    pres_atm: float = 760

    # dependent variables
    ctotal: float = 0.0
    co2: float = 0.0
    cco2: float = 0.0
    cn2: float = 0.0
    ch2o: float = 0.0
    cother: float = 0.0
    po2: float = 0.0
    pco2: float = 0.0
    pn2: float = 0.0
    ph2o: float = 0.0
    pother: float = 0.0
    fo2: float = 0.0
    fco2: float = 0.0
    fn2: float = 0.0
    fh2o: float = 0.0
    fother: float = 0.0
    temp: float = 0.0
    pres_max: float = -1000.0
    pres_min: float = 1000.0
    pres_mean: float = 0.0
    vol_max: float = -1000.0
    vol_min: float = 1000.0
    tidal_volume = 0.0

    # local parameters
    _gas_constant: float = 62.36367

    # override the calc_model method as the blood capacitance has some specific actions
    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # add heat to the gas
        self.add_heat()

        # add water vapour to the gas
        self.add_watervapour()

        # do the cap actions
        super().calc_model()

        # calculate the current gas composition
        self.calc_gas_composition()

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        # if self gas capacitance has a fixed composition then return
        if self.fixed_composition:
            return

        # execute the parent class method
        super().volume_in(dvol)

        # change the gas concentrations
        dco2: float = (model_from.co2 - self.co2) * dvol
        self.co2 = (self.co2 * self.vol + dco2) / self.vol

        dcco2: float = (model_from.cco2 - self.cco2) * dvol
        self.cco2: float = (self.cco2 * self.vol + dcco2) / self.vol

        dcn2 = (model_from.cn2 - self.cn2) * dvol
        self.cn2 = (self.cn2 * self.vol + dcn2) / self.vol

        dch2o = (model_from.ch2o - self.ch2o) * dvol
        self.ch2o = (self.ch2o * self.vol + dch2o) / self.vol

        dcother = (model_from.cother - self.cother) * dvol
        self.cother = (self.cother * self.vol + dcother) / self.vol

        # change temperature due to influx of gas
        dtemp = (model_from.temp - self.temp) * dvol
        self.temp = (self.temp * self.vol + dtemp) / self.vol

    def calc_gas_composition(self) -> None:
        # calculate the concentration in mmol/l using the sum of all concentrations
        self.ctotal = self.ch2o + self.co2 + self.cco2 + self.cn2 + self.cother

        # protect against division by zero
        if self.ctotal == 0:
            return

        # calculate the partial pressures
        self.ph2o = (self.ch2o / self.ctotal) * self.pres
        self.po2 = (self.co2 / self.ctotal) * self.pres
        self.pco2 = (self.cco2 / self.ctotal) * self.pres
        self.pn2 = (self.cn2 / self.ctotal) * self.pres
        self.pother = (self.cother / self.ctotal) * self.pres

        # calculate the fractions
        self.fh2o = self.ch2o / self.ctotal
        self.fo2 = self.co2 / self.ctotal
        self.fco2 = self.cco2 / self.ctotal
        self.fn2 = self.cn2 / self.ctotal
        self.fother = self.cother / self.ctotal

    def calc_watervapour_pressure(self) -> float:
        # calculate the water vapour pressure in air depending on the temperature
        return math.pow(math.e, 20.386 - 5132 / (self.temp + 273))

    def add_watervapour(self) -> None:
        # Calculate water vapour pressure at compliance temperature
        pH2Ot: float = self.calc_watervapour_pressure()

        # do the diffusion from water vapour depending on the tissue water vapour and gas water vapour pressure
        dH2O: float = 0.00001 * (pH2Ot - self.ph2o) * self._t
        self.ch2o = (self.ch2o * self.vol + dH2O) / self.vol

        # as the water vapour also takevol_totals volume this is added to the compliance
        if self.pres != 0 and not self.fixed_composition:
            # as dH2O is in mmol/l we have convert it as the gas constant is in mol
            self.vol += ((self._gas_constant * (273.15 + self.temp)) / self.pres) * (
                dH2O / 1000.0
            )

    def add_heat(self) -> None:
        # calculate a temperature change depending on the target temperature and the current temperature
        dT: float = (self.target_temp - self.temp) * 0.0005
        self.temp += dT

        # change the volume as the temperature changes
        if self.pres != 0 and not self.fixed_composition:
            # as Ctotal is in mmol/l we have convert it as the gas constant is in mol
            dV: float = (
                self.ctotal * self.vol * self._gas_constant * dT
            ) / self.pres
            self.vol += dV / 1000.0

        # guard against negative volumes
        if self.vol < 0:
            self.vol = 0
