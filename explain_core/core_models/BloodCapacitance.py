class BloodCapacitance:
    # static properties
    model_type: str = "BloodCapacitance"
    model_interface: list = []

    # works ssjajskdjks
    def __init__(self, model_ref: object, name: str = ""):
        # initialize independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.fixed_composition = False
        self.analysis_enabled = False
        self.aboxy = {}
        self.solutes = {}
        self.drugs = {}

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
        self.vol = self.vol_max = self.vol_min = self.vol_sv = 0.0
        self.pres = self.pres_in = self.pres_out = self.pres_tm = 0.0
        self.po2 = self.pco2 = self.ph = self.so2 = 0.0
        self.el = 0.0

        # initialize local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
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

        self.el = _el

        # Calculate pressures
        self.pres_in = _el * vol_diff
        self.pres_out = self.pres_ext + self.pres_cc + self.pres_mus + self.pres_atm
        self.pres_tm = self.pres_in - self.pres_out
        self.pres = self.pres_in + self.pres_out

        # Reset external pressures
        self.pres_ext = self.pres_cc = self.pres_mus = 0.0

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
