import math


class GasResistor:
    # static properties
    model_type: str = "GasResistor"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # initialize independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.analysis_enabled = False
        self.no_flow: bool = True
        self.no_back_flow: bool = True
        self.comp_from: str = ""
        self.comp_to: str = ""
        self.r_for = self.r_for_factor = 1.0
        self.r_back = self.r_back_factor = 1.0
        self.r_k = self.r_k_factor = 1.0
        self.r_ans_factor = self.r_mob_factor = self.r_drug_factor = 1.0
        self.r_scaling_factor = 1.0
        self.ans_activity_factor = self.act_factor = 0.0
        self.p1_ext = self.p2_ext = 0.0
        self.p1_ext_factor = self.p2_ext_factor = 0.0

        # initialize dependent properties
        self.flow = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False
        self._model_comp_from = None
        self._model_comp_to = None

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the connected components
        if type(self.comp_from) == str:
            self._model_comp_from = self._model_engine.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) == str:
            self._model_comp_to = self._model_engine.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        #  get the pressures of the connected model components
        _p1 = self._model_comp_from.pres + self.p1_ext * self.p1_ext_factor
        _p2 = self._model_comp_to.pres + self.p2_ext * self.p2_ext_factor

        # reset the external pressures
        self.p1_ext = 0
        self.p2_ext = 0

        # calculate the resistances
        _r_for_base = self.r_for * self.r_scaling_factor
        _r_back_base = self.r_back * self.r_scaling_factor
        _r_k_base = self.r_k * self.r_scaling_factor

        _r_for = (
            _r_for_base
            + (self.r_for_factor - 1) * _r_for_base
            + ((self.r_ans_factor - 1) * _r_for_base) * self.ans_activity_factor
            + (self.r_mob_factor - 1) * _r_for_base
            + (self.r_drug_factor - 1) * _r_for_base
        )

        _r_back = (
            _r_back_base
            + (self.r_back_factor - 1) * _r_back_base
            + ((self.r_ans_factor - 1) * _r_back_base) * self.ans_activity_factor
            + (self.r_mob_factor - 1) * _r_back_base
            + (self.r_drug_factor - 1) * _r_back_base
        )

        _r_k = (
            _r_k_base
            + (self.r_k_factor - 1) * _r_k_base
            + ((self.r_ans_factor - 1) * _r_k_base) * self.ans_activity_factor
            + (self.r_mob_factor - 1) * _r_k_base
            + (self.r_drug_factor - 1) * _r_k_base
        )

        # make the resistances flow dependent
        _r_for += _r_k * self.flow * self.flow
        _r_back += _r_k * self.flow * self.flow

        # guard for too small resistances
        _r_for = max(_r_for, 20.0)
        _r_back = max(_r_back, 20.0)

        # calculate flow
        if self.no_flow or (_p1 <= _p2 and self.no_back_flow):
            self.flow = 0.0
        elif _p1 > _p2:
            # forward flow
            self.flow = (_p1 - _p2) / _r_for
        else:
            # back flow
            self.flow = (_p1 - _p2) / _r_back

        # Update the volumes of the model components connected by this resistor
        vol_not_removed = 0.0
        if self.flow > 0:
            # Flow is from comp_from to comp_to
            vol_not_removed = self._model_comp_from.volume_out(self.flow * self._t)
            # If not all volume can be removed from the model component, transfer the remaining volume to the other model component
            # This is undesirable but it is better than having a negative volume
            self._model_comp_to.volume_in(
                self.flow * self._t - vol_not_removed, self._model_comp_from
            )
        elif self.flow < 0:
            # Flow is from comp_to to comp_from
            vol_not_removed = self._model_comp_to.volume_out(-self.flow * self._t)
            # If not all volume can be removed from the model component, transfer the remaining volume to the other model component
            # This is undesirable but it is better than having a negative volume
            self._model_comp_from.volume_in(
                -self.flow * self._t - vol_not_removed, self._model_comp_to
            )

    def reconnect(self, comp_from, comp_to):
        # store the connectors
        self.comp_from = comp_from
        self.comp_to = comp_to

        # get a reference to the connected components
        if type(self.comp_from) == str:
            self._model_comp_from = self._model_engine.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) == str:
            self._model_comp_to = self._model_engine.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to