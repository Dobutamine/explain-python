import math

from base_models.base_model import BaseModel


class Resuscitation(BaseModel):
	model_type = "resuscitation"

	def __init__(self, model_ref={}, name=None):
		super().__init__(model_ref=model_ref, name=name)

		self.cpr_enabled = False
		self.chest_comp_freq = 100.0
		self.chest_comp_max_pres = 10.0
		self.chest_comp_targets = {"THORAX": 0.1}
		self.chest_comp_no = 15
		self.chest_comp_cont = False

		self.vent_freq = 30.0
		self.vent_no = 2
		self.vent_pres_pip = 16.0
		self.vent_pres_peep = 5.0
		self.vent_insp_time = 1.0
		self.vent_fio2 = 0.21

		self.chest_comp_pres = 0.0

		self._ventilator = None
		self._breathing = None
		self._comp_timer = 0.0
		self._comp_counter = 0
		self._comp_pause = False
		self._comp_pause_interval = 2.0
		self._comp_pause_counter = 0.0
		self._vent_interval = 0.0
		self._vent_counter = 0.0

	def _resolve_model(self, *candidate_names):
		for model_name in candidate_names:
			if not model_name:
				continue
			if isinstance(self.model_ref, dict) and model_name in self.model_ref:
				return self.model_ref[model_name]
			engine = getattr(self, "_model_engine", None)
			if engine is None:
				continue
			models = getattr(engine, "models", None)
			if isinstance(models, dict) and model_name in models:
				return models[model_name]
		return None

	def init_model(self, args=None):
		super().init_model(args)

		self._ventilator = self._resolve_model("Ventilator", "VENT", "MechanicalVentilator")
		self._breathing = self._resolve_model("Breathing")

		if self._ventilator is not None:
			self.set_fio2(self.vent_fio2)

	def calc_model(self):
		if not self.cpr_enabled:
			return

		vent_freq = float(self.vent_freq)
		vent_no = float(self.vent_no)
		if vent_freq > 0.0 and vent_no > 0.0:
			self._comp_pause_interval = (60.0 / vent_freq) * vent_no
			self._vent_interval = self._comp_pause_interval / vent_no + self._t
		else:
			self._comp_pause_interval = 0.0
			self._vent_interval = 0.0

		if self._ventilator is not None:
			if self.chest_comp_cont:
				self._ventilator.vent_rate = self.vent_freq
			else:
				self._ventilator.vent_rate = 1.0

		if self._comp_pause:
			self._comp_pause_counter += self._t

			if self._comp_pause_counter > self._comp_pause_interval:
				self._comp_pause = False
				self._comp_pause_counter = 0.0
				self._comp_counter = 0
				self._vent_counter = 0.0

			self._vent_counter += self._t
			if self._vent_counter > self._vent_interval:
				self._vent_counter = 0.0
				if self._ventilator is not None and hasattr(self._ventilator, "trigger_breath"):
					self._ventilator.trigger_breath()
		else:
			a = self.chest_comp_max_pres / 2.0
			f = self.chest_comp_freq / 60.0
			self.chest_comp_pres = a * math.sin(2.0 * math.pi * f * self._comp_timer - 0.5 * math.pi) + a

			self._comp_timer += self._t
			if self.chest_comp_freq > 0.0 and self._comp_timer > 60.0 / self.chest_comp_freq:
				self._comp_timer = 0.0
				self._comp_counter += 1

		if self._comp_counter >= self.chest_comp_no and not self.chest_comp_cont:
			self._comp_pause = True
			self._comp_pause_counter = 0.0
			self._comp_counter = 0
			if self._ventilator is not None and hasattr(self._ventilator, "trigger_breath"):
				self._ventilator.trigger_breath()

		for target_name, force_factor in self.chest_comp_targets.items():
			target_model = self._resolve_model(target_name)
			if target_model is None:
				continue
			target_model.pres_cc = self.chest_comp_pres * float(force_factor)

	def switch_cpr(self, state):
		state = bool(state)
		if state:
			if self._ventilator is not None:
				if hasattr(self._ventilator, "switch_ventilator"):
					self._ventilator.switch_ventilator(True)
				if hasattr(self._ventilator, "set_pc"):
					self._ventilator.set_pc(
						self.vent_pres_pip,
						self.vent_pres_peep,
						1.0,
						self.vent_insp_time,
						5.0,
					)
			if self._breathing is not None and hasattr(self._breathing, "switch_breathing"):
				self._breathing.switch_breathing(False)
			self.cpr_enabled = True
		else:
			self.cpr_enabled = False

	def set_fio2(self, new_fio2):
		self.vent_fio2 = float(new_fio2)
		if self._ventilator is not None and hasattr(self._ventilator, "set_fio2"):
			self._ventilator.set_fio2(self.vent_fio2)
