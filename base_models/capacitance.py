from base_models.base_model import BaseModel


class Capacitance(BaseModel):
    model_type = "capacitance"

    def __init__(self, model_ref = {}, name=None):
        # initialize the base model properties
        super().__init__(model_ref=model_ref, name=name)

        # initialize independent properties
        self.u_vol = 0.0  # unstressed volume UV (L)
        self.el_base = 0.0  # baseline elastance E (mmHg/L)
        self.el_k = 0.0  # non-linear elastance factor K2 (unitless)
        self.pres_ext = 0.0  # non persistent external pressure p2(t) (mmHg)
        self.fixed_composition = False # whether the composition of the capacitance is fixed (True) or variable (False)

        # non-persistent property factors. These factors reset to 1.0 after each model step
        self.u_vol_factor = 1.0  # non-persistent unstressed volume factor step (unitless)
        self.el_base_factor = 1.0  # non-persistent elastance factor step (unitless)
        self.el_k_factor = 1.0  # non-persistent elastance factor step (unitless)

        # persistent property factors. These factors are persistent and do not reset
        self.u_vol_factor_ps = 1.0  # persistent unstressed volume factor (unitless)
        self.el_base_factor_ps = 1.0  # persistent elastance factor (unitless)
        self.el_k_factor_ps = 1.0  # persistent elastance factor (unitless)

        # initialize dependent properties
        self.vol = 0.0  # volume v(t) (L)
        self.pres = 0.0  # pressure p1(t) (mmHg)
        self.pres_in = 0.0  # recoil pressure of the elastance (mmHg)
        self.pres_tm = 0.0  # transmural pressure (mmHg)

        # local variables
        self._el = 0.0  # calculated elastance (mmHg/L)
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
        # calculate the elastance and non-linear elastance incorporating the factors
        self._el = self.el_base  + (self.el_base_factor - 1) * self.el_base + (self.el_base_factor_ps - 1) * self.el_base
        self._el_k = self.el_k  + (self.el_k_factor - 1) * self.el_k + (self.el_k_factor_ps - 1) * self.el_k

        # reset the non persistent factors
        self.el_base_factor = 1.0
        self.el_k_factor = 1.0  

    def calc_volume(self):
        # calculate the unstressed volume incorporating the factors
        self._u_vol = self.u_vol  + (self.u_vol_factor - 1) * self.u_vol + (self.u_vol_factor_ps - 1) * self.u_vol

        # reset the non persistent factors
        self.u_vol_factor = 1.0

    def calc_pressure(self):
        # calculate the recoil pressure
        self.pres_in = self._el_k * (self.vol - self._u_vol) ** 2 + self._el * (self.vol - self._u_vol)

        # calculate the transmural pressure
        self.pres_tm = self.pres_in - self.pres_ext

        # calculate the total pressure by incorporating the external pressures
        self.pres = self.pres_in + self.pres_ext

        # reset the external pressures
        self.pres_ext = 0.0

    def volume_in(self, dvol, comp_from=None):
        if not self.fixed_composition:
            # add volume to the capacitance
            self.vol += dvol

    def volume_out(self, dvol):
        if not self.fixed_composition:
            # remove volume from capacitance
            self.vol -= dvol
