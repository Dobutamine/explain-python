import math

from base_models.base_model import BaseModel
from functions.blood_composition import calc_blood_composition
from functions.gas_composition import calc_gas_composition
from helpers.realtime_moving_average import RealTimeMovingAverage

class Ecls(BaseModel):
	"""Extracorporeal life support (ECLS/ECMO) circuit controller."""

	model_type = "ecls"

	def __init__(self, model_ref={}, name=None):
		"""Initialize ECLS configuration, runtime metrics, and component references."""
		super().__init__(model_ref=model_ref, name=name)

		self.ecls_running = False
		self.ecls_mode = "VA-ECMO"
		self.pres_atm = 760.0
		self.tubing_clamped = True
		self.tubing_diameter = 0.25
		self.tubing_elastance = 11600.0
		self.tubing_in_length = 1.0
		self.tubing_out_length = 1.0
		self.drainage_origin = "RA"
		self.return_target = "AAR"
		self.drainage_cannula_diameter = 12.0
		self.drainage_cannula_length = 0.11
		self.return_cannula_diameter = 12.0
		self.return_cannula_length = 0.11
		self.pump_volume = 0.014
		self.pump_resistance = 50.0
		self.pump_elastance = 15000.0
		self.pump_occlusive = False
		self.oxy_volume = 0.031
		self.oxy_resistance = 50.0
		self.oxy_elastance = 15000.0
		self.oxy_dif_o2 = 0.0001
		self.oxy_dif_co2 = 0.0001
		self.gas_flow = 0.5
		self.fio2_gas = 0.3
		self.co2_gas_flow = 0.0
		self.temp_gas = 37.0
		self.humidity_gas = 0.5
		self.pump_rpm = 2250.0

		self.blood_flow = 0.0
		self.p_ven = 0.0
		self.p_int = 0.0
		self.p_art = 0.0
		self.p_tmp = 0.0
		self.pre_oxy_bloodgas = {}
		self.post_oxy_bloodgas = {}
		self.pre_oxy_ph = 0.0
		self.pre_oxy_hco3 = 0.0
		self.pre_oxy_be = 0.0
		self.pre_oxy_so2 = 0.0
		self.pre_oxy_po2 = 0.0
		self.pre_oxy_pco2 = 0.0
		self.post_oxy_so2 = 0.0
		self.post_oxy_po2 = 0.0
		self.post_oxy_pco2 = 0.0
		self.post_oxy_ph = 0.0
		self.post_oxy_hco3 = 0.0
		self.post_oxy_be = 0.0
		self.drainage_resistance = 20.0
		self.return_resistance = 20.0
		self.tubin_resistance = 20.0
		self.tubout_resistance = 20.0
		self.tubin_volume = 0.0
		self.tubout_volume = 0.0

		self._drainage = None
		self._tubin = None
		self._tubin_pump = None
		self._tubin_oxy = None
		self._pump = None
		self._pump_oxy = None
		self._pump_tubout = None
		self._oxy = None
		self._oxy_tubout = None
		self._tubout = None
		self._return = None
		self._gasin = None
		self._gasin_oxy = None
		self._gasoxy = None
		self._gasoxy_gasout = None
		self._gasout = None
		self._gasex = None
		self._is_oxy_circuit = True
		self._is_pump_circuit = True

		self._fico2_gas = 0.0004
		self._update_interval = 0.015
		self._update_counter = 0.0
		self._bloodgas_interval = 1.0
		self._bloodgas_counter = 0.0
		self._prev_ecls_state = False

		self._flow_average = RealTimeMovingAverage(3000)
		self._pven_average = RealTimeMovingAverage(300)
		self._pint_average = RealTimeMovingAverage(300)
		self._part_average = RealTimeMovingAverage(300)

	def _resolve_model(self, model_name):
		"""Resolve a circuit component by name from registry or engine."""
		if not model_name:
			return None
		if isinstance(self.model_ref, dict):
			return self.model_ref.get(model_name)
		engine = getattr(self, "_model_engine", None)
		if engine is not None:
			models = getattr(engine, "models", None)
			if isinstance(models, dict):
				return models.get(model_name)
		return None

	def init_model(self, args=None):
		"""Resolve circuit components and apply initial ECLS configuration."""
		super().init_model(args)

		self._drainage = self._resolve_model("ECLS_DRAINAGE")
		self._tubin = self._resolve_model("ECLS_TUBIN")
		self._tubin_pump = self._resolve_model("ECLS_TUBIN_PUMP")
		self._tubin_oxy = self._resolve_model("ECLS_TUBIN_OXY")
		self._pump = self._resolve_model("ECLS_PUMP")
		self._pump_oxy = self._resolve_model("ECLS_PUMP_OXY")
		self._pump_tubout = self._resolve_model("ECLS_PUMP_TUBOUT")
		self._oxy = self._resolve_model("ECLS_OXY")
		self._oxy_tubout = self._resolve_model("ECLS_OXY_TUBOUT")
		self._tubout = self._resolve_model("ECLS_TUBOUT")
		self._return = self._resolve_model("ECLS_RETURN")
		self._gasin = self._resolve_model("ECLS_GASIN")
		self._gasin_oxy = self._resolve_model("ECLS_GASIN_OXY")
		self._gasoxy = self._resolve_model("ECLS_GASOXY")
		self._gasoxy_gasout = self._resolve_model("ECLS_OXY_GASOUT")
		self._gasout = self._resolve_model("ECLS_GASOUT")
		self._gasex = self._resolve_model("ECLS_GASEX")

		model_time_total = float(getattr(self._model_engine, "model_time_total", 0.0) or 0.0)
		if model_time_total == 0.0:
			self.set_ecls_mode(self.ecls_mode)
			if self._drainage is not None:
				self._drainage.comp_from = self.drainage_origin
			if self._return is not None:
				self._return.comp_to = self.return_target
			if self._pump_oxy is not None:
				self._pump_oxy.no_back_flow = self.pump_occlusive

			self.calc_resistances()
			self.calc_tubing_volumes()
			self.set_pump_volume(self.pump_volume)
			self.set_oxygenator_volume(self.oxy_volume)

			self.set_gas_volumes()
			self.set_gas_compositions()
			self.set_gas_flow(self.gas_flow)
			self.set_gas_exchanger()

			self.tubing_clamped = True
			self.switch_blood_components(self.ecls_running)
			self.switch_gas_components(self.ecls_running)

	def calc_model(self):
		"""Run one ECLS control/update step for flow, pressures, and gas settings."""
		if self.ecls_running and self._return is not None:
			self.blood_flow = self._flow_average.add_value(float(getattr(self._return, "flow", 0.0) or 0.0) * 60.0)

		self._update_counter += getattr(self, "_t", 0.0)
		self._bloodgas_counter += getattr(self, "_t", 0.0)

		if self._update_counter <= self._update_interval:
			return

		self._update_counter = 0.0

		if self.ecls_running != self._prev_ecls_state:
			self.switch_ecls(self.ecls_running)
			self._prev_ecls_state = self.ecls_running

		if self._tubin is not None:
			self.p_ven = self._pven_average.add_value(float(getattr(self._tubin, "pres", 0.0) or 0.0))
		if self._pump is not None:
			pump_pres = float(getattr(self._pump, "pres", 0.0) or 0.0)
			if not math.isnan(pump_pres):
				self.p_int = self._pint_average.add_value(pump_pres)
		if self._tubout is not None:
			self.p_art = self._part_average.add_value(float(getattr(self._tubout, "pres", 0.0) or 0.0))
		self.p_tmp = self.p_int - self.p_art

		self.calc_bloodgas()
		self.pre_oxy_ph = self.pre_oxy_bloodgas.get("ph", 0.0)
		self.pre_oxy_hco3 = self.pre_oxy_bloodgas.get("hco3", 0.0)
		self.pre_oxy_be = self.pre_oxy_bloodgas.get("be", 0.0)
		self.pre_oxy_so2 = self.pre_oxy_bloodgas.get("so2", 0.0)
		self.pre_oxy_po2 = self.pre_oxy_bloodgas.get("po2", 0.0)
		self.pre_oxy_pco2 = self.pre_oxy_bloodgas.get("pco2", 0.0)
		self.post_oxy_ph = self.post_oxy_bloodgas.get("ph", 0.0)
		self.post_oxy_hco3 = self.post_oxy_bloodgas.get("hco3", 0.0)
		self.post_oxy_be = self.post_oxy_bloodgas.get("be", 0.0)
		self.post_oxy_so2 = self.post_oxy_bloodgas.get("so2", 0.0)
		self.post_oxy_po2 = self.post_oxy_bloodgas.get("po2", 0.0)
		self.post_oxy_pco2 = self.post_oxy_bloodgas.get("pco2", 0.0)

		if self._pump is not None:
			self._pump.pump_rpm = self.pump_rpm
		if self._pump_oxy is not None:
			self._pump_oxy.no_back_flow = self.pump_occlusive

		if self._gasin_oxy is not None and self._gasin is not None:
			gas_flow_lps = self.gas_flow / 60.0
			if gas_flow_lps > 0.0:
				res = (float(getattr(self._gasin, "pres", self.pres_atm) or self.pres_atm) - self.pres_atm) / gas_flow_lps
				self._gasin_oxy.r_for = res
				self._gasin_oxy.r_back = res

		total_gas_flow = self.gas_flow + (self.co2_gas_flow / 1000.0)
		added_fico2 = (self.co2_gas_flow * 0.001 / total_gas_flow) if total_gas_flow > 0 else 0.0
		self._fico2_gas = 0.0004 + added_fico2
		if self._gasin is not None:
			calc_gas_composition(self._gasin, self.fio2_gas, self.temp_gas, self.humidity_gas, self._fico2_gas)

		if self._drainage is not None:
			self._drainage.no_flow = self.tubing_clamped
		if self._return is not None:
			self._return.no_flow = self.tubing_clamped

	def switch_ecls(self, state):
		"""Enable or disable ECLS blood and gas sub-circuits."""
		self.ecls_running = bool(state)
		self.switch_blood_components(self.ecls_running)
		self.switch_gas_components(self.ecls_running)

	def set_ecls_mode(self, new_mode):
		"""Set ECLS operating mode and update circuit topology switches."""
		self.ecls_mode = str(new_mode)
		if self.ecls_mode in {"VA-ECMO", "VV-ECMO"}:
			self._is_oxy_circuit = True
			self._is_pump_circuit = True
		elif self.ecls_mode in {"RVAD", "LVAD", "BIVAD"}:
			self._is_oxy_circuit = False
			self._is_pump_circuit = True
		elif self.ecls_mode == "WHOMB":
			self._is_oxy_circuit = True
			self._is_pump_circuit = False

		self.switch_blood_components(self.ecls_running)
		self.switch_gas_components(self.ecls_running)

	def set_clamp(self, state):
		self.tubing_clamped = bool(state)

	def set_pump_rpm(self, new_rpm):
		self.pump_rpm = float(new_rpm)
		if self._pump is not None:
			self._pump.pump_rpm = self.pump_rpm

	def set_gas_flow(self, new_gas_flow):
		new_gas_flow = float(new_gas_flow)
		if self._gasin_oxy is None:
			self.gas_flow = max(new_gas_flow, 0.0)
			return
		if new_gas_flow > 0.0 and self._gasin is not None:
			self.gas_flow = new_gas_flow
			self._gasin_oxy.no_flow = False
			res = (float(getattr(self._gasin, "pres", self.pres_atm) or self.pres_atm) - self.pres_atm) / (self.gas_flow / 60.0)
			self._gasin_oxy.r_for = res
			self._gasin_oxy.r_back = res
		else:
			self.gas_flow = max(new_gas_flow, 0.0)
			self._gasin_oxy.no_flow = True

	def set_fio2(self, new_fio2):
		value = float(new_fio2)
		self.fio2_gas = value / 100.0 if value > 1.0 else value

	def set_co2_flow(self, new_co2_flow):
		value = float(new_co2_flow)
		if value >= 0.0:
			self.co2_gas_flow = value

	def set_tubing_diameter(self, new_diameter):
		value = float(new_diameter)
		if value <= 0.0:
			return
		self.tubing_diameter = value
		self.calc_tubing_volumes()
		self.calc_resistances()

	def set_tubing_in_length(self, new_length):
		value = float(new_length)
		if value <= 0.0:
			return
		self.tubing_in_length = value
		self.calc_tubing_volumes()
		self.calc_resistances()

	def set_tubing_out_length(self, new_length):
		value = float(new_length)
		if value <= 0.0:
			return
		self.tubing_out_length = value
		self.calc_tubing_volumes()
		self.calc_resistances()

	def set_oxygenator_volume(self, new_volume):
		value = float(new_volume)
		if value < 0.0:
			return
		self.oxy_volume = value
		if self._oxy is not None:
			self._oxy.u_vol = value
			if hasattr(self._oxy, "vol"):
				self._oxy.vol = value
			if hasattr(self._oxy, "calc_pressure"):
				self._oxy.calc_pressure()

	def set_pump_occlusive(self, state):
		self.pump_occlusive = bool(state)
		if self._pump_oxy is not None:
			self._pump_oxy.no_back_flow = self.pump_occlusive

	def set_drainage_origin(self, new_target):
		self.drainage_origin = str(new_target)
		if self._drainage is not None:
			self._drainage.comp_from = self.drainage_origin

	def set_return_target(self, new_target):
		self.return_target = str(new_target)
		if self._return is not None:
			self._return.comp_to = self.return_target

	def set_pump_volume(self, new_volume):
		value = float(new_volume)
		if value < 0.0:
			return
		self.pump_volume = value
		if self._pump is not None:
			self._pump.u_vol = value
			if hasattr(self._pump, "vol"):
				self._pump.vol = value
			if hasattr(self._pump, "calc_pressure"):
				self._pump.calc_pressure()

	def switch_blood_components(self, state=True):
		state = bool(state)
		if self._drainage is not None:
			self._drainage.is_enabled = state
			self._drainage.no_flow = self.tubing_clamped
		if self._tubin is not None:
			self._tubin.is_enabled = state

		if self._is_pump_circuit:
			if self._pump is not None:
				self._pump.is_enabled = state
			if self._pump_oxy is not None:
				self._pump_oxy.is_enabled = state
				self._pump_oxy.no_flow = not state
			if self._tubin_oxy is not None:
				self._tubin_oxy.is_enabled = False
				self._tubin_oxy.no_flow = True
		else:
			if self._pump is not None:
				self._pump.is_enabled = False
			if self._pump_oxy is not None:
				self._pump_oxy.is_enabled = False
				self._pump_oxy.no_flow = True
			if self._tubin_oxy is not None:
				self._tubin_oxy.is_enabled = state
				self._tubin_oxy.no_flow = not state

		if self._tubin_pump is not None:
			self._tubin_pump.is_enabled = state
			self._tubin_pump.no_flow = not state

		if self._is_oxy_circuit:
			if self._oxy is not None:
				self._oxy.is_enabled = state
			if self._oxy_tubout is not None:
				self._oxy_tubout.is_enabled = state
				self._oxy_tubout.no_flow = not state
			if self._pump_tubout is not None:
				self._pump_tubout.is_enabled = False
				self._pump_tubout.no_flow = True
		else:
			if self._oxy is not None:
				self._oxy.is_enabled = False
			if self._oxy_tubout is not None:
				self._oxy_tubout.is_enabled = False
				self._oxy_tubout.no_flow = True
			if self._pump_tubout is not None:
				self._pump_tubout.is_enabled = state
				self._pump_tubout.no_flow = not state

		if self._tubout is not None:
			self._tubout.is_enabled = state
		if self._return is not None:
			self._return.is_enabled = state
			self._return.no_flow = self.tubing_clamped

	def calc_bloodgas(self):
		if self._bloodgas_counter <= self._bloodgas_interval:
			return
		self._bloodgas_counter = 0.0

		if self._tubin is not None and getattr(self._tubin, "is_enabled", True):
			calc_blood_composition(self._tubin)
			self.pre_oxy_bloodgas = {
				"ph": getattr(self._tubin, "ph", 0.0),
				"pco2": getattr(self._tubin, "pco2", 0.0),
				"po2": getattr(self._tubin, "po2", 0.0),
				"hco3": getattr(self._tubin, "hco3", 0.0),
				"be": getattr(self._tubin, "be", 0.0),
				"so2": getattr(self._tubin, "so2", 0.0),
			}

		if self._tubout is not None and getattr(self._tubout, "is_enabled", True):
			calc_blood_composition(self._tubout)
			self.post_oxy_bloodgas = {
				"ph": getattr(self._tubout, "ph", 0.0),
				"pco2": getattr(self._tubout, "pco2", 0.0),
				"po2": getattr(self._tubout, "po2", 0.0),
				"hco3": getattr(self._tubout, "hco3", 0.0),
				"be": getattr(self._tubout, "be", 0.0),
				"so2": getattr(self._tubout, "so2", 0.0),
			}

	def calc_resistances(self):
		self.drainage_resistance = self._calc_tube_resistance(self.drainage_cannula_diameter * 0.00033, self.drainage_cannula_length)
		self.tubin_resistance = self._calc_tube_resistance(self.tubing_diameter * 0.0254, self.tubing_in_length)
		if self._drainage is not None:
			self._drainage.r_for = self.drainage_resistance + self.tubin_resistance
			self._drainage.r_back = self.drainage_resistance + self.tubin_resistance

		if self._tubin_pump is not None:
			self._tubin_pump.r_for = self.pump_resistance
			self._tubin_pump.r_back = self.pump_resistance

		if self._pump_oxy is not None:
			self._pump_oxy.r_for = self.oxy_resistance
			self._pump_oxy.r_back = self.oxy_resistance

		self.tubout_resistance = self._calc_tube_resistance(self.tubing_diameter * 0.0254, self.tubing_out_length)
		if self._oxy_tubout is not None:
			self._oxy_tubout.r_for = self.tubout_resistance
			self._oxy_tubout.r_back = self.tubout_resistance

		self.return_resistance = self._calc_tube_resistance(self.return_cannula_diameter * 0.00033, self.return_cannula_length)
		if self._return is not None:
			self._return.r_for = self.return_resistance
			self._return.r_back = self.return_resistance

	def set_drainage_cannula_diameter(self, new_diameter):
		value = float(new_diameter)
		if value > 1.0:
			self.drainage_cannula_diameter = value
			self.calc_resistances()

	def set_return_cannula_diameter(self, new_diameter):
		value = float(new_diameter)
		if value > 1.0:
			self.return_cannula_diameter = value
			self.calc_resistances()

	def set_drainage_cannula_length(self, new_length):
		value = float(new_length)
		if value > 0.01:
			self.drainage_cannula_length = value
			self.calc_resistances()

	def set_return_cannula_length(self, new_length):
		value = float(new_length)
		if value > 0.01:
			self.return_cannula_length = value
			self.calc_resistances()

	def calc_tubing_volumes(self):
		self.tubin_volume = self._calc_tube_volume(self.tubing_diameter * 0.0254, self.tubing_in_length)
		self.tubout_volume = self._calc_tube_volume(self.tubing_diameter * 0.0254, self.tubing_out_length)

		if self._tubin is not None:
			self._tubin.vol = self.tubin_volume
			self._tubin.u_vol = self.tubin_volume
			self._tubin.el_base = self.tubing_elastance
			if hasattr(self._tubin, "calc_pressure"):
				self._tubin.calc_pressure()

		if self._tubout is not None:
			self._tubout.vol = self.tubout_volume
			self._tubout.u_vol = self.tubout_volume
			self._tubout.el_base = self.tubing_elastance
			if hasattr(self._tubout, "calc_pressure"):
				self._tubout.calc_pressure()

	def switch_gas_components(self, state=True):
		state = bool(state)
		enabled = state and self._is_oxy_circuit

		for component in [self._gasin, self._gasoxy, self._gasout, self._gasex]:
			if component is not None:
				component.is_enabled = enabled

		if self._gasin_oxy is not None:
			self._gasin_oxy.is_enabled = enabled
			self._gasin_oxy.no_flow = not enabled

		if self._gasoxy_gasout is not None:
			self._gasoxy_gasout.is_enabled = enabled
			self._gasoxy_gasout.no_flow = not enabled

	def set_gas_exchanger(self):
		if self._gasex is not None:
			self._gasex.dif_o2 = self.oxy_dif_o2
			self._gasex.dif_co2 = self.oxy_dif_co2

	def set_gas_volumes(self):
		if self._gasin is not None:
			self._gasin.vol = 5.4
			self._gasin.u_vol = 5.0
			self._gasin.el_base = 1000.0
			self._gasin.fixed_composition = True
			if hasattr(self._gasin, "calc_pressure"):
				self._gasin.calc_pressure()

		if self._gasoxy is not None:
			self._gasoxy.vol = 0.031
			self._gasoxy.u_vol = 0.031
			self._gasoxy.el_base = 10000.0
			self._gasoxy.fixed_composition = False
			if hasattr(self._gasoxy, "calc_pressure"):
				self._gasoxy.calc_pressure()

		if self._gasout is not None:
			self._gasout.vol = 5.0
			self._gasout.u_vol = 5.0
			self._gasout.el_base = 1000.0
			self._gasout.fixed_composition = True
			if hasattr(self._gasout, "calc_pressure"):
				self._gasout.calc_pressure()

	def set_gas_compositions(self):
		"""Recompute gas compositions for ECLS gas compartments."""
		total_gas_flow = self.gas_flow + (self.co2_gas_flow / 1000.0)
		added_fico2 = (self.co2_gas_flow * 0.001 / total_gas_flow) if total_gas_flow > 0 else 0.0
		self._fico2_gas = 0.0004 + added_fico2

		if self._gasin is not None:
			calc_gas_composition(self._gasin, self.fio2_gas, self.temp_gas, self.humidity_gas, self._fico2_gas)
		if self._gasoxy is not None:
			calc_gas_composition(self._gasoxy, self.fio2_gas, self.temp_gas, self.humidity_gas, self._fico2_gas)
		if self._gasout is not None:
			calc_gas_composition(self._gasout, 0.205, 20.0, 0.1, 0.0004)

	def _calc_tube_volume(self, diameter, length):
		"""Return tube volume in mL for diameter (m) and length (m)."""
		return math.pi * math.pow(0.5 * float(diameter), 2) * float(length) * 1000.0

	def _calc_tube_resistance(self, diameter, length, viscosity=6.0):
		"""Return Poiseuille-based tube resistance estimate."""
		n_pas = float(viscosity) / 1000.0
		radius_meters = float(diameter) / 2.0
		if radius_meters <= 0.0 or float(length) <= 0.0:
			return 1e8
		res = (8.0 * n_pas * float(length)) / (math.pi * math.pow(radius_meters, 4))
		return res * 0.00000750062
