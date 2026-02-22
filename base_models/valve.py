from base_models.base_model import BaseModel


class Valve(BaseModel):
    """Valve flow element with optional no-backflow behavior."""

    model_type = "valve"

    def __init__(self, model_ref = {}, name=None):
        """Initialize valve parameters, state, and connected endpoints."""
        # initialize the base model properties
        super().__init__(model_ref=model_ref, name=name)

        # initialize independent properties
        self.r_for = 1.0  # forward flow resistance Rf (mmHg*s/l)
        self.r_back = 1.0  # backward flow resistance Rb (mmHg*s/l )
        self.r_k = 0.0  # non-linear resistance coefficient K1 (unitless)
        self.l = 0.0  # intertance L (mmHg*s^2/L)
        self.comp_from = ""  # holds the name of the upstream component
        self.comp_to = ""  # holds the name of the downstream component
        self.no_flow = False  # flags whether flow is allowed across this valve
        self.no_back_flow = False  # flags whether backflow is allowed across this valve
        self.p1_ext = 0.0  # external pressure on the inlet (mmHg)
        self.p2_ext = 0.0  # external pressure on the outlet (mmHg)
        self.fixed_composition = False

        # non-persistent property factors. These factors reset to 1.0 after each model step
        self.r_factor = 1.0  # non-persistent resistance factor
        self.r_k_factor = 1.0  # non-persistent non-linear coefficient factor
        self.l_factor = 1.0  # non-persistent inertance factor

        # persistent property factors. These factors are persistent and do not reset
        self.r_factor_ps = 1.0  #  persistent resistance factor
        self.r_k_factor_ps = 1.0  # persistent non-linear coefficient factor
        self.l_factor_ps = 1.0  # persistent inertance factor

        # initialize dependent properties
        self.flow = 0.0  # flow f(t) (L/s)

        # local variables
        self._comp_from = {}  # holds a reference to the upstream component
        self._comp_to = {}  # holds a reference to the downstream component
        self._r_for = 1000  # calculated forward resistance (mmHg/L*s)
        self._r_back = 1000  # calculated backward resistance (mmHg/L*s)
        self._r_k = 0  # calculated non-linear resistance factor (unitless)

    def calc_model(self):
        """Run one valve update step (resolve components, resistance, flow)."""
        # find the up- and downstream components and store the references
        self._comp_from = self.model_ref[self.comp_from]
        self._comp_to = self.model_ref[self.comp_to]

        # calculate the resistances
        self.calc_resistance()

        # calculate the flow
        self.calc_flow()

    def calc_resistance(self):
        """Update effective valve resistance terms from configured factors."""
        # incorporate all factors influencing this valve
        self._r_for = self.r_for  + (self.r_factor - 1) * self.r_for + (self.r_factor_ps - 1) * self.r_for
        self._r_back = self.r_back + (self.r_factor - 1) * self.r_back + (self.r_factor_ps - 1) * self.r_back
        self._r_k = self.r_k + (self.r_k_factor - 1) * self.r_k + (self.r_k_factor_ps - 1) * self.r_k

        # reset the non persistent factors
        self.r_factor = 1.0
        self.r_k_factor = 1.0

    def calc_flow(self):
        """Compute directional valve flow and transfer volume between models."""
        # get the pressure of the volume containing compartments and incorporate the external pressures
        _p1_t = self._comp_from.pres + self.p1_ext
        _p2_t = self._comp_to.pres + self.p2_ext

        # reset the external pressures
        self.p1_ext = 0.0
        self.p2_ext = 0.0

        # reset the current flow
        self.flow = 0.0

        # return if no flow is allowed across this valve
        if self.no_flow:
            self._prev_flow = 0.0
            # return from this function
            return

        # calculate the forward flow between two components
        if _p1_t >= _p2_t:
            # calculate the forward flow
            self.flow = (_p1_t - _p2_t - self._r_k * self.flow ** 2) / self._r_for

            # update the volumes of the connected components but do not remove the volume which could not be removed from the upstream component (to prevent volume loss)
            self._comp_from.volume_out(self.flow * self._t)
            self._comp_to.volume_in(self.flow * self._t, self._comp_from)

            # return from this function
            return

        # calculate the backward flow between two components
        if _p1_t < _p2_t and not self.no_back_flow:
            # calculate the backward flow
            self.flow = (_p1_t - _p2_t + self._r_k * self.flow ** 2) / self._r_back

            # update the volumes of the connected components but do not remove the volume which could not be removed from the upstream component (to prevent volume loss)
            self._comp_to.volume_out(-self.flow * self._t)
            self._comp_from.volume_in(-self.flow * self._t, self._comp_to)

            # return from this function
            return
