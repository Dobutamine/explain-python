from base_models.base_model import BaseModel


class TimeVaryingElastance(BaseModel):
    model_type = "time_varying_elastance"

    def __init__(self, model_ref = {}, name=None):
        # initialize the base model properties
        super().__init__(model_ref=model_ref, name=name)

        # initialize independent properties
        self.u_vol = 0.0  # unstressed volume UV (L)
        self.el_min = 0.0  # minimal elastance Emin (mmHg/L)
        self.el_max = 0.0  # maximal elastance emax(n) (mmHg/L)
        self.el_k = 0.0  # non-linear elastance coefficient K2 (unitless)
        self.pres_ext = 0.0  # non persistent external pressure p2(t) (mmHg)
        self.act_factor = 0.0  # activation factor from the heart model (unitless)
        self.fixed_composition = False  # whether volume composition is fixed

        # non-persistent property factors. These factors reset to 1.0 after each model step
        self.u_vol_factor = 1.0  # non-persistent unstressed volume factor step (unitless)
        self.el_min_factor = 1.0  # non-persistent minimal elastance factor step (unitless)
        self.el_max_factor = 1.0  # non-persistent maximal elastance factor step (unitless)
        self.el_k_factor = 1.0  # non-persistent elastance factor step (unitless)

        # persistent property factors. These factors are persistent and do not reset
        self.u_vol_factor_ps = 1.0  # persistent unstressed volume factor step (unitless)
        self.el_min_factor_ps = 1.0  # persistent minimal elastance factor step (unitless)
        self.el_max_factor_ps = 1.0  # persistent maximal elastance factor step (unitless)
        self.el_k_factor_ps = 1.0  # persistent elastance factor step (unitless)

        # initialize dependent properties
        self.vol = 0.0  # volume v(t) (L)
        self.pres = 0.0  # pressure p1(t) (mmHg)
        self.pres_in = 0.0  # recoil pressure of the elastance (mmHg)
        self.pres_tm = 0.0  # transmural pressure (mmHg)

        # local properties
        self._el_min = 0.0  # calculated minimal elastance (mmHg/L)
        self._el_max = 0.0  # calculated minimal elastance (mmHg/L)
        self._u_vol = 0.0  # calculated unstressed volume (L)
        self._el_k = 0.0  # calculated elastance non-linear k (unitless)

    def calc_model(self):
        # calculate the current elastance and volumes
        self.calc_elastance()
        self.calc_volume()
        
        # if the volume is zero or lower, handle it as a special case to avoid negative volumes
        if self.vol < 0.0:
            # raise a negative volume error
            raise ValueError(f"Volume cannot be negative. Current volume: {self.vol} L in {self.name}")

        # calculate the pressure based on the elastance and volume
        self.calc_pressure()

    def calc_elastance(self):
        # calculate the elastances and non-linear elastance incorporating the factors
        self._el_min = self.el_min + (self.el_min_factor - 1) * self.el_min + (self.el_min_factor_ps - 1) * self.el_min
        self._el_max = self.el_max + (self.el_max_factor - 1) * self.el_max + (self.el_max_factor_ps - 1) * self.el_max
        self._el_k = self.el_k + (self.el_k_factor - 1) * self.el_k + (self.el_k_factor_ps - 1) * self.el_k

        # make sure that el_max is not smaller than el_min
        if self._el_max < self._el_min:
            self._el_max = self._el_min
    
        # reset the non persistent factors
        self.el_min_factor = 1.0
        self.el_max_factor = 1.0
        self.el_k_factor = 1.0

    def calc_volume(self):
        # calculate the unstressed volume incorporating the factors
        self._u_vol = self.u_vol  + (self.u_vol_factor - 1) * self.u_vol + (self.u_vol_factor_ps - 1) * self.u_vol

        # reset the non persistent factors
        self.u_vol_factor = 1.0

    def calc_pressure(self):
        # calculate the recoil pressure
        p_ms = (self.vol - self._u_vol) * self._el_max
        p_ed = self._el_k * (self.vol - self._u_vol) ** 2 + self._el_min * (self.vol - self._u_vol)

        # calculate the current recoil pressure
        self.pres_in = (p_ms - p_ed) * self.act_factor + p_ed

        # calculate the total pressure by incorporating the external pressures
        self.pres = self.pres_in + self.pres_ext

        # calculate the transmural pressure
        self.pres_tm = self.pres_in - self.pres_ext

        # reset the external pressure
        self.pres_ext = 0.0

    def volume_in(self, dvol, comp_from=None):
        if not self.fixed_composition:
            # add volume to the capacitance
            self.vol += dvol

    def volume_out(self, dvol):
        if not self.fixed_composition:
            # remove volume from capacitance
            self.vol -= dvol
