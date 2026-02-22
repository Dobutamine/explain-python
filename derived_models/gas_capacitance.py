import math

from base_models.capacitance import Capacitance


class GasCapacitance(Capacitance):
    """Gas compartment with pressure, temperature, and gas-fraction dynamics."""

    model_type = "gas_capacitance"

    def __init__(self, model_ref={}, name=None):
        """Initialize gas capacitance thermodynamic and composition properties."""
        super().__init__(model_ref=model_ref, name=name)

        self.pres_atm = 760.0
        self.pres_cc = 0.0
        self.pres_mus = 0.0
        self.fixed_composition = False
        self.target_temp = 0.0

        self.ctotal = 0.0
        self.co2 = 0.0
        self.cco2 = 0.0
        self.cn2 = 0.0
        self.cother = 0.0
        self.ch2o = 0.0

        self.po2 = 0.0
        self.pco2 = 0.0
        self.pn2 = 0.0
        self.pother = 0.0
        self.ph2o = 0.0

        self.fo2 = 0.0
        self.fco2 = 0.0
        self.fn2 = 0.0
        self.fother = 0.0
        self.fh2o = 0.0

        self.temp = 0.0
        self.humidity = 0.0
        self.pres_rel = 0.0

        self._gas_constant = 62.36367

    def calc_model(self):
        """Run one gas compartment step (heat, vapor, pressure, composition)."""
        self.add_heat()
        self.add_watervapour()

        self.calc_elastance()
        self.calc_volume()

        if self.vol < 0.0:
            raise ValueError(f"Volume cannot be negative. Current volume: {self.vol} L in {self.name}")

        self.calc_pressure()
        self.calc_gas_composition()

    def calc_pressure(self):
        """Compute pressure including atmospheric and external contributors."""
        super().calc_pressure()

        self.pres = self.pres + self.pres_cc + self.pres_mus + self.pres_atm
        self.pres_rel = self.pres - self.pres_atm

        self.pres_cc = 0.0
        self.pres_mus = 0.0

    def volume_in(self, dvol, comp_from=None):
        """Add incoming volume and mix gas composition from source compartment."""
        super().volume_in(dvol)

        if comp_from is None or self.vol <= 0.0:
            return

        self.co2 = (self.co2 * self.vol + (getattr(comp_from, "co2", self.co2) - self.co2) * dvol) / self.vol
        self.cco2 = (self.cco2 * self.vol + (getattr(comp_from, "cco2", self.cco2) - self.cco2) * dvol) / self.vol
        self.cn2 = (self.cn2 * self.vol + (getattr(comp_from, "cn2", self.cn2) - self.cn2) * dvol) / self.vol
        self.ch2o = (self.ch2o * self.vol + (getattr(comp_from, "ch2o", self.ch2o) - self.ch2o) * dvol) / self.vol
        self.cother = (self.cother * self.vol + (getattr(comp_from, "cother", self.cother) - self.cother) * dvol) / self.vol

        self.temp = (self.temp * self.vol + (getattr(comp_from, "temp", self.temp) - self.temp) * dvol) / self.vol

    def add_heat(self):
        """Move temperature toward target and adjust volume accordingly."""
        dtemp = (self.target_temp - self.temp) * 0.0005
        self.temp += dtemp

        if self.pres != 0.0 and not self.fixed_composition:
            dvol = (self.ctotal * self.vol * self._gas_constant * dtemp) / self.pres
            self.vol += dvol / 1000.0

        if self.vol < 0.0:
            self.vol = 0.0

    def add_watervapour(self):
        """Add/remove water vapor toward temperature-dependent equilibrium."""
        ph2o_target = self.calc_watervapour_pressure()
        time_step = getattr(self, "_t", 0.0)
        dh2o = 0.00001 * (ph2o_target - self.ph2o) * time_step

        if self.vol > 0.0:
            self.ch2o = (self.ch2o * self.vol + dh2o) / self.vol

        if self.pres != 0.0 and not self.fixed_composition:
            self.vol += ((self._gas_constant * (273.15 + self.temp)) / self.pres) * (dh2o / 1000.0)

    def calc_watervapour_pressure(self):
        """Return saturated water vapor pressure (mmHg) for current temperature."""
        return math.exp(20.386 - 5132.0 / (self.temp + 273.0))

    def calc_gas_composition(self):
        """Recompute partial pressures and fractions from gas concentrations."""
        self.ctotal = self.ch2o + self.co2 + self.cco2 + self.cn2 + self.cother

        if self.ctotal == 0.0:
            return

        self.ph2o = (self.ch2o / self.ctotal) * self.pres
        self.po2 = (self.co2 / self.ctotal) * self.pres
        self.pco2 = (self.cco2 / self.ctotal) * self.pres
        self.pn2 = (self.cn2 / self.ctotal) * self.pres
        self.pother = (self.cother / self.ctotal) * self.pres

        self.fh2o = self.ch2o / self.ctotal
        self.fo2 = self.co2 / self.ctotal
        self.fco2 = self.cco2 / self.ctotal
        self.fn2 = self.cn2 / self.ctotal
        self.fother = self.cother / self.ctotal
