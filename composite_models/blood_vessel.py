from derived_models.blood_capacitance import BloodCapacitance
from base_models.resistor import Resistor


class BloodVessel(BloodCapacitance):
    """Composite blood vessel model with embedded input resistors."""

    model_type = "blood_vessel"

    def __init__(self, model_ref={}, name=None):
        """Initialize vessel state, resistance parameters, and connector config."""
        super().__init__(model_ref=model_ref, name=name)

        self.inputs = []
        self.r_for = 1.0
        self.r_back = 1.0
        self.r_k = 0.0
        self.l = 0.0
        self.comp_from = ""
        self.comp_to = ""
        self.no_flow = False
        self.no_back_flow = False
        self.p1_ext = 0.0
        self.p2_ext = 0.0
        self.alpha = 0.0
        self.ans_sens = 0.0
        self.ans_activity = 1.0

        self.r_factor = 1.0
        self.r_k_factor = 1.0
        self.l_factor = 1.0

        self.r_factor_ps = 1.0
        self.r_k_factor_ps = 1.0
        self.l_factor_ps = 1.0

        self.flow = 0.0
        self.flow_forward = 0.0
        self.flow_backward = 0.0
        self.r_current = 0.0
        self.el_current = 0.0

        self._resistors = {}
        self._r_for = 1000.0
        self._r_back = 1000.0
        self._r_k = 0.0
        self._l = 0.0

    def init_model(self, args=None):
        """Initialize vessel and create input connector resistors from `inputs`."""
        super().init_model(args)

        model_registry = self.model_ref if isinstance(self.model_ref, dict) else {}
        if not model_registry and getattr(self, "_model_engine", None) is not None:
            model_registry = getattr(self._model_engine, "models", {})

        model_ref_for_resistor = self._model_engine if getattr(self, "_model_engine", None) is not None else model_registry

        for input_name in self.inputs:
            resistor_name = f"{input_name}_{self.name}"

            if resistor_name in model_registry:
                self._resistors[resistor_name] = model_registry[resistor_name]
                continue

            resistor = Resistor(model_ref=model_ref_for_resistor, name=resistor_name)
            resistor.init_model(
                {
                    "name": resistor_name,
                    "description": f"input connector for {self.name}",
                    "is_enabled": self.is_enabled,
                    "r_for": self.r_for,
                    "r_back": self.r_back,
                    "r_k": self.r_k,
                    "no_flow": self.no_flow,
                    "no_back_flow": self.no_back_flow,
                    "comp_from": input_name,
                    "comp_to": self.name,
                }
            )

            model_registry[resistor_name] = resistor
            self._resistors[resistor_name] = resistor

    def calc_model(self):
        """Run one vessel step and propagate parameters to connector resistors."""
        self.calc_resistances()
        self.calc_elastances()
        self.calc_inertances()

        self.r_current = self._r_for
        self.el_current = self._el

        for resistor in self._resistors.values():
            resistor.r_for = self._r_for
            resistor.r_back = self._r_back
            resistor.r_k = self._r_k

            resistor.no_flow = self.no_flow
            resistor.no_back_flow = self.no_back_flow
            resistor.p1_ext = self.p1_ext
            resistor.p2_ext = self.p2_ext

            resistor.l = self._l
            resistor.r_factor = self.r_factor
            resistor.r_factor_ps = self.r_factor_ps
            resistor.r_k_factor = self.r_k_factor
            resistor.l_factor = self.l_factor
            resistor.l_factor_ps = self.l_factor_ps

        self.calc_volume()

        if self.vol < 0.0:
            raise ValueError(f"Volume cannot be negative. Current volume: {self.vol} L in {self.name}")

        self.calc_pressure()
        self.get_flows()

    def get_flows(self):
        """Aggregate net, forward, and backward flow from all input resistors."""
        self.flow = 0.0
        self.flow_forward = 0.0
        self.flow_backward = 0.0

        for resistor in self._resistors.values():
            if not resistor.is_enabled:
                continue

            if resistor.flow > 0.0:
                self.flow_forward += resistor.flow
            else:
                self.flow_backward += -resistor.flow

        self.flow = self.flow_forward - self.flow_backward

    def calc_inertances(self):
        """Update effective inertance using transient and persistent factors."""
        self._l = self.l + (self.l_factor - 1.0) * self.l + (self.l_factor_ps - 1.0) * self.l
        self.l_factor = 1.0

    def calc_resistances(self):
        """Update effective forward/backward resistance including ANS modulation."""
        self._r_for = (
            self.r_for
            + (self.r_factor - 1.0) * self.r_for
            + (self.r_factor_ps - 1.0) * self.r_for
            + (self.ans_activity - 1.0) * self.r_for * self.ans_sens
        )

        self._r_back = (
            self.r_back
            + (self.r_factor - 1.0) * self.r_back
            + (self.r_factor_ps - 1.0) * self.r_back
            + (self.ans_activity - 1.0) * self.r_back * self.ans_sens
        )

        self._r_k = (
            self.r_k
            + (self.r_k_factor - 1.0) * self.r_k
            + (self.r_k_factor_ps - 1.0) * self.r_k
        )

        self.r_factor = 1.0
        self.r_k_factor = 1.0

    def calc_elastances(self):
        """Update effective elastance terms from factor and ANS contributions."""
        ans_elas_factor = self.ans_activity ** self.alpha
        r_elas_factor = self.r_factor ** self.alpha
        r_ps_elas_factor = self.r_factor_ps ** self.alpha

        self._el = (
            self.el_base
            + (self.el_base_factor - 1.0) * self.el_base
            + (self.el_base_factor_ps - 1.0) * self.el_base
            + (r_elas_factor - 1.0) * self.el_base
            + (r_ps_elas_factor - 1.0) * self.el_base
            + (ans_elas_factor - 1.0) * self.el_base * self.ans_sens
        )

        self._el_k = (
            self.el_k
            + (self.el_k_factor - 1.0) * self.el_k
            + (self.el_k_factor_ps - 1.0) * self.el_k
        )

        self.el_base_factor = 1.0
        self.el_k_factor = 1.0
