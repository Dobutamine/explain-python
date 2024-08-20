import math


class GasCapacitance:
    # static properties
    model_type: str = "GasCapacitance"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.fixed_composition = False

        # initialize independent properties
        self.u_vol = self.u_vol_factor = self.u_vol_ans_factor = 1.0
        self.u_vol_drug_factor = self.u_vol_scaling_factor = 1.0
        self.el_base = self.el_base_factor = self.el_base_ans_factor = 1.0
        self.el_base_drug_factor = self.el_base_scaling_factor = 1.0
        self.el_k = self.el_k_factor = self.el_k_ans_factor = 1.0
        self.el_k_drug_factor = self.el_k_scaling_factor = 1.0
        self.pres_ext = self.pres_cc = self.pres_atm = self.pres_mus = 0.0
        self.act_factor = self.ans_activity_factor = 1.0

        # initialize dependent properties
        self.vol = 0.0
        self.pres = self.pres_in = self.pres_out = self.pres_tm = 0.0
        self.ctotal = self.co2 = self.cco2 = self.cn2 = self.ch2o = self.cother = 0.0
        self.po2 = self.pco2 = self.pn2 = self.ph2o = self.pother = 0.0
        self.fo2 = self.fco2 = self.fn2 = self.fh2o = self.fother = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._gas_constant = 62.36367

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # add heat to the gas
        self.add_heat()

        # add water vapour to the gas
        self.add_watervapour()

        # Calculate the baseline elastance and unstressed volume
        _el_base = self.el_base * self.el_base_scaling_factor
        _el_k_base = self.el_k * self.el_k_scaling_factor
        _u_vol_base = self.u_vol * self.u_vol_scaling_factor

        # Adjust for factors
        _el = (
            _el_base
            + (self.el_base_factor - 1) * _el_base
            + (self.el_base_ans_factor - 1) * _el_base * self.ans_activity_factor
            + (self.el_base_drug_factor - 1) * _el_base
        )
        _el_k = (
            _el_k_base
            + (self.el_k_factor - 1) * _el_k_base
            + (self.el_k_ans_factor - 1) * _el_k_base * self.ans_activity_factor
            + (self.el_k_drug_factor - 1) * _el_k_base
        )
        _u_vol = (
            _u_vol_base
            + (self.u_vol_factor - 1) * _u_vol_base
            + (self.u_vol_ans_factor - 1) * _u_vol_base * self.ans_activity_factor
            + (self.u_vol_drug_factor - 1) * _u_vol_base
        )

        # calculate the volume difference
        vol_diff = self.vol - _u_vol

        # make the elastances volume dependent
        _el += _el_k * vol_diff * vol_diff

        # Calculate pressures
        self.pres_in = _el * vol_diff
        self.pres_out = self.pres_ext + self.pres_cc + self.pres_mus + self.pres_atm
        self.pres_tm = self.pres_in - self.pres_out
        self.pres = self.pres_in + self.pres_out

        # Reset external pressures
        self.pres_ext = self.pres_cc = self.pres_mus = 0.0

        # calculate the current gas composition
        self.calc_gas_composition()

    def volume_in(self, dvol, comp_from):
        if self.fixed_composition:
            return

        # increase the volume
        self.vol += dvol

        # change the gas concentrations
        if self.vol > 0.0:
            dco2 = (comp_from.co2 - self.co2) * dvol
            self.co2 = (self.co2 * self.vol + dco2) / self.vol

            dcco2 = (comp_from.cco2 - self.cco2) * dvol
            self.cco2 = (self.cco2 * self.vol + dcco2) / self.vol

            dcn2 = (comp_from.cn2 - self.cn2) * dvol
            self.cn2 = (self.cn2 * self.vol + dcn2) / self.vol

            dch2o = (comp_from.ch2o - self.ch2o) * dvol
            self.ch2o = (self.ch2o * self.vol + dch2o) / self.vol

            dcother = (comp_from.cother - self.cother) * dvol
            self.cother = (self.cother * self.vol + dcother) / self.vol

            # change temperature due to influx of gas
            dtemp = (comp_from.temp - self.temp) * dvol
            self.temp = (self.temp * self.vol + dtemp) / self.vol

    def volume_out(self, dvol):
        # do not change the volume if the composition is fixed
        if self.fixed_composition:
            return 0.0

        # guard against negative volumes
        vol_not_removed = max(0.0, -self.vol + dvol)
        self.vol = max(0.0, self.vol - dvol)

        return vol_not_removed

    def add_heat(self):
        # calculate a temperature change depending on the target temperature and the current temperature
        dT = (self.target_temp - self.temp) * 0.0005
        self.temp += dT

        # change the volume as the temperature changes
        if self.pres != 0.0 and self.fixed_composition == False:
            # as Ctotal is in mmol/l we have convert it as the gas constant is in mol
            dV = (self.ctotal * self.vol * self._gas_constant * dT) / self.pres
            self.vol += dV / 1000.0

        # guard against negative volumes
        if self.vol < 0:
            self.vol = 0

    def add_watervapour(self):
        # Calculate water vapour pressure at compliance temperature
        pH2Ot = self.calc_watervapour_pressure()

        # do the diffusion from water vapour depending on the tissue water vapour and gas water vapour pressure
        dH2O = 0.00001 * (pH2Ot - self.ph2o) * self._t
        if self.vol > 0.0:
            self.ch2o = (self.ch2o * self.vol + dH2O) / self.vol

        # as the water vapour also takevol_totals volume this is added to the compliance
        if self.pres != 0.0 and self.fixed_composition == False:
            # as dH2O is in mmol/l we have convert it as the gas constant is in mol
            self.vol += ((self._gas_constant * (273.15 + self.temp)) / self.pres) * (
                dH2O / 1000.0
            )

    def calc_watervapour_pressure(self):
        #   calculate the water vapour pressure in air depending on the temperature
        return math.pow(math.e, 20.386 - 5132 / (self.temp + 273))

    def calc_gas_composition(self):
        # calculate the concentration in mmol/l using the sum of all concentrations
        self.ctotal = self.ch2o + self.co2 + self.cco2 + self.cn2 + self.cother

        # protect against division by zero
        if self.ctotal == 0.0:
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

