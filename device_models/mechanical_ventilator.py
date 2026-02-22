from collections.abc import Mapping

from base_models.base_model import BaseModel
from functions.gas_composition import calc_gas_composition


class MechanicalVentilator(BaseModel):
	model_type = "mechanical_ventilator"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.pres_atm = 760.0
		self.fio2 = 0.205
		self.humidity = 1.0
		self.temp = 37.0
		self.ettube_diameter = 4.0
		self.ettube_length = 110.0
		self.vent_mode = "PRVC"
		self.vent_rate = 40.0
		self.tidal_volume = 0.015
		self.insp_time = 0.4
		self.insp_flow = 12.0
		self.exp_flow = 3.0
		self.pip_cmh2o = 14.0
		self.pip_cmh2o_max = 14.0
		self.peep_cmh2o = 3.0
		self.trigger_volume_perc = 6.0
		self.synchronized = False

		self.components = {}

		self.pres = 0.0
		self.flow = 0.0
		self.vol = 0.0
		self.exp_time = 1.0
		self.trigger_volume = 0.0
		self.minute_volume = 0.0
		self.compliance = 0.0
		self.resistance = 0.0
		self.exp_tidal_volume = 0.0
		self.insp_tidal_volume = 0.0
		self.ncc_insp = 0.0
		self.ncc_exp = 0.0
		self.etco2 = 0.0
		self.co2 = 0.0
		self.triggered_breath = False
		self.tv_kg = 0.0

		self._vent_gasin = None
		self._vent_gascircuit = None
		self._vent_gasout = None
		self._vent_insp_valve = None
		self._vent_exp_valve = None
		self._vent_ettube = None
		self._ventilator_parts = []
		self._ettube_length_ref = 110.0
		self._pip = 0.0
		self._pip_max = 0.0
		self._peep = 0.0
		self._a = 0.0
		self._b = 0.0
		self._insp_time_counter = 0.0
		self._exp_time_counter = 0.0
		self._insp_tidal_volume_counter = 0.0
		self._exp_tidal_volume_counter = 0.0
		self._trigger_volume_counter = 0.0
		self._inspiration = False
		self._expiration = True
		self._tv_tolerance = 0.0005
		self._trigger_blocked = False
		self._trigger_start = False
		self._breathing_model = None
		self._peak_flow = 0.0
		self._prev_et_tube_flow = 0.0
		self._et_tube_resistance = 40.0

	def _resolve_model(self, model_name):
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
		linked_components = None
		if args is not None:
			normalized = dict(args) if isinstance(args, Mapping) else self._normalize_init_args(args)
			linked_components = normalized.pop("components", None)
			super().init_model(normalized)
			if linked_components is not None:
				self.components = linked_components
		else:
			super().init_model(args)

		self._breathing_model = self._resolve_model("Breathing")
		self._vent_gasin = self._resolve_model("VENT_GASIN")
		self._vent_gascircuit = self._resolve_model("VENT_GASCIRCUIT")
		self._vent_gasout = self._resolve_model("VENT_GASOUT")
		self._vent_insp_valve = self._resolve_model("VENT_INSP_VALVE")
		self._vent_ettube = self._resolve_model("VENT_ETTUBE")
		self._vent_exp_valve = self._resolve_model("VENT_EXP_VALVE")

		self._ventilator_parts = [
			self._vent_gasin,
			self._vent_gascircuit,
			self._vent_gasout,
			self._vent_insp_valve,
			self._vent_ettube,
			self._vent_exp_valve,
		]

		if self._vent_gasin is not None:
			calc_gas_composition(self._vent_gasin, self.fio2, self.temp, self.humidity)
		if self._vent_gascircuit is not None:
			calc_gas_composition(self._vent_gascircuit, self.fio2, self.temp, self.humidity)
		if self._vent_gasout is not None:
			calc_gas_composition(self._vent_gasout, 0.205, 20.0, 0.5)

		self.set_ettube_diameter(self.ettube_diameter)
		self._et_tube_resistance = self.calc_ettube_resistance(self.flow)

	def calc_model(self):
		if not self.is_enabled:
			return
		if self._vent_gascircuit is None or self._vent_ettube is None:
			return

		self._pip = self.pip_cmh2o / 1.35951
		self._pip_max = self.pip_cmh2o_max / 1.35951
		self._peep = self.peep_cmh2o / 1.35951

		if self.synchronized:
			self.triggering()

		if self.vent_mode in {"PC", "PRVC"}:
			self.time_cycling()
			self.pressure_control()
		elif self.vent_mode == "PS":
			self.flow_cycling()
			self.pressure_control()

		self.pres = (float(getattr(self._vent_gascircuit, "pres", self.pres_atm) or self.pres_atm) - self.pres_atm) * 1.35951
		self.flow = float(getattr(self._vent_ettube, "flow", 0.0) or 0.0) * 60.0
		self.vol += float(getattr(self._vent_ettube, "flow", 0.0) or 0.0) * 1000.0 * self._t

		ds = self._resolve_model("DS")
		if ds is not None:
			self.co2 = float(getattr(ds, "pco2", 0.0) or 0.0)

		self.minute_volume = self.exp_tidal_volume * self.vent_rate
		if self.exp_tidal_volume > 0.0 and (self._pip - self._peep) != 0.0:
			self.compliance = 1.0 / ((self._pip - self._peep) / self.exp_tidal_volume)
		else:
			self.compliance = 0.0
		self.resistance = None
		self._et_tube_resistance = self.calc_ettube_resistance(self.flow)

	def triggering(self):
		self.trigger_volume = (self.tidal_volume / 100.0) * self.trigger_volume_perc
		if self._breathing_model is not None:
			if float(getattr(self._breathing_model, "ncc_insp", 0.0) or 0.0) == 1.0 and not self._trigger_blocked:
				self._trigger_start = True

		if self._trigger_start and self._vent_ettube is not None:
			self._trigger_volume_counter += float(getattr(self._vent_ettube, "flow", 0.0) or 0.0) * self._t

		if self._trigger_volume_counter > self.trigger_volume:
			self._trigger_volume_counter = 0.0
			self._exp_time_counter = self.exp_time
			self._trigger_start = False
			self.triggered_breath = True

	def flow_cycling(self):
		flow = float(getattr(self._vent_ettube, "flow", 0.0) or 0.0)

		if flow > 0.0 and self.triggered_breath:
			if flow > self._prev_et_tube_flow:
				self._inspiration = True
				self._expiration = False
				self.ncc_insp = -1
				if flow > self._peak_flow:
					self._peak_flow = flow
				self.exp_tidal_volume = -self._exp_tidal_volume_counter
			elif flow < 0.3 * self._peak_flow:
				self._inspiration = False
				self._expiration = True
				self.ncc_exp = -1
				self._exp_tidal_volume_counter = 0.0
				self.triggered_breath = False

			self._prev_et_tube_flow = flow

		if flow < 0.0 and not self.triggered_breath:
			self._peak_flow = 0.0
			self._prev_et_tube_flow = 0.0
			self._inspiration = False
			self._expiration = True
			self.ncc_exp = -1
			self._exp_tidal_volume_counter += flow * self._t

		if self._inspiration:
			self.ncc_insp += 1
			self._trigger_blocked = True

		if self._expiration:
			self.ncc_exp += 1
			self._trigger_blocked = False

	def time_cycling(self):
		if self.vent_rate <= 0.0:
			return
		self.exp_time = 60.0 / self.vent_rate - self.insp_time

		if self._insp_time_counter > self.insp_time:
			self._insp_time_counter = 0.0
			self.insp_tidal_volume = self._insp_tidal_volume_counter
			self._insp_tidal_volume_counter = 0.0
			self._inspiration = False
			self._expiration = True
			self.triggered_breath = False
			self.ncc_exp = -1

		if self._exp_time_counter > self.exp_time:
			self._exp_time_counter = 0.0
			self._inspiration = True
			self._expiration = False
			self.ncc_insp = -1
			self.vol = 0.0
			self.exp_tidal_volume = -self._exp_tidal_volume_counter

			ds = self._resolve_model("DS")
			if ds is not None:
				self.etco2 = float(getattr(ds, "pco2", 0.0) or 0.0)

			weight = float(getattr(self._model_engine, "weight", 0.0) or 0.0)
			if weight > 0.0:
				self.tv_kg = (self.exp_tidal_volume * 1000.0) / weight

			if self.exp_tidal_volume > 0.0:
				self.compliance = 1.0 / (((self._pip - self._peep) * 1.35951) / (self.exp_tidal_volume * 1000.0))

			self._exp_tidal_volume_counter = 0.0

			if self.vent_mode == "PRVC":
				self.pressure_regulated_volume_control()

		if self._inspiration:
			self._insp_time_counter += self._t
			self.ncc_insp += 1
			self._trigger_blocked = True
			self._trigger_volume_counter = 0.0

		if self._expiration:
			self._exp_time_counter += self._t
			self.ncc_exp += 1
			self._trigger_blocked = False

	def pressure_control(self):
		if self._vent_exp_valve is None or self._vent_insp_valve is None or self._vent_gasin is None or self._vent_gascircuit is None:
			return

		if self._inspiration:
			self._vent_exp_valve.no_flow = True
			self._vent_insp_valve.no_flow = False
			self._vent_insp_valve.no_back_flow = True
			if self.insp_flow > 0.0:
				self._vent_insp_valve.r_for = (
					float(getattr(self._vent_gasin, "pres", self.pres_atm) or self.pres_atm)
					+ self._pip
					- self.pres_atm
					- self._peep
				) / (self.insp_flow / 60.0)

			if float(getattr(self._vent_gascircuit, "pres", self.pres_atm) or self.pres_atm) > self._pip + self.pres_atm:
				self._vent_insp_valve.no_flow = True

			et_flow = float(getattr(self._vent_ettube, "flow", 0.0) or 0.0)
			if et_flow > 0.0:
				self._insp_tidal_volume_counter += et_flow * self._t

		if self._expiration:
			self._vent_insp_valve.no_flow = True
			self._vent_exp_valve.no_flow = False
			self._vent_exp_valve.no_back_flow = True
			self._vent_exp_valve.r_for = 10.0

			if self._vent_gasout is not None:
				el_base = float(getattr(self._vent_gasout, "el_base", 0.0) or 0.0)
				u_vol = float(getattr(self._vent_gasout, "u_vol", 0.0) or 0.0)
				if el_base > 0.0:
					self._vent_gasout.vol = self._peep / el_base + u_vol

			et_flow = float(getattr(self._vent_ettube, "flow", 0.0) or 0.0)
			if et_flow < 0.0:
				self._exp_tidal_volume_counter += et_flow * self._t

	def pressure_regulated_volume_control(self):
		if self.exp_tidal_volume < self.tidal_volume - self._tv_tolerance:
			self.pip_cmh2o += 1.0
			if self.pip_cmh2o > self.pip_cmh2o_max:
				self.pip_cmh2o = self.pip_cmh2o_max

		if self.exp_tidal_volume > self.tidal_volume + self._tv_tolerance:
			self.pip_cmh2o -= 1.0
			if self.pip_cmh2o < self.peep_cmh2o + 2.0:
				self.pip_cmh2o = self.peep_cmh2o + 2.0

	def reset_dependent_properties(self):
		self.pres = 0.0
		self.flow = 0.0
		self.vol = 0.0
		self.exp_time = 1.0
		self.trigger_volume = 0.0
		self.minute_volume = 0.0
		self.compliance = 0.0
		self.resistance = 0.0
		self.exp_tidal_volume = 0.0
		self.insp_tidal_volume = 0.0
		self.ncc_insp = 0.0
		self.ncc_exp = 0.0
		self.etco2 = 0.0
		self.co2 = 0.0
		self.triggered_breath = False

	def switch_ventilator(self, state):
		state = bool(state)
		self.is_enabled = state
		if not state:
			self.reset_dependent_properties()

		for vp in self._ventilator_parts:
			if vp is None:
				continue
			vp.is_enabled = state
			if hasattr(vp, "no_flow"):
				vp.no_flow = not state

		mouth_ds = self._resolve_model("MOUTH_DS")
		if mouth_ds is not None and hasattr(mouth_ds, "no_flow"):
			mouth_ds.no_flow = state

	def calc_ettube_resistance(self, flow):
		flow = float(flow)
		res = (self._a * flow + self._b) * (self.ettube_length / self._ettube_length_ref)
		if res < 15.0:
			res = 15.0

		if self._vent_ettube is not None:
			self._vent_ettube.r_for = res
			self._vent_ettube.r_back = res

		return res

	def set_ettube_length(self, new_length):
		new_length = float(new_length)
		if new_length >= 50.0:
			self.ettube_length = new_length

	def set_ettube_diameter(self, new_diameter):
		new_diameter = float(new_diameter)
		if new_diameter > 1.5:
			self.ettube_diameter = new_diameter
			self._a = -2.375 * new_diameter + 11.9375
			self._b = -14.375 * new_diameter + 65.9374

	def set_fio2(self, new_fio2):
		new_fio2 = float(new_fio2)
		if new_fio2 > 20.0:
			self.fio2 = new_fio2 / 100.0
		else:
			self.fio2 = new_fio2

		if self._vent_gasin is not None:
			calc_gas_composition(
				self._vent_gasin,
				self.fio2,
				float(getattr(self._vent_gasin, "temp", self.temp) or self.temp),
				float(getattr(self._vent_gasin, "humidity", self.humidity) or self.humidity),
			)

	def set_humidity(self, new_humidity):
		new_humidity = float(new_humidity)
		if 0.0 <= new_humidity <= 1.0:
			self.humidity = new_humidity
			if self._vent_gasin is not None:
				calc_gas_composition(
					self._vent_gasin,
					self.fio2,
					float(getattr(self._vent_gasin, "temp", self.temp) or self.temp),
					self.humidity,
				)

	def set_temp(self, new_temp):
		self.temp = float(new_temp)
		if self._vent_gasin is not None:
			calc_gas_composition(
				self._vent_gasin,
				self.fio2,
				self.temp,
				float(getattr(self._vent_gasin, "humidity", self.humidity) or self.humidity),
			)

	def set_pc(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0):
		self.pip_cmh2o = float(pip)
		self.pip_cmh2o_max = float(pip)
		self.peep_cmh2o = float(peep)
		self.vent_rate = float(rate)
		self.insp_time = float(t_in)
		self.insp_flow = float(insp_flow)
		self.vent_mode = "PC"

	def set_prvc(self, pip_max=18.0, peep=4.0, rate=40.0, tv=15.0, t_in=0.4, insp_flow=10.0):
		self.pip_cmh2o_max = float(pip_max)
		self.peep_cmh2o = float(peep)
		self.vent_rate = float(rate)
		self.insp_time = float(t_in)
		self.tidal_volume = float(tv) / 1000.0
		self.insp_flow = float(insp_flow)
		self.vent_mode = "PRVC"

	def set_psv(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0):
		self.pip_cmh2o = float(pip)
		self.pip_cmh2o_max = float(pip)
		self.peep_cmh2o = float(peep)
		self.vent_rate = float(rate)
		self.insp_time = float(t_in)
		self.insp_flow = float(insp_flow)
		self.vent_mode = "PS"

	def trigger_breath(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0):
		self._exp_time_counter = self.exp_time + 0.1


class Ventilator(MechanicalVentilator):
	model_type = "ventilator"
