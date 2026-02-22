from derived_models.blood_capacitance import BloodCapacitance


class Pump(BloodCapacitance):
    model_type = "pump"

    def __init__(self, model_ref={}, name=None):
        super().__init__(model_ref=model_ref, name=name)

        self.inlet = ""  # name of inlet resistor/valve component
        self.outlet = ""  # name of outlet resistor/valve component
        self.pump_rpm = 0.0  # pump speed in rotations per minute
        self.pump_mode = 0  # 0 = centrifugal (acts on inlet outlet side), 1 = roller
        self.pump_pressure = 0.0  # generated pump pressure (mmHg)

        self.pres_cc = 0.0  # non-persistent pressure contribution (mmHg)
        self.pres_mus = 0.0  # non-persistent pressure contribution (mmHg)

        self._inlet = None  # reference to inlet flow component
        self._outlet = None  # reference to outlet flow component

    def _resolve_component(self, component_name):
        if not component_name:
            return None

        if isinstance(self.model_ref, dict) and component_name in self.model_ref:
            return self.model_ref[component_name]

        model_engine = getattr(self, "_model_engine", None)
        if model_engine is not None:
            models = getattr(model_engine, "models", None)
            if isinstance(models, dict):
                return models.get(component_name)

        return None

    def calc_pressure(self):
        self._inlet = self._resolve_component(self.inlet)
        self._outlet = self._resolve_component(self.outlet)

        self.pres_in = self._el_k * (self.vol - self._u_vol) ** 2 + self._el * (self.vol - self._u_vol)
        self.pres_tm = self.pres_in - self.pres_ext
        self.pres = self.pres_in + self.pres_ext + self.pres_cc + self.pres_mus

        self.pres_ext = 0.0
        self.pres_cc = 0.0
        self.pres_mus = 0.0

        self.pump_pressure = -self.pump_rpm / 25.0

        if self.pump_mode == 0:
            if self._inlet is not None:
                self._inlet.p1_ext = 0.0
                self._inlet.p2_ext = self.pump_pressure
        else:
            if self._outlet is not None:
                self._outlet.p1_ext = self.pump_pressure
                self._outlet.p2_ext = 0.0
