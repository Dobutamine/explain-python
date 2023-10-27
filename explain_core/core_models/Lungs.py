from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.GasCapacitance import GasCapacitance
from explain_core.core_models.GasExchanger import GasExchanger
from explain_core.base_models.Container import Container
from explain_core.base_models.Resistor import Resistor

class Lungs(BaseModel):
    # independent parameters
    upper_airways: str = ["MOUTH_DS"]
    dead_space: str = ["DS"]
    thorax: str = "THORAX"
    chestwall: str = ["CHEST_L", "CHEST_R"]
    alveolar_spaces: str = ["ALL", "ALR"]
    lower_airways: str = ["DS_ALL", "DS_ALR"]
    gas_exchangers: str = ["GASEX_LL", "GASEX_RL"]
    

    # local parameters
    _upper_airways: Resistor = []
    _dead_space: GasCapacitance = []
    _lower_airways: Resistor = []
    _alveolar_spaces: GasCapacitance = []
    _thorax: Container = []
    _chestwall: Container = []
    _gas_exchangers: Resistor = []

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get all the model components
        for uaw in self.upper_airways:
            self._upper_airways.append(self._model.models[uaw])
        
        for ds in self.dead_space:
            self._dead_space.append(self._model.models[ds])

        for law in self.lower_airways:
            self._lower_airways.append(self._model.models[law])
        
        for alvs in self.alveolar_spaces:
            self._alveolar_spaces.append(self._model.models[alvs])
        
        for th in self.thorax:
            self._thorax.append(self._model.models[th])
        
        for cw in self.chestwall:
            self._chestwall.append(self._model.models[cw])
        
        for gasex in self.gas_exchangers:
            self._gas_exchangers.append(self._model.models[gasex])

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        pass

    def change_lung_compliance(self, comp_change):
        if comp_change > 0.0:
            for alv_space in self._alveolar_spaces:
                alv_space.el_base_factor = 1.0 / comp_change

    def change_chestwall_compliance(self, comp_change):
        if comp_change > 0.0:
            for cw in self._chestwall:
                cw.el_base_factor = 1.0 / comp_change

    def change_upper_airway_resistance(self, res_change):
        if res_change > 0.0:
            for uaw in self._upper_airways:
                uaw.r_for_factor = res_change
                uaw.r_back_factor = res_change

    def change_lower_airway_resistance(self, res_change):
        if res_change > 0.0:
            for law in self._lower_airways:
                law.r_for_factor = res_change
                law.r_back_factor = res_change



