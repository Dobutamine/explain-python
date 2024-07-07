class BloodPump:
    # static properties
    model_type: str = "BloodPump"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # initialize independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.fixed_composition = False
        self.aboxy = {}
        self.solutes = {}
        self.drugs = {}
        self.pump_mode = 0  # 0 = centrifugal, 1 = roller pump
        self.pump_pressure = 0.0
        self.pump_rpm = 0.0
        self.inlet = ""
        self.outlet = ""

        # initialize independent properties
        self.u_vol = self.u_vol_factor = self.u_vol_scaling_factor = 1.0
        self.el_base = self.el_base_factor = self.el_base_scaling_factor = 1.0
        self.el_k = self.el_k_factor = self.el_k_scaling_factor = 1.0
        self.pres_ext = self.pres_atm = 0.0

        # initialize dependent properties
        self.vol = self.vol_max = self.vol_min = self.vol_sv = 0.0
        self.pres = self.pres_in = self.pres_out = self.pres_tm = 0.0
        self.pres_max = self.pres_min = self.pres_mean = 0.0

        # initialize local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False
        self._heart = None
        self._inlet_res = None
        self._outlet_res = None
        self._temp_pres_max = -1000.0
        self._temp_pres_min = 1000.0
        self._temp_vol_max = -1000.0
        self._temp_vol_min = 1000.0
        self._analytics_timer = 0.0
        self._analytics_window = 2.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
        for key, value in args.items():
            setattr(self, key, value)

        # get the reference to the heart model
        self._heart = self._model_engine.models["Heart"]

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    def connect_pump(self, _in, _out):
        if type(_in) == str:
            self._inlet_res = self._model_engine.models[_in]
        else:
            self._inlet_res = _in

        if type(_out) == str:
            self._outlet_res = self._model_engine.models[_out]
        else:
            self._outlet_res = _out

    # actual model calculations are done here
    def calc_model(self):
        # conect the pump if not already connected
        if not self._inlet_res or not self._outlet_res:
            self.connect_pump(self.inlet, self.outlet)

        # Calculate the baseline elastance and unstressed volume
        _el_base = self.el_base * self.el_base_scaling_factor
        _el_k_base = self.el_k * self.el_k_scaling_factor
        _u_vol_base = self.u_vol * self.u_vol_scaling_factor

        # Adjust for factors
        _el = _el_base + (self.el_base_factor - 1) * _el_base
        _el_k = _el_k_base + (self.el_k_factor - 1) * _el_k_base
        _u_vol = _u_vol_base + (self.u_vol_factor - 1) * _u_vol_base

        # calculate the volume difference
        vol_diff = self.vol - _u_vol

        # make the elastances volume dependent
        _el += _el_k * vol_diff * vol_diff

        # Calculate pressures
        self.pres_in = _el * vol_diff
        self.pres_out = self.pres_ext + self.pres_atm
        self.pres_tm = self.pres_in - self.pres_out
        self.pres = self.pres_in + self.pres_out

        # Analyze pressure and volume values
        self.analyze()

        # Reset external pressures
        self.pres_ext = 0.0

        # apply the pump pressures to the connected resistors
        self.pump_pressure = -self.pump_rpm / 25.0

        if self.pump_mode == 0:
            self._inlet_res.p1_ext = 0.0
            self._inlet_res.p2_ext = self.pump_pressure
        else:
            self._outlet_res.p1_ext = self.pump_pressure
            self._outlet_res.p2_ext = 0.0

    def volume_in(self, dvol, comp_from):
        # return if the capacitance is fixed
        if self.fixed_composition:
            return

        # increase the volume
        self.vol += dvol

        # return if the volume is zero or lower
        if self.vol <= 0.0:
            return

        # process the solutes and drugs
        for solute, conc in self.solutes.items():
            self.solutes[solute] += (
                (comp_from.solutes[solute] - conc) * dvol
            ) / self.vol

        for drug, conc in self.drugs.items():
            self.drugs[drug] += ((comp_from.drugs[drug] - conc) * dvol) / self.vol

        # process the aboxy relevant properties
        ab_solutes = ["to2", "tco2", "hemoglobin", "albumin"]
        for ab_sol in ab_solutes:
            self.aboxy[ab_sol] += (
                (comp_from.aboxy[ab_sol] - self.aboxy[ab_sol]) * dvol
            ) / self.vol

    def volume_out(self, dvol):
        # do not change the volume if the composition is fixed
        if self.fixed_composition:
            return 0.0

        # guard against negative volumes
        vol_not_removed = max(0.0, -self.vol + dvol)
        self.vol = max(0.0, self.vol - dvol)

        return vol_not_removed

    def analyze(self):
        self._temp_pres_max = max(self.pres, self._temp_pres_max)
        self._temp_pres_min = min(self.pres, self._temp_pres_min)
        self._temp_vol_max = max(self.vol, self._temp_vol_max)
        self._temp_vol_min = min(self.vol, self._temp_vol_min)

        if (
            self._analytics_timer >= self._analytics_window
            or self._heart.ncc_ventricular == 1
        ):
            self.pres_max = self._temp_pres_max
            self.pres_min = self._temp_pres_min
            self.pres_mean = (2.0 * self.pres_min + self.pres_max) / 3.0
            self.vol_max = self._temp_vol_max
            self.vol_min = self._temp_vol_min
            self.vol_sv = self.vol_max - self.vol_min

            self._temp_pres_max = -1000.0
            self._temp_pres_min = 1000.0
            self._temp_vol_max = -1000.0
            self._temp_vol_min = 1000.0
            self._analytics_timer = 0.0

        # increase the analytics timer with the modeling stepsize
        self._analytics_timer += self._t
