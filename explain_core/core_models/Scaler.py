import math


class Scaler:
    # static properties
    model_type: str = "Scaler"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.reference_weight = 3.545
        self.weight = 3.5
        self.age = 0.0
        self.gestational_age = 40.0
        self.map_ref = 40.0
        self.hr_ref = 140.0
        self.heart = []
        self.baroreceptor = []
        self.metabolism = []
        self.breathing = []
        self.left_atrium = []
        self.right_atrium = []
        self.left_ventricle = []
        self.right_ventricle = []
        self.coronaries = []
        self.arteries = []
        self.pulmonary_arteries = []
        self.pulmonary_veins = []
        self.systemic_arteries = []
        self.systemic_veins = []
        self.capillaries = []
        self.heart_valves = []
        self.shunts = []
        self.syst_blood_connectors = []
        self.pulm_blood_connectors = []
        self.pericardium = []
        self.lungs = []
        self.airways = []
        self.thorax = []
        self.blood_containing_components = []
        self.gas_containing_components = []


        # general scaler
        self.global_scale_factor = 1.0

        # blood volume in mL/kg
        self.blood_volume_kg = 0.08

        # lung volume in mL/kg
        self.lung_volume_kg = 0.03

        # reference heartrate in bpm (-1 = no change) neonate = 110.0
        self.hr_ref = 1.0

        # reference mean arterial pressure in mmHg (-1 = no change) neonate = 51.26
        self.map_ref = 1.0

        # reference minute volume in bpm (-1 = no change) neonate = 40
        self.minute_volume_ref_scaling_factor = 1.0

        # vt/rr ratio in L/bpm/kg (-1 = no change) neonate = 0.0001212
        self.vt_rr_ratio_scaling_factor = 1.0

        # oxygen consumption in ml/min/kg (-1 = no change)
        self.vo2_scaling_factor = 1.0

        # respiratory quotient  (-1 = no change)
        self.resp_q_scaling_factor = 1.0

        # heart chamber scalers
        self.el_min_atrial_factor = 1.0
        self.el_max_atrial_factor = 1.0

        self.el_min_ventricular_factor = 1.0
        self.el_max_ventricular_factor = 1.0

        self.u_vol_atrial_factor = 1.0
        self.u_vol_ventricular_factor = 1.0

        # coronary scalers
        self.el_min_cor_factor = 1.0
        self.el_max_cor_factor = 1.0
        self.u_vol_cor_factor = 1.0

        # heart valve scalers
        self.res_valve_factor = 1.0

        # pericardium scalers
        self.el_base_pericardium_factor = 1.0
        self.u_vol_pericardium_factor = 1.0

        # systemic arteries
        self.el_base_syst_art_factor = 1.0
        self.u_vol_syst_art_factor = 1.0

        # pulmonary arteries
        self.el_base_pulm_art_factor = 1.0
        self.u_vol_pulm_art_factor = 1.0

        # systemic veins
        self.el_base_syst_ven_factor = 1.0
        self.u_vol_syst_ven_factor = 1.0

        # pulmonary veins
        self.el_base_pulm_ven_factor = 1.0
        self.u_vol_pulm_ven_factor = 1.0

        # capillaries
        self.el_base_cap_factor = 1.0
        self.u_vol_cap_factor = 1.0

        # systemic blood connectors
        self.res_syst_blood_connectors_factor = 1.0

        # pulmonary blood connectors
        self.res_pulm_blood_connectors_factor = 1.0

        # shunts
        self.res_shunts_factor = 1.0

        # lungs
        self.el_base_lungs_factor = 1.0
        self.u_vol_lungs_factor = 1.0

        # airways
        self.res_airway_factor = 1.0

        # thorax
        self.el_base_thorax_factor = 1.0
        self.u_vol_thorax_factor = 1.0

        # dependent parameters
        self.total_blood_volume = 0.0
        self.total_gas_volume = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # get the current setting
        self.weight = self._model_engine.weight
        self.age = self._model_engine.age
        self.gestational_age = self._model_engine.gestational_age

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        pass

    def scale_patient(self):
        # scale total blood volume
        self.scale_total_blood_volume(self.blood_volume_kg)

        # scale total lung volume
        self.scale_total_lung_volume(self.lung_volume_kg)

        # scale pericardium
        self.scale_pericardium()

        # scale the thorax
        self.scale_thorax()

        # scale the baroreflex of the autonomous nervous system
        self.scale_ans(self.hr_ref, self.map_ref)

        # scale the control of breathing model
        self.scale_cob()

        # scale the metabolism
        self.scale_metabolism()

        # scale mob
        self.scale_mob()

        # scale the heart
        self.scale_heart()

        # scale the systemic arteries
        self.scale_systemic_arteries()

        # scale the pulmonary arteries
        self.scale_pulmonary_arteries()

        # scale the capillaries
        self.scale_capillaries()

        # scale the systemic veins
        self.scale_systemic_veins()

        # scale the pulmonary veins
        self.scale_pulmonary_veins()

        # scale the systemic blood connectors
        self.scale_syst_blood_connectors()

        # scale the pulmonary blood connectors
        self.scale_pulm_blood_connectors()

        # scale the shunts
        self.scale_shunts()

        # scale the valves
        self.scale_heart_valves()

        # scale the lung
        self.scale_lungs()

        # scale the airways
        self.scale_airways()

        # get the current total blood and lung volume in l/kg
        self.blood_volume_kg = self.get_total_blood_volume() / self._model_engine.weight
        self.lung_volume_kg = self.get_total_lung_volume() / self._model_engine.weight

    def scale_weight(self, new_weight):
        # calculate the global scaling factor. This factor is relative to the reference baseline patient
        self.global_scale_factor = new_weight / self.reference_weight

        # set the new weight
        self.weight = new_weight
        self._model_engine.weight = new_weight

        # scale the whole patient
        self.scale_patient()

    def scale_total_blood_volume(self, new_blood_volume_kg):
        self.blood_volume_kg = new_blood_volume_kg
        
        # determine the new absolute blood volume in litres
        target_blood_volume = new_blood_volume_kg * self.weight

        # get the current blood volume
        current_blood_volume = self.get_total_blood_volume()

        # calculate the change of the total volume
        scale_factor = target_blood_volume / current_blood_volume

        # change the volume of the blood containing models
        for bc in self.blood_containing_components:
            self._model_engine.models[bc].vol = self._model_engine.models[bc].vol * scale_factor
    
    def scale_total_lung_volume(self, new_lung_volume_kg):
        self.lung_volume_kg = new_lung_volume_kg

        # determine the new absolute lung volume in litres
        target_lung_volume = new_lung_volume_kg * self.weight

        # determine the current lung volume
        current_volume = self.get_total_lung_volume()

        # calculate the change in total lung volume
        scale_factor = target_lung_volume / current_volume

        # change the volume of the gas containing models
        for lu in self.lungs:
            self._model_engine.models[lu].vol = self._model_engine.models[lu].vol * scale_factor

        # change the volume of the thorax
        for th in self.thorax:
            self._model_engine.models[th].vol = self._model_engine.models[th].vol * scale_factor

    def scale_ans_hr(self, hr_ref):
        self.hr_ref = hr_ref
        self.scale_ans(self.hr_ref, self.map_ref)

    def scale_ans_map(self, map_ref):
        self.map_ref = map_ref
        self.scale_ans(self.hr_ref, self.map_ref)

    def scale_ans(self, hr_ref, map_ref):
        self.hr_ref = hr_ref
        self.map_ref = map_ref
        for he in self.heart:
            self._model_engine.models[he].heart_rate_ref = self.hr_ref
            self._model_engine.models[he].heart_rate_forced = self.hr_ref

        # adjust the baroreceptor
        for br in self.baroreceptor:
            self._model_engine.models[br].min_value = self.map_ref / 2.0
            self._model_engine.models[br].set_value = self.map_ref
            self._model_engine.models[br].max_value = self.map_ref * 2.0

    def scale_cob(self):
        for br in self.breathing:
            self._model_engine.models[br].minute_volume_ref_scaling_factor = self.minute_volume_ref_scaling_factor
            self._model_engine.models[br].vt_rr_ratio_scaling_factor = self.vt_rr_ratio_scaling_factor
        
    def scale_metabolism(self):
        for me in self.metabolism:
            self._model_engine.models[me].vo2_scaling_factor = self.vo2_scaling_factor
            self._model_engine.models[me].resp_q_scaling_factor = self.resp_q_scaling_factor

    def scale_mob(self):
        # the mob model uses a weight based approach
        pass

    def scale_heart(self):
        # right atrium
        for ra in self.right_atrium:
            # change the unstressed volume
            self._model_engine.models[ra].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_atrial_factor

            # change the minimal and maximal elastance
            self._model_engine.models[ra].el_min_scaling_factor = (1.0 / self.global_scale_factor) * self.el_min_atrial_factor
            self._model_engine.models[ra].el_max_scaling_factor = (1.0 / self.global_scale_factor) * self.el_max_atrial_factor

        # left atrium
        for la in self.left_atrium:
            # change the unstressed volume
            self._model_engine.models[la].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_atrial_factor

            # change the minimal and maximal elastance
            self._model_engine.models[la].el_min_scaling_factor = (1.0 / self.global_scale_factor) * self.el_min_atrial_factor
            self._model_engine.models[la].el_max_scaling_factor = (1.0 / self.global_scale_factor) * self.el_max_atrial_factor


        # right ventricle
        for rv in self.right_ventricle:
            # change the unstressed volume
            self._model_engine.models[rv].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_ventricular_factor

            # change the minimal and maximal elastance
            self._model_engine.models[rv].el_min_scaling_factor = (1.0 / self.global_scale_factor) * self.el_min_ventricular_factor
            self._model_engine.models[rv].el_max_scaling_factor = (1.0 / self.global_scale_factor) * self.el_max_ventricular_factor


        # left ventricle
        for lv in self.left_ventricle:
            # change the unstressed volume
            self._model_engine.models[lv].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_ventricular_factor

            # change the minimal and maximal elastance
            self._model_engine.models[lv].el_min_scaling_factor = (1.0 / self.global_scale_factor) * self.el_min_ventricular_factor
            self._model_engine.models[lv].el_max_scaling_factor = (1.0 / self.global_scale_factor) * self.el_max_ventricular_factor

        # coronaries
        for cor in self.coronaries:
            # change the unstressed volume
            self._model_engine.models[cor].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_cor_factor

            # change the minimal and maximal elastance
            self._model_engine.models[cor].el_min_scaling_factor = (1.0 / self.global_scale_factor) * self.el_min_cor_factor
            self._model_engine.models[cor].el_max_scaling_factor = (1.0 / self.global_scale_factor) * self.el_max_cor_factor

    def scale_heart_valves(self):
        for hv in self.heart_valves:
            self._model_engine.models[hv].r_scaling_factor = (1.0 / self.global_scale_factor) * self.res_valve_factor

    def scale_pericardium(self):
        for pc in self.pericardium:
            # change the unstressed volume
            self._model_engine.models[pc].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_pericardium_factor

            # change the baseline elastance
            self._model_engine.models[pc].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_pericardium_factor
    
    def scale_systemic_arteries(self):
        for sa in self.systemic_arteries:
            # change the unstressed volume
            self._model_engine.models[sa].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_syst_art_factor

            # change the baseline elastance
            self._model_engine.models[sa].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_syst_art_factor
    
    def scale_systemic_veins(self):
        for sv in self.systemic_veins:
            # change the unstressed volume
            self._model_engine.models[sv].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_syst_ven_factor

            # change the baseline elastance
            self._model_engine.models[sv].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_syst_ven_factor
    
    def scale_syst_blood_connectors(self):
        for sbc in self.syst_blood_connectors:
            self._model_engine.models[sbc].r_scaling_factor = (1.0 / self.global_scale_factor) * self.res_syst_blood_connectors_factor

    def scale_pulmonary_arteries(self):
        for pa in self.pulmonary_arteries:
            # change the unstressed volume
            self._model_engine.models[pa].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_pulm_art_factor

            # change the baseline elastance
            self._model_engine.models[pa].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_pulm_art_factor
    
    def scale_pulmonary_veins(self):
        for pv in self.pulmonary_veins:
            # change the unstressed volume
            self._model_engine.models[pv].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_pulm_ven_factor

            # change the baseline elastance
            self._model_engine.models[pv].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_pulm_ven_factor
    
    def scale_pulm_blood_connectors(self):
        for pbc in self.pulm_blood_connectors:
            self._model_engine.models[pbc].r_scaling_factor = (1.0 / self.global_scale_factor) * self.res_pulm_blood_connectors_factor

    def scale_capillaries(self):
        for cap in self.capillaries:
            # change the unstressed volume
            self._model_engine.models[cap].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_cap_factor

            # change the baseline elastance
            self._model_engine.models[cap].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_cap_factor
    
    def scale_shunts(self):
        for sh in self.shunts:
            self._model_engine.models[sh].r_scaling_factor = (1.0 / self.global_scale_factor) * self.res_shunts_factor

    def scale_lungs(self):
        for lu in self.lungs:
            # change the unstressed volume
            self._model_engine.models[lu].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_lungs_factor

            # change the baseline elastance
            self._model_engine.models[lu].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_lungs_factor
    
    def scale_airways(self):
        for aw in self.airways:
            self._model_engine.models[aw].r_scaling_factor = (1.0 / self.global_scale_factor) * self.res_airway_factor

    def scale_thorax(self):
        for th in self.thorax:
            # change the unstressed volume
            self._model_engine.models[th].u_vol_scaling_factor = self.global_scale_factor * self.u_vol_thorax_factor

            # change the baseline elastance
            self._model_engine.models[th].el_base_scaling_factor = (1.0 / self.global_scale_factor) * self.el_base_thorax_factor
    
    def get_total_blood_volume(self):
        total_volume = 0.0
        for target in self.blood_containing_components:
            if self._model_engine.models[target].is_enabled:
                total_volume += self._model_engine.models[target].vol
        self.total_blood_volume = total_volume
        return total_volume

    def get_total_lung_volume(self):
        total_volume = 0.0
        for target in self.gas_containing_components:
            if self._model_engine.models[target].is_enabled:
                total_volume += self._model_engine.models[target].vol
        self.total_gas_volume = total_volume
        return total_volume



            
