class BloodDiffusor:
    # static properties
    model_type: str = "BloodDiffusor"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.solutes = []
        self.drugs = []
        self.aboxy = []
        self.comp_blood1 = None
        self.comp_blood2 = None
        self.dif_cap = 0.01
        self.dif_cap_factor = 1.0
        self.dif_cap_scaling_factor = 1.0

        # dependent properties
        self.flux_o2 = 0.0
        self.flux_co2 = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._t: float = model_ref.modeling_stepsize
        self._is_initialized: bool = False
        self._comp_blood1 = None
        self._comp_blood2 = None
        self._flux_o2 = 0
        self._flux_co2 = 0

    def init_model(self, **args: dict[str, any]):
        # set the values of the properties as passed in the arguments
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the models
        if type(self.comp_blood1) == str:
            self._comp_blood1 = self._model_engine.models[self.comp_blood1]
        else:
            self._comp_blood1 = self.comp_blood1

        if type(self.comp_blood2) == str:
            self._comp_blood2 = self._model_engine.models[self.comp_blood2]
        else:
            self._comp_blood2 = self.comp_blood2

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # diffuse the solutes
        for solute in self.solutes:
            d_sol = (
                (self._comp_blood1.solutes[solute] - self._comp_blood2.solutes[solute])
                * self.dif_cap
                * self.dif_cap_factor
                * self.dif_cap_scaling_factor
            )
            self._comp_blood2.solutes[solute] = (
                (self._comp_blood2.solutes[solute] * self._comp_blood2.vol) + d_sol
            ) / self._comp_blood2.vol

            self._comp_blood1.solutes[solute] = (
                (self._comp_blood1.solutes[solute] * self._comp_blood1.vol) - d_sol
            ) / self._comp_blood1.vol

        # diffuse the drugs
        for drug in self.drugs:
            d_drug = (
                (self._comp_blood1.drugs[drug] - self._comp_blood2.drugs[drug])
                * self.dif_cap
                * self.dif_cap_factor
                * self.dif_cap_scaling_factor
            )
            self._comp_blood2.drugs[drug] = (
                (self._comp_blood2.drugs[drug] * self._comp_blood2.vol) + d_drug
            ) / self._comp_blood2.vol

            self._comp_blood1.drugs[drug] = (
                (self._comp_blood1.drugs[drug] * self._comp_blood1.vol) - d_drug
            ) / self._comp_blood1.vol

        # diffuse the aboxy
        for abox in self.aboxy:
            d_abox = (
                (self._comp_blood1.aboxy[abox] - self._comp_blood2.aboxy[abox])
                * self.dif_cap
                * self.dif_cap_factor
                * self.dif_cap_scaling_factor
            )
            self._comp_blood2.aboxy[abox] = (
                (self._comp_blood2.aboxy[abox] * self._comp_blood2.vol) + d_abox
            ) / self._comp_blood2.vol

            self._comp_blood1.aboxy[abox] = (
                (self._comp_blood1.aboxy[abox] * self._comp_blood1.vol) - d_abox
            ) / self._comp_blood1.vol

    def reconnect(self, comp_blood1, comp_blood2):
        # store the new components
        self.comp_blood1 = comp_blood1
        self.comp_blood2 = comp_blood2

        # get a reference to the models
        if type(self.comp_blood1) == str:
            self._comp_blood1 = self._model_engine.models[self.comp_blood1]
        else:
            self._comp_blood1 = self.comp_blood1

        if type(self.comp_blood2) == str:
            self._comp_blood2 = self._model_engine.models[self.comp_blood2]
        else:
            self._comp_blood2 = self.comp_blood2
