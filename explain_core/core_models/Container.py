import math


class Container:
    # static properties
    model_type: str = "Container"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.analysis_enabled = False
        self.contained_components = []

        # initialize independent properties
        self.u_vol = self.u_vol_factor = 1.0
        self.u_vol_drug_factor = self.u_vol_scaling_factor = 1.0
        self.vol_extra = 0.0
        self.el_base = self.el_base_factor = 1.0
        self.el_base_drug_factor = self.el_base_scaling_factor = 1.0
        self.el_k = self.el_k_factor = 1.0
        self.el_k_drug_factor = self.el_k_scaling_factor = 1.0
        self.pres_ext = self.pres_cc = self.pres_atm = self.pres_mus = 0.0
        self.act_factor = 1.0

        # dependent properties
        self.vol = self.vol_max = self.vol_min = self.vol_sv = 0.0
        self.pres = self.pres_in = self.pres_out = self.pres_tm = 0.0
        
        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize

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
        # set the starting volume
        self.vol = self.vol_extra

        # get the cummulative volume from all contained models
        for c in self.contained_components:
            self.vol += self._model_engine.models[c].vol

        # Calculate the baseline elastance and unstressed volume
        _el_base = self.el_base * self.el_base_scaling_factor
        _el_k_base = self.el_k * self.el_k_scaling_factor
        _u_vol_base = self.u_vol * self.u_vol_scaling_factor

        # Adjust for factors
        _el = (
            _el_base
            + self.act_factor
            + +(self.el_base_factor - 1) * _el_base
            + (self.el_base_drug_factor - 1) * _el_base
        )
        _el_k = (
            _el_k_base
            + (self.el_k_factor - 1) * _el_k_base
            + (self.el_k_drug_factor - 1) * _el_k_base
        )
        _u_vol = (
            _u_vol_base
            + (self.u_vol_factor - 1) * _u_vol_base
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
        self.act_factor = 0.0

        # transfer the pressures to the models the container contains
        for c in self.contained_components:
            self._model_engine.models[c].pres_ext += self.pres


