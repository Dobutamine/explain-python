import math

from base_models.base_model import BaseModel


class Placenta(BaseModel):
	model_type = "placenta"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.placenta_running = False
		self.umb_art_vol = 0.0162
		self.umb_art_el_base = 20000.0
		self.umb_art_res = 7200.0
		self.umb_art_res_factor = 1.0
		self.umb_ven_vol = 0.0319
		self.umb_ven_el_base = 1000.0
		self.umb_ven_res = 1000.0
		self.umb_ven_res_factor = 1.0
		self.umb_length = 0.55
		self.umb_art_diameter = 0.0043
		self.umb_ven_diameter = 0.0086
		self.plf_res = 50.0
		self.plf_vol = 0.427
		self.plf_el_base = 25000.0
		self.plm_vol = 0.5
		self.plm_el_base = 5000.0
		self.dif_o2 = 0.01
		self.dif_co2 = 0.01
		self.mat_to2 = 6.85
		self.mat_tco2 = 23.0
		self.umb_clamped = True

		self.umb_art_flow = 0.0
		self.umb_art_velocity = 0.0
		self.umb_ven_flow = 0.0
		self.umb_ven_velocity = 0.0
		self.mat_po2 = 0.0
		self.mat_pco2 = 0.0

		self._update_interval = 0.015
		self._update_counter = 0.0

	def _models(self):
		if isinstance(self.model_ref, dict):
			return self.model_ref

		engine = getattr(self, "_model_engine", None)
		if engine is not None:
			models = getattr(engine, "models", None)
			if isinstance(models, dict):
				return models

		return {}

	def _model(self, name):
		return self._models().get(name)

	def init_model(self, args=None):
		super().init_model(args)

		engine = getattr(self, "_model_engine", None)
		model_time_total = float(getattr(engine, "model_time_total", 0.0) or 0.0)
		if model_time_total == 0.0:
			self.build_placenta()

		self.switch_placenta(self.placenta_running)

	def calc_model(self):
		ad_umb_art = self._model("AD_UMB_ART")
		if ad_umb_art is not None:
			self.umb_art_flow = float(getattr(ad_umb_art, "flow", 0.0) or 0.0) * 60.0

		umb_ven_ivci = self._model("UMB_VEN_IVCI")
		if umb_ven_ivci is not None:
			self.umb_ven_flow = float(getattr(umb_ven_ivci, "flow", 0.0) or 0.0) * 60.0

		art_area = math.pi * math.pow(self.umb_art_diameter / 2.0, 2.0)
		ven_area = math.pi * math.pow(self.umb_ven_diameter / 2.0, 2.0)
		self.umb_art_velocity = ((self.umb_art_flow / 1000.0) / 60.0) / art_area if art_area > 0.0 else 0.0
		self.umb_ven_velocity = ((self.umb_ven_flow / 1000.0) / 60.0) / ven_area if ven_area > 0.0 else 0.0

		time_step = getattr(self, "_t", 0.0)
		self._update_counter += time_step
		if self._update_counter <= self._update_interval or not self.placenta_running:
			return

		self._update_counter = 0.0

		if ad_umb_art is not None:
			ad_umb_art.no_flow = self.umb_clamped
			ad_umb_art.r_for = self.umb_art_res
			ad_umb_art.r_back = self.umb_art_res

		if umb_ven_ivci is not None:
			umb_ven_ivci.no_flow = self.umb_clamped

		umb_art_plf = self._model("UMB_ART_PLF")
		if umb_art_plf is not None:
			umb_art_plf.r_for = self.plf_res
			umb_art_plf.r_back = self.plf_res

		plf_umb_ven = self._model("PLF_UMB_VEN")
		if plf_umb_ven is not None:
			plf_umb_ven.r_for = self.umb_ven_res
			plf_umb_ven.r_back = self.umb_ven_res

		umb_art = self._model("UMB_ART")
		if umb_art is not None:
			umb_art.el_base = self.umb_art_el_base
			umb_art.u_vol = self.umb_art_vol

		umb_ven = self._model("UMB_VEN")
		if umb_ven is not None:
			umb_ven.el_base = self.umb_ven_el_base
			umb_ven.u_vol = self.umb_ven_vol

		plf = self._model("PLF")
		if plf is not None:
			plf.el_base = self.plf_el_base
			plf.u_vol = self.plf_vol

		pl_gasex = self._model("PL_GASEX")
		if pl_gasex is not None:
			pl_gasex.dif_o2 = self.dif_o2
			pl_gasex.dif_co2 = self.dif_co2

		plm = self._model("PLM")
		if plm is not None:
			plm.to2 = self.mat_to2
			plm.tco2 = self.mat_tco2

	def switch_placenta(self, state):
		state = bool(state)
		self.is_enabled = state
		self.placenta_running = state

		ad_umb_art = self._model("AD_UMB_ART")
		if ad_umb_art is not None:
			ad_umb_art.is_enabled = state
			ad_umb_art.no_flow = self.umb_clamped

		umb_art = self._model("UMB_ART")
		if umb_art is not None:
			umb_art.is_enabled = state

		umb_art_plf = self._model("UMB_ART_PLF")
		if umb_art_plf is not None:
			umb_art_plf.is_enabled = state
			umb_art_plf.no_flow = not state

		plf = self._model("PLF")
		if plf is not None:
			plf.is_enabled = state

		plf_umb_ven = self._model("PLF_UMB_VEN")
		if plf_umb_ven is not None:
			plf_umb_ven.is_enabled = state
			plf_umb_ven.no_flow = not state

		plm = self._model("PLM")
		if plm is not None:
			plm.is_enabled = state

		pl_gasex = self._model("PL_GASEX")
		if pl_gasex is not None:
			pl_gasex.is_enabled = state

		umb_ven = self._model("UMB_VEN")
		if umb_ven is not None:
			umb_ven.is_enabled = state

		umb_ven_ivci = self._model("UMB_VEN_IVCI")
		if umb_ven_ivci is not None:
			umb_ven_ivci.is_enabled = state
			umb_ven_ivci.no_flow = self.umb_clamped

	def build_placenta(self):
		ad_umb_art = self._model("AD_UMB_ART")
		if ad_umb_art is not None:
			ad_umb_art.no_flow = self.umb_clamped
			ad_umb_art.no_back_flow = False
			ad_umb_art.r_for = self.umb_art_res
			ad_umb_art.r_back = self.umb_art_res

		umb_art = self._model("UMB_ART")
		if umb_art is not None:
			umb_art.vol = self.umb_art_vol
			umb_art.u_vol = self.umb_art_vol
			umb_art.el_base = self.umb_art_el_base

		umb_art_plf = self._model("UMB_ART_PLF")
		if umb_art_plf is not None:
			umb_art_plf.no_flow = not self.placenta_running
			umb_art_plf.no_back_flow = False
			umb_art_plf.r_for = self.plf_res
			umb_art_plf.r_back = self.plf_res

		plf = self._model("PLF")
		if plf is not None:
			plf.vol = self.plf_vol
			plf.u_vol = self.plf_vol
			plf.el_base = self.plf_el_base

		pl_gasex = self._model("PL_GASEX")
		if pl_gasex is not None:
			pl_gasex.dif_o2 = self.dif_o2
			pl_gasex.dif_co2 = self.dif_co2

		plm = self._model("PLM")
		if plm is not None:
			plm.vol = self.plm_vol
			plm.u_vol = self.plm_vol
			plm.el_base = self.plm_el_base

		plf_umb_ven = self._model("PLF_UMB_VEN")
		if plf_umb_ven is not None:
			plf_umb_ven.no_flow = not self.placenta_running
			plf_umb_ven.no_back_flow = False
			plf_umb_ven.r_for = self.umb_ven_res
			plf_umb_ven.r_back = self.umb_ven_res

		umb_ven = self._model("UMB_VEN")
		if umb_ven is not None:
			umb_ven.vol = self.umb_ven_vol
			umb_ven.u_vol = self.umb_ven_vol
			umb_ven.el_base = self.umb_ven_el_base

		umb_ven_ivci = self._model("UMB_VEN_IVCI")
		if umb_ven_ivci is not None:
			umb_ven_ivci.no_flow = self.umb_clamped
			umb_ven_ivci.no_back_flow = False
			umb_ven_ivci.r_for = 50.0
			umb_ven_ivci.r_back = 50.0

	def clamp_umbilical_cord(self, state):
		self.umb_clamped = bool(state)

	def set_umbilical_arteries_resistance(self, new_res):
		self.umb_art_res = float(new_res)

	def set_umbilical_vein_resistance(self, new_res):
		self.umb_ven_res = float(new_res)

	def set_fetal_placenta_resistance(self, new_res):
		self.plf_res = float(new_res)

	def set_dif_o2(self, new_dif_o2):
		self.dif_o2 = float(new_dif_o2)

	def set_dif_co2(self, new_dif_co2):
		self.dif_co2 = float(new_dif_co2)

	def set_mat_to2(self, new_to2):
		self.mat_to2 = float(new_to2)

	def set_mat_tco2(self, new_tco2):
		self.mat_tco2 = float(new_tco2)
