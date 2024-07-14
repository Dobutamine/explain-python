import math


class Lungs:
    # static properties
    model_type: str = "Lungs"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.upper_airways = []
        self.dead_space = []
        self.thorax = []
        self.chestwall = []
        self.alveolar_spaces = []
        self.lower_airways = []
        self.gas_exchangers = []
        self.lung_shunts = []

        # dependent properties
        self.dif_o2_change = 1.0
        self.dif_co2_change = 1.0
        self.dead_space_change = 1.0
        self.lung_comp_change = 1.0
        self.chestwall_comp_change = 1.0
        self.thorax_comp_change = 1.0
        self.upper_aw_res_change = 1.0
        self.lower_aw_res_change = 1.0
        self.lung_shunt_change = 1.0
        self.atelectasis_change = 1.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._upper_airways = []
        self._dead_space = []
        self._thorax = []
        self._chestwall = []
        self._alveolar_spaces = []
        self._lower_airways = []
        self._gas_exchangers = []
        self._lung_shunts = []

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # store a reference to the necessary models
        for target in self.upper_airways:
            self._upper_airways.append(self._model_engine.models[target])

        for target in self.dead_space:
            self._dead_space.append(self._model_engine.models[target])

        for target in self.lower_airways:
            self._lower_airways.append(self._model_engine.models[target])

        for target in self.chestwall:
            self._chestwall.append(self._model_engine.models[target])

        for target in self.alveolar_spaces:
            self._alveolar_spaces.append(self._model_engine.models[target])

        for target in self.gas_exchangers:
            self._gas_exchangers.append(self._model_engine.models[target])

        for target in self.lung_shunts:
            self._lung_shunts.append(self._model_engine.models[target])

        for target in self.thorax:
            self._thorax.append(self._model_engine.models[target])

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        pass

    def change_lung_shunt(self, change_forward, change_backward=-1):
        if change_forward > 0.0:
            self.lung_shunt_change = change_forward
            for target in self._lung_shunts:
                target.r_for_factor = change_forward
                target.r_back_factor = change_forward
                if change_backward >= 0.0:
                    target.r_back_factor = change_backward

    def change_atelectasis(self, change):
        if change > 0.0:
            self.atelectasis_change = change

    def change_dead_space(self, change):
        if change > 0.0:
            self.dead_space_change = change
            for target in self._dead_space:
                target.u_vol_factor = change

    def change_dif(self, change):
        if change > 0.0:
            self.dif_o2_change = change
            self.dif_co2_change = change
            for target in self._gas_exchangers:
                target.dif_o2_factor = change
                target.dif_co2_factor = change

    def change_dif_o2(self, change):
        if change > 0.0:
            self.dif_o2_change = change
            for target in self._gas_exchangers:
                target.dif_o2_factor = change

    def change_dif_co2(self, change):
        if change > 0.0:
            self.dif_co2_change = change
            for target in self._gas_exchangers:
                target.dif_co2_factor = change

    def change_lower_airway_resistance(self, change_forward, change_backward=-1):
        if change_forward > 0.0:
            self.lower_aw_res_change = change_forward
            for target in self._lower_airways:
                target.r_for_factor = change_forward
                target.r_back_factor = change_forward

    def change_upper_airway_resistance(self, change_forward, change_backward=-1):
        if change_forward > 0.0:
            self.lower_aw_res_change = change_forward
            for target in self._upper_airways:
                target.r_for_factor = change_forward
                target.r_back_factor = change_forward

    def change_thorax_compliance(self, change):
        if change > 0.0:
            self.thorax_comp_change = change
            for target in self._thorax:
                target.el_base_factor = 1.0 / change

    def change_lung_compliance(self, change):
        if change > 0.0:
            self.lung_comp_change = change
            for target in self._alveolar_spaces:
                target.el_base_factor = 1.0 / change

    def change_chestwall_compliance(self, change):
        if change > 0.0:
            self.chestwall_comp_change = change
            for target in self._chestwall:
                target.el_base_factor = 1.0 / change
