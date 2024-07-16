import math


class Fluids:
    # static properties
    model_type: str = "Fluids"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.fluid_types = None

        # dependent properties
        self.total_blood_volume = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._infusions = []

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        infusions_finished = True

        for iv in self._infusions:
            finished = iv.calc_iv()
            if not finished:
                infusions_finished = False

        if infusions_finished:
            self._infusions = []

    def add_volume(self, vol=10.0, in_time=5.0, site="VLB", fluid_type=None):
        if vol > 0.0:
            if fluid_type in self.fluid_types.keys():
                new_fluid = Fluid(
                    vol,
                    self.fluid_types[fluid_type],
                    in_time,
                    0.0,
                    self._model_engine.models[site],
                    self._t,
                )
                self._infusions.append(new_fluid)
            else:
                new_fluid = Fluid(
                    vol,
                    None,
                    in_time,
                    0.0,
                    self._model_engine.models[site],
                    self._t,
                )
                self._infusions.append(new_fluid)

            return True

    def remove_volume(self, vol=10.0, in_time=5.0, site="VLB"):
        if vol > 0.0:
            new_fluid = Fluid(
                -vol,
                None,
                in_time,
                0.0,
                self._model_engine.models[site],
                self._t,
            )
            self._infusions.append(new_fluid)
            return True


class Fluid:
    def __init__(self, volume, fluid_comp, in_time, at_time, site, t):
        self._t = t
        self._addition = True
        if volume < 0:
            self._addition = False
            volume = -volume
        if fluid_comp:
            self.fluid_comp = fluid_comp
            if "solutes" in fluid_comp.keys():
                self.solutes = {**fluid_comp["solutes"]}
            else:
                self.solutes = {}
            if "aboxy" in fluid_comp.keys():
                self.aboxy = {**fluid_comp["aboxy"]}
            else:
                self.aboxy = {}
        else:
            self.solutes = {}
            self.aboxy = {}

        self.site = site
        self.completed = False
        self.volume = volume / 1000.0
        self.in_time = in_time
        self.at_time = at_time
        self.delta_vol = (self.volume / self.in_time) * self._t

    def calc_iv(self):
        if self.at_time > 0:
            self.at_time -= self._t
            return self.completed

        self.in_time -= self._t
        self.volume -= self.delta_vol

        if self.volume < 0:
            self.volume = 0
            self.completed = True
            return self.completed

        # substract the volume and return
        if not self._addition:
            self.site.vol -= self.delta_vol
            if self.site.vol < 0:
                self.site.vol = 0
            return self.completed

        # add  the volume and return
        self.site.vol += self.delta_vol

        # process the aboxy and solutes if the fluid_composition is not none
        if self.fluid_comp:
            for solute, conc in self.aboxy.items():
                d_solute = (conc - self.site.aboxy[solute]) * self.delta_vol
                self.site.aboxy[solute] += d_solute / self.site.vol

            for solute, conc in self.solutes.items():
                d_solute = (conc - self.site.solutes[solute]) * self.delta_vol
                self.site.solutes[solute] += d_solute / self.site.vol

        return self.completed
