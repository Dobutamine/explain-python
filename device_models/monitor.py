from collections.abc import Mapping

from base_models.base_model import BaseModel


class Monitor(BaseModel):
	model_type = "monitor"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.hr_avg_beats = 5.0
		self.rr_avg_time = 20.0
		self.sat_avg_time = 5.0
		self.sat_sampling_interval = 1.0
		self.heart = "Heart"
		self.lv = "LV"
		self.rv = "RV"
		self.ascending_aorta = "AA"
		self.descending_aorta = "AD"
		self.pulm_artery = "PA"
		self.right_atrium = "RA"
		self.breathing = "Breathing"
		self.ventilator = "Ventilator"
		self.aortic_valve = "LV_AA"
		self.pulm_valve = "RV_PA"
		self.cor_ra = "COR_RA"
		self.aa_brain = "AA_BR"
		self.ad_kid = "AD_KID"
		self.ivc_ra = "IVCI_RA"
		self.svc_ra = "SVC_RA"
		self.thorax = "THORAX"
		self.deadspace = "DS"
		self.fo = "FO"
		self.da = "DA_OUT"
		self.vsd = "VSD"
		self.ips = "IPS"
		self.ua = "AD_UMB_ART"
		self.uv = "UMB_VEN_IVCI"

		self.heart_rate = 0.0
		self.heart_rate_btb = 0.0
		self.resp_rate = 0.0
		self.resp_rate_btb = 0.0
		self.test = 0.0
		self.abp_syst = 0.0
		self.abp_diast = 0.0
		self.abp_mean = 0.0
		self.abp_pre_syst = 0.0
		self.abp_pre_diast = 0.0
		self.abp_pre_mean = 0.0
		self.pap_syst = 0.0
		self.pap_diast = 0.0
		self.pap_mean = 0.0
		self.edv_lv = 0.0
		self.esv_lv = 0.0
		self.edp_lv = 0.0
		self.esp_lv = 0.0
		self.edv_rv = 0.0
		self.esv_rv = 0.0
		self.edp_rv = 0.0
		self.esp_rv = 0.0
		self.cvp = 0.0
		self.spo2 = 0.0
		self.spo2_pre = 0.0
		self.spo2_ven = 0.0
		self.etco2 = 0.0
		self.temp = 0.0
		self.co = 0.0
		self.ci = 0.0
		self.lvo = 0.0
		self.rvo = 0.0
		self.lv_sv = 0.0
		self.rv_sv = 0.0
		self.ivc_flow = 0.0
		self.svc_flow = 0.0
		self.cor_flow = 0.0
		self.brain_flow = 0.0
		self.kid_flow = 0.0
		self.da_flow = 0.0
		self.fo_flow = 0.0
		self.vsd_flow = 0.0
		self.ips_flow = 0.0
		self.ua_flow = 0.0
		self.uv_flow = 0.0
		self.fio2 = 0.0
		self.pip = 0.0
		self.p_plat = 0.0
		self.peep = 0.0
		self.tidal_volume = 0.0
		self.ph = 0.0
		self.po2 = 0.0
		self.pco2 = 0.0
		self.hco3 = 0.0
		self.be = 0.0
		self.dps = 0.0
		self.do2_br = 0.0
		self.do2_lb = 0.0

		self.ecg_signal = 0.0
		self.abp_signal = 0.0
		self.pap_signal = 0.0
		self.cvp_signal = 0.0
		self.spo2_pre_signal = 0.0
		self.spo2_signal = 0.0
		self.resp_signal = 0.0
		self.co2_signal = 0.0

		self._heart = None
		self._lv = None
		self._rv = None
		self._breathing = None
		self._ventilator = None
		self._aa = None
		self._ad = None
		self._ra = None
		self._pa = None
		self._ds = None
		self._thorax = None
		self._lv_aa = None
		self._rv_pa = None
		self._ivc_ra = None
		self._svc_ra = None
		self._cor_ra = None
		self._aa_br = None
		self._ad_kid = None
		self._ad_umb_art = None
		self._umb_ven_ivci = None
		self._fo = None
		self._da = None
		self._vsd = None
		self._ips = None

		self._temp_aa_pres_max = -1000.0
		self._temp_aa_pres_min = 1000.0
		self._temp_ad_pres_max = -1000.0
		self._temp_ad_pres_min = 1000.0
		self._temp_ra_pres_max = -1000.0
		self._temp_ra_pres_min = 1000.0
		self._temp_pa_pres_max = -1000.0
		self._temp_pa_pres_min = 1000.0
		self._temp_lv_pres_max = -1000.0
		self._temp_lv_pres_min = 1000.0
		self._temp_rv_pres_max = -1000.0
		self._temp_rv_pres_min = 1000.0
		self._temp_lv_vol_max = -1000.0
		self._temp_lv_vol_min = 1000.0
		self._temp_rv_vol_max = -1000.0
		self._temp_rv_vol_min = 1000.0
		self._lvo_counter = 0.0
		self._rvo_counter = 0.0
		self._cor_flow_counter = 0.0
		self._ivc_flow_counter = 0.0
		self._svc_flow_counter = 0.0
		self._brain_flow_counter = 0.0
		self._kid_flow_counter = 0.0
		self._da_flow_counter = 0.0
		self._fo_flow_counter = 0.0
		self._vsd_flow_counter = 0.0
		self._ips_flow_counter = 0.0
		self._ua_flow_counter = 0.0
		self._uv_flow_counter = 0.0
		self._hr_list = []
		self._edv_lv_list = []
		self._edv_rv_list = []
		self._esv_lv_list = []
		self._esv_rv_list = []
		self._edp_lv_list = []
		self._edp_rv_list = []
		self._rr_list = []
		self._spo2_list = []
		self._spo2_pre_list = []
		self._spo2_ven_list = []
		self._rr_avg_counter = 0.0
		self._sat_avg_counter = 0.0
		self._sat_sampling_counter = 0.0
		self._beats_counter = 0
		self._beats_time = 0.0
		self._qrs_interval_counter = 0.0
		self._qrs_interval_counter_factor = 1.0
		self._rr_update_counter = 0.0
		self._resp_rate_max_valid = 300.0

	def _resolve_model(self, model_name):
		if isinstance(model_name, (list, tuple)):
			if not model_name:
				return None
			model_name = model_name[0]
		if not model_name:
			return None
		if isinstance(self.model_ref, dict):
			resolved = self.model_ref.get(model_name)
			if resolved is not None:
				return resolved
		engine = getattr(self, "_model_engine", None)
		if engine is not None:
			models = getattr(engine, "models", None)
			if isinstance(models, dict):
				return models.get(model_name)
		return None

	def _safe_float(self, obj, attr_name, default=0.0):
		if obj is None:
			return float(default)
		value = getattr(obj, attr_name, default)
		if value is None:
			return float(default)
		return float(value)

	def init_model(self, args=None):
		if args is not None:
			normalized = dict(args) if isinstance(args, Mapping) else self._normalize_init_args(args)
			super().init_model(normalized)
		else:
			super().init_model(args)

		self._heart = self._resolve_model(self.heart)
		self._lv = self._resolve_model(self.lv)
		self._rv = self._resolve_model(self.rv)
		self._ra = self._resolve_model(self.right_atrium)
		self._breathing = self._resolve_model(self.breathing)
		self._ventilator = self._resolve_model(self.ventilator) or self._resolve_model("VENT")
		self._ds = self._resolve_model(self.deadspace)
		self._thorax = self._resolve_model(self.thorax)
		self._aa = self._resolve_model(self.ascending_aorta)
		self._ad = self._resolve_model(self.descending_aorta)
		self._pa = self._resolve_model(self.pulm_artery)
		self._lv_aa = self._resolve_model(self.aortic_valve)
		self._rv_pa = self._resolve_model(self.pulm_valve)
		self._ivc_ra = self._resolve_model(self.ivc_ra)
		self._svc_ra = self._resolve_model(self.svc_ra)
		self._cor_ra = self._resolve_model(self.cor_ra)
		self._aa_br = self._resolve_model(self.aa_brain)
		self._ad_kid = self._resolve_model(self.ad_kid)
		self._da = self._resolve_model(self.da)
		self._fo = self._resolve_model(self.fo)
		self._vsd = self._resolve_model(self.vsd)
		self._ips = self._resolve_model(self.ips)
		self._ad_umb_art = self._resolve_model(self.ua)
		self._umb_ven_ivci = self._resolve_model(self.uv)
		self._rr_update_counter = 0.0

	def calc_avg_heartrate(self, hr):
		self._hr_list.append(float(hr))

		if hr < 80.0:
			self.hr_avg_beats = 4.0
		else:
			self.hr_avg_beats = 12.0

		if self._hr_list:
			self.heart_rate = sum(self._hr_list) / len(self._hr_list)

		while len(self._hr_list) > int(self.hr_avg_beats):
			self._hr_list.pop(0)

	def calc_model(self):
		self.collect_pressures()
		self.collect_blood_flows()
		self.collect_signals()

		self.temp = self._safe_float(self._aa, "temp", self.temp)
		self.etco2 = self._safe_float(self._ventilator, "etco2", self.etco2)

		ncc_ventricular = self._safe_float(self._heart, "ncc_ventricular", 0.0)
		if ncc_ventricular == 1.0 and self._qrs_interval_counter > 0.0:
			self.heart_rate_btb = 60.0 / self._qrs_interval_counter
			self._qrs_interval_counter = 0.0
			self._qrs_interval_counter_factor = 1.0
			self.calc_avg_heartrate(self.heart_rate_btb)

		if self._qrs_interval_counter > 1.0 * self._qrs_interval_counter_factor and self._qrs_interval_counter > 0.0:
			self.heart_rate_btb = 60.0 / self._qrs_interval_counter
			self._qrs_interval_counter_factor += 1.0
			self.calc_avg_heartrate(self.heart_rate_btb)

		if self._rr_update_counter > 0.015:
			self._rr_update_counter = 0.0
			resp_rate_candidate = self._safe_float(self._breathing, "resp_rate_measured", self.resp_rate)
			if 0.0 <= resp_rate_candidate <= self._resp_rate_max_valid:
				self.resp_rate = resp_rate_candidate
		self._rr_update_counter += self._t

		if ncc_ventricular == 1.0:
			self._beats_counter += 1

			if self._aa is not None:
				self.abp_pre_syst = self._temp_aa_pres_max
				self.abp_pre_diast = self._temp_aa_pres_min
				self.abp_pre_mean = (2.0 * self._temp_aa_pres_min + self._temp_aa_pres_max) / 3.0
				self._temp_aa_pres_max = -1000.0
				self._temp_aa_pres_min = 1000.0
			if self._ad is not None:
				self.abp_syst = self._temp_ad_pres_max
				self.abp_diast = self._temp_ad_pres_min
				self.abp_mean = (2.0 * self._temp_ad_pres_min + self._temp_ad_pres_max) / 3.0
				self._temp_ad_pres_max = -1000.0
				self._temp_ad_pres_min = 1000.0
			if self._ra is not None:
				self.cvp = (2.0 * self._temp_ra_pres_min + self._temp_ra_pres_max) / 3.0
				self._temp_ra_pres_max = -1000.0
				self._temp_ra_pres_min = 1000.0
			if self._pa is not None:
				self.pap_syst = self._temp_pa_pres_max
				self.pap_diast = self._temp_pa_pres_min
				self.pap_mean = (2.0 * self._temp_pa_pres_min + self._temp_pa_pres_max) / 3.0
				self._temp_pa_pres_max = -1000.0
				self._temp_pa_pres_min = 1000.0
			if self._lv is not None:
				self._edv_lv_list.append(self._temp_lv_vol_max * 1000.0)
				self._edv_rv_list.append(self._temp_rv_vol_max * 1000.0)
				self._esv_lv_list.append(self._temp_lv_vol_min * 1000.0)
				self._esv_rv_list.append(self._temp_rv_vol_min * 1000.0)

				if self._edv_lv_list:
					self.edv_lv = sum(self._edv_lv_list) / len(self._edv_lv_list)
				if self._edv_rv_list:
					self.edv_rv = sum(self._edv_rv_list) / len(self._edv_rv_list)
				if self._esv_lv_list:
					self.esv_lv = sum(self._esv_lv_list) / len(self._esv_lv_list)
				if self._esv_rv_list:
					self.esv_rv = sum(self._esv_rv_list) / len(self._esv_rv_list)

				self.lv_sv = self.edv_lv - self.esv_lv
				self.rv_sv = self.edv_rv - self.esv_rv

				while len(self._edv_lv_list) > int(self.hr_avg_beats):
					self._edv_lv_list.pop(0)
					self._edv_rv_list.pop(0)
					self._esv_lv_list.pop(0)
					self._esv_rv_list.pop(0)

				self.edp_lv = self._temp_lv_pres_min
				self.esp_lv = self._temp_lv_pres_max
				self.edp_rv = self._temp_rv_pres_min
				self.esp_rv = self._temp_rv_pres_max

				self._temp_lv_pres_max = -1000.0
				self._temp_lv_pres_min = 1000.0
				self._temp_rv_pres_max = -1000.0
				self._temp_rv_pres_min = 1000.0
				self._temp_lv_vol_max = -1000.0
				self._temp_lv_vol_min = 1000.0
				self._temp_rv_vol_max = -1000.0
				self._temp_rv_vol_min = 1000.0

		if self._beats_counter > self.hr_avg_beats and self._beats_time > 0.0:
			if self._lv_aa is not None:
				self.lvo = (self._lvo_counter / self._beats_time) * 60.0
				self._lvo_counter = 0.0
			if self._rv_pa is not None:
				self.rvo = (self._rvo_counter / self._beats_time) * 60.0
				self._rvo_counter = 0.0
			if self._ivc_ra is not None:
				self.ivc_flow = (self._ivc_flow_counter / self._beats_time) * 60.0
				self._ivc_flow_counter = 0.0
			if self._svc_ra is not None:
				self.svc_flow = (self._svc_flow_counter / self._beats_time) * 60.0
				self._svc_flow_counter = 0.0
			if self._cor_ra is not None:
				self.cor_flow = (self._cor_flow_counter / self._beats_time) * 60.0
				self._cor_flow_counter = 0.0
			if self._aa_br is not None:
				self.brain_flow = (self._brain_flow_counter / self._beats_time) * 60.0
				self._brain_flow_counter = 0.0
				self.do2_br = self.brain_flow * self._safe_float(self._aa, "to2", 0.0) * 22.4
			if self._ad_kid is not None:
				self.kid_flow = (self._kid_flow_counter / self._beats_time) * 60.0
				self._kid_flow_counter = 0.0
				self.do2_lb = self.kid_flow * 4.0 * self._safe_float(self._ad, "to2", 0.0) * 22.4
			if self._da is not None:
				self.da_flow = (self._da_flow_counter / self._beats_time) * 60.0
				self._da_flow_counter = 0.0
			if self._fo is not None:
				self.fo_flow = (self._fo_flow_counter / self._beats_time) * 60.0
				self._fo_flow_counter = 0.0
			if self._vsd is not None:
				self.vsd_flow = (self._vsd_flow_counter / self._beats_time) * 60.0
				self._vsd_flow_counter = 0.0
			if self._ips is not None:
				self.ips_flow = (self._ips_flow_counter / self._beats_time) * 60.0
				self._ips_flow_counter = 0.0
			if self._ad_umb_art is not None:
				self.ua_flow = (self._ua_flow_counter / self._beats_time) * 60.0
				self._ua_flow_counter = 0.0
			if self._umb_ven_ivci is not None:
				self.uv_flow = (self._uv_flow_counter / self._beats_time) * 60.0
				self._uv_flow_counter = 0.0

			self._beats_counter = 0
			self._beats_time = 0.0

		self._qrs_interval_counter += self._t
		self._beats_time += self._t

		self.spo2 = self._safe_float(self._ad, "so2", self.spo2)
		self.spo2_pre = self._safe_float(self._aa, "so2", self.spo2_pre)
		self.spo2_ven = self._safe_float(self._ra, "so2", self.spo2_ven)

	def collect_signals(self):
		self.ecg_signal = self._safe_float(self._heart, "ecg_signal", 0.0)
		self.resp_signal = self._safe_float(self._thorax, "vol", 0.0)
		self.spo2_pre_signal = self._safe_float(self._aa, "pres_in", 0.0)
		self.spo2_signal = self._safe_float(self._ad, "pres_in", 0.0)
		self.abp_signal = self._safe_float(self._ad, "pres_in", 0.0)
		self.pap_signal = self._safe_float(self._pa, "pres_in", 0.0)
		self.cvp_signal = self._safe_float(self._ra, "pres_in", 0.0)
		self.co2_signal = self._safe_float(self._ventilator, "co2", 0.0)

	def collect_pressures(self):
		self._temp_aa_pres_max = max(self._temp_aa_pres_max, self._safe_float(self._aa, "pres_in", -1000.0)) if self._aa else -1000.0
		self._temp_aa_pres_min = min(self._temp_aa_pres_min, self._safe_float(self._aa, "pres_in", 1000.0)) if self._aa else 1000.0
		self._temp_lv_pres_max = max(self._temp_lv_pres_max, self._safe_float(self._lv, "pres_in", -1000.0)) if self._lv else -1000.0
		self._temp_lv_pres_min = min(self._temp_lv_pres_min, self._safe_float(self._lv, "pres_in", 1000.0)) if self._lv else 1000.0
		self._temp_rv_pres_max = max(self._temp_rv_pres_max, self._safe_float(self._rv, "pres_in", -1000.0)) if self._rv else -1000.0
		self._temp_rv_pres_min = min(self._temp_rv_pres_min, self._safe_float(self._rv, "pres_in", 1000.0)) if self._rv else 1000.0
		self._temp_lv_vol_max = max(self._temp_lv_vol_max, self._safe_float(self._lv, "vol", -1000.0)) if self._lv else -1000.0
		self._temp_lv_vol_min = min(self._temp_lv_vol_min, self._safe_float(self._lv, "vol", 1000.0)) if self._lv else 1000.0
		self._temp_rv_vol_max = max(self._temp_rv_vol_max, self._safe_float(self._rv, "vol", -1000.0)) if self._rv else -1000.0
		self._temp_rv_vol_min = min(self._temp_rv_vol_min, self._safe_float(self._rv, "vol", 1000.0)) if self._rv else 1000.0
		self._temp_ad_pres_max = max(self._temp_ad_pres_max, self._safe_float(self._ad, "pres_in", -1000.0)) if self._ad else -1000.0
		self._temp_ad_pres_min = min(self._temp_ad_pres_min, self._safe_float(self._ad, "pres_in", 1000.0)) if self._ad else 1000.0
		self._temp_ra_pres_max = max(self._temp_ra_pres_max, self._safe_float(self._ra, "pres_in", -1000.0)) if self._ra else -1000.0
		self._temp_ra_pres_min = min(self._temp_ra_pres_min, self._safe_float(self._ra, "pres_in", 1000.0)) if self._ra else 1000.0
		self._temp_pa_pres_max = max(self._temp_pa_pres_max, self._safe_float(self._pa, "pres_in", -1000.0)) if self._pa else -1000.0
		self._temp_pa_pres_min = min(self._temp_pa_pres_min, self._safe_float(self._pa, "pres_in", 1000.0)) if self._pa else 1000.0

	def collect_blood_flows(self):
		self._lvo_counter += self._safe_float(self._lv_aa, "flow", 0.0) * self._t
		self._rvo_counter += self._safe_float(self._rv_pa, "flow", 0.0) * self._t
		self._cor_flow_counter += self._safe_float(self._cor_ra, "flow", 0.0) * self._t
		self._ivc_flow_counter += self._safe_float(self._ivc_ra, "flow", 0.0) * self._t
		self._svc_flow_counter += self._safe_float(self._svc_ra, "flow", 0.0) * self._t
		self._brain_flow_counter += self._safe_float(self._aa_br, "flow", 0.0) * self._t
		self._kid_flow_counter += self._safe_float(self._ad_kid, "flow", 0.0) * self._t
		self._da_flow_counter += self._safe_float(self._da, "flow", 0.0) * self._t
		self._fo_flow_counter += self._safe_float(self._fo, "flow", 0.0) * self._t
		self._vsd_flow_counter += self._safe_float(self._vsd, "flow", 0.0) * self._t
		self._ips_flow_counter += self._safe_float(self._ips, "flow", 0.0) * self._t
		self._ua_flow_counter += self._safe_float(self._ad_umb_art, "flow", 0.0) * self._t
		self._uv_flow_counter += self._safe_float(self._umb_ven_ivci, "flow", 0.0) * self._t
