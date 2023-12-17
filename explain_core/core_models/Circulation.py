from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Resistor import Resistor
from explain_core.core_models.BloodCapacitance import BloodCapacitance


class Circulation(BaseModel):
    # independent parameters
    systemic_arteries: str = ["AA", "AAR", "AD"]
    systemic_veins: str = ["IVCI", "IVCE", "SVC"]
    svr_targets: str = ["AD_INT", "AD_KID", "AD_LS", "AAR_RUB", "AD_RLB"]
    pulmonary_arteries: str = ["PA"]
    pulmonary_veins: str = ["PV"]
    pvr_targets: str = ["PA_LL", "PA_RL"]
    venpool_targets: str = ["IVCE", "SVC"]
    ofo_targets: str = ["FO"]
    vsd_targets: str = ["VSD"]
    ips_targets: str = ["IPS"]

    # dependent parameters
    _systemic_arteries: BloodCapacitance = []
    _systemic_veins: BloodCapacitance = []
    _svr_targets: Resistor = []
    _pulmonary_arteries: BloodCapacitance = []
    _pulmonary_veins: BloodCapacitance = []
    _pvr_targets: Resistor = []
    _venpool_targets: BloodCapacitance = []
    _heart_inferior_vena_cava: Resistor = []
    _heart_superior_vena_cava: Resistor = []
    _heart_aorta: Resistor = []
    _heart_pulmonary_artery: Resistor = []
    _heart_pulmonary_veins: Resistor = []
    _ofo_targets: Resistor = []
    _vsd_targets: Resistor = []
    _ips_targets: Resistor = []

    dp: float = 0.0

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # store a reference to the necessary models
        for sa in self.systemic_arteries:
            self._systemic_arteries.append(self._model.models[sa])

        for sv in self.systemic_veins:
            self._systemic_veins.append(self._model.models[sv])

        for svrt in self.svr_targets:
            self._svr_targets.append(self._model.models[svrt])

        for pvrt in self.pvr_targets:
            self._pvr_targets.append(self._model.models[pvrt])

        for vpt in self.venpool_targets:
            self._venpool_targets.append(self._model.models[vpt])

        for res in self.heart_aorta:
            self._heart_aorta.append(self._model.models[res])

        for res in self.heart_inferior_vena_cava:
            self._heart_inferior_vena_cava.append(self._model.models[res])

        for res in self.heart_superior_vena_cava:
            self._heart_superior_vena_cava.append(self._model.models[res])

        for res in self.heart_pulmonary_artery:
            self._heart_pulmonary_artery.append(self._model.models[res])

        for res in self.heart_pulmonary_veins:
            self._heart_pulmonary_veins.append(self._model.models[res])

        for res in self.ofo_targets:
            self._ofo_targets.append(self._model.models[res])

        for res in self.vsd_targets:
            self._vsd_targets.append(self._model.models[res])

        for res in self.ips_targets:
            self._ips_targets.append(self._model.models[res])

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self):
        self.dp = self._model.models["AAR"].pres - self._model.models["PA"].pres

    def set_ofo_diameter(self, new_diameter):
        if new_diameter >= 0.0:
            for ofo in self._ofo_targets:
                ofo.set_diameter(new_diameter)

    def set_vsd_diameter(self, new_diameter):
        if new_diameter >= 0.0:
            for vsd in self._vsd_targets:
                vsd.set_diameter(new_diameter)

    def change_lungshunt(self, ls_change):
        if ls_change > 0.0:
            for ips in self._ips_targets:
                ips.set_r_for_factor(1.0 / ls_change)
                ips.set_r_back_factor(1.0 / ls_change)

    def change_pvr(self, pvr_change):
        if pvr_change > 0.0:
            for pvrt in self._pvr_targets:
                pvrt.set_r_for_factor(pvr_change)
                pvrt.set_r_back_factor(pvr_change)

    def change_svr(self, svr_change):
        if svr_change > 0.0:
            for svrt in self._svr_targets:
                svrt.set_r_for_factor(svr_change)
                svrt.set_r_back_factor(svr_change)

    def change_venpool(self, venpool_change):
        if venpool_change > 0.0:
            for vpt in self._venpool_targets:
                vpt.u_vol_factor = venpool_change

    def change_arterial_compliance(self, comp_change):
        if comp_change > 0.0:
            for sa in self._systemic_arteries:
                sa.el_base_factor = 1.0 / comp_change

    def change_venous_compliance(self, comp_change):
        if comp_change > 0.0:
            for sv in self._systemic_veins:
                sv.el_base_factor = 1.0 / comp_change
