from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance

class Fluid: 
    site: Capacitance = {}
    volume: float = 0.0
    in_time: float = 5.0
    at_time: float = 0.0
    infusing: bool = False
    completed: bool = False
    delta_vol: float = 0.0

    fluid_comp: dict[str, float] = None
    solutes: dict[str, float] = {}
    aboxy: dict[str, float] = {}

    _t: float = 0.0005
    _addition: bool = True

    def __init__(self, volume: float, fluid_comp: dict[str, float], in_time: float, at_time: float, site: Capacitance, t: float):
        self._t = t
        if volume < 0:
            self._addition = False
            volume = -volume

        if fluid_comp is not None:
            self.fluid_comp = fluid_comp
            self.solutes = fluid_comp["solutes"]
            self.aboxy = fluid_comp["aboxy"]
        else:
            self.solutes = {}
            self.aboxy = {}

        self.site = site
        self.volume = volume / 1000.0
        self.in_time = in_time
        self.at_time = at_time
        self.delta_vol = (self.volume / self.in_time) * self._t


    def calc_iv(self) -> bool:
        if self.at_time > 0:
            self.at_time -= self._t
            return self.completed

        self.in_time -= self._t
        self.volume -= self.delta_vol

        if (self.volume < 0):
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
        _site_vol = self.site.vol + self.site.u_vol
        if self.fluid_comp is not None:
            for solute, conc in self.aboxy.items():
                d_solute = (conc - self.site.aboxy[solute]) * self.delta_vol
                self.site.aboxy[solute] += d_solute / _site_vol
            for solute, conc in self.solutes.items():
                d_solute = (conc - self.site.solutes[solute]) * self.delta_vol
                self.site.solutes[solute] += d_solute / _site_vol          
        
        return self.completed


class Fluids(BaseModel):
    fluid_types = {}
    _infusions: Fluid = []

    def calc_model(self):
        # assume that all infusions are finished
        infusions_finished = True

        # iterate over all infusions
        for _iv in self._infusions:
            # get the status of the infusion
            finished = _iv.calc_iv()
            if not finished:
                infusions_finished = False

        # reset the infusions list if all are finished
        if infusions_finished:
            self._infusions = []
            

    def add_volume(self, vol: float = 10.0, in_time: float = 5.0, at_time: float = 0.0, site: str = "IVCE", fluid_type: str = None) -> bool:
        # first build a infusion fluid
        if vol > 0:
            if fluid_type in self.fluid_types.keys():
                # fluid found
                new_fluid = Fluid(vol, self.fluid_types[fluid_type], in_time, at_time, self._model.models[site], self._t)
                self._infusions.append(new_fluid)
            else:
                 # no fluid found -> volume change without concentration change of the solutes
                new_fluid = Fluid(vol, None, in_time, at_time, self._model.models[site], self._t)
                self._infusions.append(new_fluid)
            return True
        else:
            # fluid not found
            print("zero or negative volume changes are not allowed. Use the remove_volume method to remove volume!")
            return False


    def remove_volume(self, vol: float = 10.0, in_time: float = 5.0, at_time: float = 0.0, site: str = "IVCE") -> bool:
        if vol > 0:
            new_fluid = Fluid(-vol, None, in_time, at_time, self._model.models[site], self._t)
            self._infusions.append(new_fluid)
            return True
        else:
            print("zero or negative volume changes are not allowed. Use the add_volume method to add volume!")
            return False


    def set_total_blood_volume(self, new_blood_volume):
        current_blood_volume = self.get_total_blood_volume(output=False)
        new_blood_volume = new_blood_volume
        
        # divide the new blood volume over all blood holding capacitances
        for model in self._model.models.values():
            if "Blood" in model.model_type:
                if model.is_enabled:
                    try:
                        # calculate the current fraction of the blood volume in this blood containing capacitance
                        current_fraction = model.vol / current_blood_volume
                        # add the same fraction of the desired volume change to the blood containing capacitance
                        model.vol += current_fraction * (new_blood_volume - current_blood_volume)
                        # guard for negative volumes
                        if model.vol < 0.0:
                            model.vol = 0.0
                    except:
                        current_fraction = 0


    def get_total_blood_volume(self, output = True) -> float:
        total_blood_volume: float = 0.0

        for model in self._model.models.values():
            if "Blood" in model.model_type:
                if model.is_enabled:
                    try:
                        total_blood_volume += model.vol
                    except:
                        total_blood_volume += 0.0

            # if "Blood" in model.model_type and model.is_enabled:
            #     total_blood_volume += model.vol
        
        if output:
            print(f"Total blood volume = {total_blood_volume * 1000.0} ml ({total_blood_volume * 1000.0 / self._model.weight} ml/kg)")
        
        return total_blood_volume
    
    def get_total_volume(self, output = True) -> float:
        total_blood_volume: float = 0.0

        for model in self._model.models.values():
            if model.model_type == 'BloodCapacitance' or model.model_type == 'BloodTimeVaryingElastance' or model.model_type == 'LymphCapacitance':
                if model.is_enabled:
                    try:
                        total_blood_volume += model.vol
                    except:
                        total_blood_volume += 0.0

            # if "Blood" in model.model_type and model.is_enabled:
            #     total_blood_volume += model.vol
        
        bv = self.get_total_blood_volume(True)
        if output:
            print(f"Total volume = {total_blood_volume * 1000.0} ml ({total_blood_volume * 1000.0 / self._model.weight} ml/kg)")
        
        return total_blood_volume






