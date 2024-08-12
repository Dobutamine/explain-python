import math


class Placenta:
    # static properties
    model_type: str = "Placenta"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.pl_circ_enabled = False
        self.umb_art_diameter = 1.0
        self.umb_art_length = 1.0
        self.umb_ven_diameter = 1.0
        self.umb_ven_length = 1.0
        self.umb_art_res = 30000
        self.umb_art_res_factor = 1.0
        self.umb_ven_res = 30000
        self.umb_ven_res_factor = 1.0
        self.plf_el_base = 5000.0
        self.plf_el_base_factor = 5000.0
        self.plf_u_vol = 0.15
        self.plf_u_vol_factor = 0.15
        self.plm_el_base = 5000.0
        self.plm_el_base_factor = 5000.0
        self.plm_u_vol = 0.5
        self.plm_u_vol_factor = 0.5
        self.diff = 0.01
        self.diff_factor = 1.0
        self.dif_o2 = 0.01
        self.dif_o2_factor = 1.0
        self.dif_co2 = 0.01
        self.dif_co2_factor = 1.0
        self.mat_to2 = 6.5
        self.mat_tco2 = 23.0

        # dependent properties
        self.umb_art_flow = 0.0
        self.umb_art_flow_lmin = 0.0
        self.umb_art_velocity = 0.0
        self.mat_po2 = 0.0
        self.mat_pco2 = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._umb_art = None
        self._umb_ven = None
        self._plm = None
        self._plf = None
        self._pl_gasex = None

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # UMB_ART, UMB_VEN, PLF, PLM, PL_GASEX
        self._umb_art = self._model_engine.models["UMB_ART"]
        self._umb_ven = self._model_engine.models["UMB_VEN"]
        self._plf = self._model_engine.models["PLF"]
        self._plm = self._model_engine.models["PLM"]
        self._pl_gasex = self._model_engine.models["PL_GASEX"]

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        if self.pl_circ_enabled:
            self._umb_art.no_flow = False
            self._umb_ven.no_flow = False

            self._umb_art.r_for = self.umb_art_res
            self._umb_art.r_for_factor = self.umb_art_res_factor

            self._umb_art.r_back = self.umb_art_res
            self._umb_art.r_back_factor = self.umb_art_res_factor

            self._umb_ven.r_for = self.umb_ven_res
            self._umb_ven.r_for_factor = self.umb_ven_res_factor

            self._umb_ven.r_back = self.umb_ven_res
            self._umb_ven.r_back_factor = self.umb_ven_res_factor

            self._plf.el_base = self.plf_el_base
            self._plf.el_base_factor = self.plf_el_base_factor

            self._plf.u_vol = self.plf_u_vol
            self._plf.u_vol_factor = self.plf_u_vol_factor

            self._plm.aboxy["to2"] = self.mat_to2
            self._plm.aboxy["tco2"] = self.mat_tco2

            self._pl_gasex.dif_co2 = self.dif_co2
            self._pl_gasex.dif_o2 = self.dif_o2
            self._pl_gasex.dif_co2_factor = self.dif_co2_factor
            self._pl_gasex.dif_o2_factor = self.dif_co2_factor

            self.mat_po2 = self._plm.aboxy["po2"]
            self.mat_pco2 = self._plm.aboxy["pco2"]

            self.umb_art_flow = self._umb_art.flow
            self.umb_art_flow_lmin = self._umb_art.umb_art_flow_lmin
        else:
            self._umb_art.no_flow = True
            self._umb_ven.no_flow = True
            self.umb_art_flow = 0.0
            self.umb_art_flow_lmin = 0.0
            self.umb_art_velocity = 0.0

            self._umb_art.flow = 0.0
            self._umb_art.flow_lmin = 0.0

            self._umb_ven.flow = 0.0
            self._umb_ven.flow_lmin = 0.0

    def switch_placenta(self, state):
        self.pl_circ_enabled = state
        self._umb_art.is_enabled = state
        self._umb_ven.is_enabled = state
        self._plf.is_enabled = state
        self._plm.is_enabled = state
        self._pl_gasex.is_enabled = state
        self._umb_art.no_flow = not state
        self._umb_ven.no_flow = not state
        if not state:
            self.umb_art_flow = 0.0
            self.umb_art_flow_lmin = 0.0
            self.umb_art_velocity = 0.0

            self._umb_art.flow = 0.0
            self._umb_art.flow_lmin = 0.0

            self._umb_ven.flow = 0.0
            self._umb_ven.flow_lmin = 0.0
