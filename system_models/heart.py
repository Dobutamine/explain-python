import math

from base_models.base_model import BaseModel


class Heart(BaseModel):
	"""Cardiac cycle controller coordinating chamber activation and timing."""

	model_type = "heart"

	def __init__(self, model_ref={}, name=None):
		"""Initialize heart timing, modulation factors, and cycle state."""
		super().__init__(model_ref=model_ref, name=name)

		self.heart_rate_ref = 110.0
		self.pq_time = 0.1
		self.qrs_time = 0.075
		self.qt_time = 0.25
		self.av_delay = 0.0005
		self.ans_sens = 1.0
		self.ans_activity = 1.0
		self.ans_activity_hr = 1.0
		self.hr_factor = 1.0
		self.hr_mob_factor = 1.0
		self.hr_temp_factor = 1.0
		self.hr_drug_factor = 1.0

		self.cont_factor = 1.0
		self.cont_factor_left = 1.0
		self.cont_factor_right = 1.0
		self.cont_mob_factor = 1.0
		self.cont_drug_factor = 1.0

		self.relax_factor = 1.0
		self.relax_factor_left = 1.0
		self.relax_factor_right = 1.0
		self.relax_mob_factor = 1.0
		self.relax_drug_factor = 1.0

		self.pc_el_factor = 1.0
		self.pc_extra_volume = 0.0

		self.heart_rate = 120.0
		self.heart_rate_measured = 120.0
		self.cardiac_cycle_state = 0

		self.ecg_signal = 0.0
		self.ncc_ventricular = 0
		self.ncc_atrial = 0
		self.cardiac_cycle_running = 0
		self.cardiac_cycle_time = 0.353

		self.lv_edv = 0.0
		self.lv_esv = 0.0
		self.lv_edp = 0.0
		self.lv_esp = 0.0
		self.lv_sp = 0.0
		self.lv_sv = 0.0
		self.lv_ef = 0.0

		self.rv_edv = 0.0
		self.rv_esv = 0.0
		self.rv_edp = 0.0
		self.rv_esp = 0.0
		self.rv_sp = 0.0
		self.rv_sv = 0.0
		self.rv_ef = 0.0

		self.ra_edv = 0.0
		self.ra_esv = 0.0
		self.ra_edp = 0.0
		self.ra_esp = 0.0
		self.ra_sp = 0.0

		self.la_edv = 0.0
		self.la_esv = 0.0
		self.la_edp = 0.0
		self.la_esp = 0.0
		self.la_sp = 0.0

		self._kn = 0.579
		self._prev_cardiac_cycle_running = 0
		self._prev_cardiac_cycle_state = 0
		self._temp_cardiac_cycle_time = 0.0
		self._sa_node_interval = 1.0
		self._sa_node_timer = 0.0
		self._av_delay_timer = 0.0
		self._pq_timer = 0.0
		self._pq_running = False
		self._av_delay_running = False
		self._qrs_timer = 0.0
		self._qrs_running = False
		self._ventricle_is_refractory = False
		self._qt_timer = 0.0
		self._qt_running = False

		self._la = None
		self._lv = None
		self._ra = None
		self._rv = None
		self._la_lv = None
		self._lv_aa = None
		self._ra_rv = None
		self._coronaries = None
		self._pc = None

		self._systole_running = False
		self._diastole_running = False

		self._prev_la_lv_flow = 0.0
		self._prev_lv_aa_flow = 0.0
		self._prev_cont_factor = 1.0
		self._prev_cont_factor_left = 1.0
		self._prev_cont_factor_right = 1.0
		self._prev_relax_factor = 1.0
		self._prev_relax_factor_left = 1.0
		self._prev_relax_factor_right = 1.0
		self._prev_pc_el_factor = 1.0
		self._hr_counter = 0.0
		self._hr_factor = 1.0

		self._update_counter_factors = 0.0
		self._update_interval_factors = 0.015

		self.aaf = 0.0
		self.vaf = 0.0
		self.cqt_time = self.qt_time

	def _resolve_model(self, component_name):
		"""Resolve a connected model by name from registry or engine."""
		if isinstance(self.model_ref, dict) and component_name in self.model_ref:
			return self.model_ref[component_name]

		model_engine = getattr(self, "_model_engine", None)
		if model_engine is not None:
			models = getattr(model_engine, "models", None)
			if isinstance(models, dict):
				return models.get(component_name)

		return None

	def analyze(self):
		"""Update derived chamber pressure/volume metrics over cycle transitions."""
		if self._prev_cardiac_cycle_state == 0 and self.cardiac_cycle_state == 1:
			self.lv_edv = self._lv.vol
			self.lv_edp = self._lv.pres_in
			self.rv_edv = self._rv.vol
			self.rv_edp = self._rv.pres_in

		if self._prev_cardiac_cycle_state == 1 and self.cardiac_cycle_state == 0:
			self.lv_esv = self._lv.vol
			self.lv_esp = self._lv.pres_in
			self.la_esv = self._la.vol
			self.la_esp = self._la.pres_in
			self.rv_esv = self._rv.vol
			self.rv_esp = self._rv.pres_in
			self.ra_esv = self._ra.vol
			self.ra_esp = self._ra.pres_in

		if self._prev_cardiac_cycle_state == 0 and self.cardiac_cycle_state == 1:
			self.lv_edv = self._lv.vol
			self.lv_esp = self._lv.pres_in
			self.la_edv = self._la.vol
			self.la_esp = self._la.pres_in
			self.rv_edv = self._rv.vol
			self.rv_esp = self._rv.pres_in
			self.ra_edv = self._ra.vol
			self.ra_esp = self._ra.pres_in

			self.lv_sv = self.lv_edv - self.lv_esv
			self.rv_sv = self.rv_edv - self.lv_edv
			self.lv_ef = self.lv_sv / self.lv_edv if self.lv_edv > 0 else 0.0
			self.rv_ef = self.rv_sv / self.rv_edv if self.rv_edv > 0 else 0.0

	def calc_model(self):
		"""Run one cardiac timing step and drive chamber activation factors."""
		self._la = self._resolve_model("LA")
		self._lv = self._resolve_model("LV")
		self._ra = self._resolve_model("RA")
		self._rv = self._resolve_model("RV")
		self._la_lv = self._resolve_model("LA_LV")
		self._ra_rv = self._resolve_model("RA_RV")
		self._lv_aa = self._resolve_model("LV_AA")
		self._coronaries = self._resolve_model("COR")
		self._pc = self._resolve_model("PERICARDIUM")

		if any(model is None for model in [self._la, self._lv, self._ra, self._rv, self._la_lv, self._lv_aa, self._coronaries, self._pc]):
			return

		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		self._update_counter_factors += time_step
		if self._update_counter_factors > self._update_interval_factors:
			self._update_counter_factors = 0.0

			cont_left = self.cont_factor_left
			cont_right = self.cont_factor_right
			if cont_left != self._prev_cont_factor_left or cont_right != self._prev_cont_factor_right:
				self.set_contractillity(cont_left, cont_right)
			self._prev_cont_factor_left = cont_left
			self._prev_cont_factor_right = cont_right

			relax_left = self.relax_factor_left
			relax_right = self.relax_factor_right
			if relax_left != self._prev_relax_factor_left or relax_right != self._prev_relax_factor_right:
				self.set_relaxation(relax_left, relax_right)
			self._prev_relax_factor_left = relax_left
			self._prev_relax_factor_right = relax_right

			pc_el = self.pc_el_factor
			if pc_el != self._prev_pc_el_factor:
				self.set_pericardium(pc_el, self.pc_extra_volume)
			self._prev_pc_el_factor = pc_el

			self._pc.vol_extra = self.pc_extra_volume

		self._prev_cardiac_cycle_running = self.cardiac_cycle_running
		self._prev_cardiac_cycle_state = self.cardiac_cycle_state

		if self._prev_la_lv_flow > 0.0 and self._la_lv.flow <= 0.0:
			self._systole_running = True
		self._prev_la_lv_flow = self._la_lv.flow

		if self._systole_running:
			if self._prev_lv_aa_flow > 0.0 and self._lv_aa.flow <= 0.0:
				self._systole_running = False
		self._prev_lv_aa_flow = self._lv_aa.flow

		if self._systole_running:
			self.cardiac_cycle_state = 1
			self._diastole_running = False
		else:
			self.cardiac_cycle_state = 0
			self._diastole_running = True

		self.heart_rate = (
			self.heart_rate_ref
			+ (self.ans_activity_hr - 1.0) * self.heart_rate_ref * self.ans_sens
			+ (self.hr_factor - 1.0) * self.heart_rate_ref
			+ (self.hr_mob_factor - 1.0) * self.heart_rate_ref
			+ (self.hr_temp_factor - 1.0) * self.heart_rate_ref
			+ (self.hr_drug_factor - 1.0) * self.heart_rate_ref
		)

		self.cqt_time = self.calc_qtc(self.heart_rate)
		self._sa_node_interval = 60.0 / self.heart_rate if self.heart_rate > 0 else 60.0

		if self._sa_node_timer > self._sa_node_interval:
			self._sa_node_timer = 0.0
			self._pq_running = True
			self.ncc_atrial = -1
			self.cardiac_cycle_running = 1
			self._temp_cardiac_cycle_time = 0.0

		if self._pq_timer > self.pq_time:
			self._pq_timer = 0.0
			self._pq_running = False
			self._av_delay_running = True

		if self._av_delay_timer > self.av_delay:
			self._av_delay_timer = 0.0
			self._av_delay_running = False
			if not self._ventricle_is_refractory:
				self._qrs_running = True
				self.ncc_ventricular = -1

		if self._qrs_timer > self.qrs_time:
			self._qrs_timer = 0.0
			self._qrs_running = False
			self._qt_running = True
			self._ventricle_is_refractory = True

		if self._qt_timer > self.cqt_time:
			self._qt_timer = 0.0
			self._qt_running = False
			self._ventricle_is_refractory = False
			self.cardiac_cycle_running = 0
			self.cardiac_cycle_time = self._temp_cardiac_cycle_time

		self._sa_node_timer += time_step

		if self.cardiac_cycle_running == 1:
			self._temp_cardiac_cycle_time += time_step

		if self._pq_running:
			self._pq_timer += time_step
			self.ecg_signal += self.gaussian(self._pq_timer, 0.05, self.pq_time / 2.0, self.pq_time)

		if self._av_delay_running:
			self._av_delay_timer += time_step

		if self._qrs_running:
			self._qrs_timer += time_step

		if self._qt_running:
			self._qt_timer += time_step

		if not self._pq_running and not self._av_delay_running and not self._qrs_running and not self._qt_running:
			self.ecg_signal = 0.0

		if self.ncc_ventricular == -1 and self._hr_counter > 0.0:
			self.heart_rate_measured = 60.0 / self._hr_counter
			self._hr_counter = 0.0
			self._hr_factor = 1.0

		if self._hr_counter > 1.0 * self._hr_factor and self._hr_counter > 0.0:
			self.heart_rate_measured = 60.0 / self._hr_counter
			self._hr_factor += 1.0

		self._hr_counter += time_step

		self.ncc_atrial += 1
		self.ncc_ventricular += 1

		self.calc_varying_elastance()

	def calc_varying_elastance(self):
		"""Compute atrial/ventricular activation waveforms and apply to chambers."""
		time_step = getattr(self, "_t", 0.0)
		if time_step <= 0.0:
			return

		atrial_duration = self.pq_time / time_step
		if self.ncc_atrial >= 0 and self.ncc_atrial < atrial_duration:
			self.aaf = math.sin(math.pi * (self.ncc_atrial / atrial_duration))
		else:
			self.aaf = 0.0

		ventricular_duration = (self.qrs_time + self.cqt_time) / time_step
		if self.ncc_ventricular >= 0 and self.ncc_ventricular < ventricular_duration:
			self.vaf = (self.ncc_ventricular / (self._kn * ventricular_duration)) * math.sin(
				math.pi * (self.ncc_ventricular / ventricular_duration)
			)
		else:
			self.vaf = 0.0

		for chamber in [self._la, self._ra, self._lv, self._rv]:
			chamber.ans_sens = self.ans_sens
			chamber.ans_activity = self.ans_activity

		self._la.act_factor = self.aaf
		self._ra.act_factor = self.aaf
		self._lv.act_factor = self.vaf
		self._rv.act_factor = self.vaf
		self._coronaries.act_factor = self.vaf

		self.analyze()

	def calc_qtc(self, hr):
		"""Return corrected QT duration using Bazett-style scaling."""
		if hr > 10.0:
			return self.qt_time * math.sqrt(60.0 / hr)
		return self.qt_time * 2.449

	def set_pericardium(self, new_el_factor, new_volume):
		"""Adjust persistent pericardial elastance factor."""
		f_pc_el = self._pc.el_base_factor_ps
		delta = new_el_factor - self._prev_pc_el_factor
		f_pc_el = max(f_pc_el + delta, 0.0)
		self._pc.el_base_factor_ps = f_pc_el

	def set_contractillity(self, new_cont_factor_left, new_cont_factor_right):
		"""Adjust persistent chamber contractility factors (left/right)."""
		f_ps_la = self._la.el_max_factor_ps
		f_ps_lv = self._lv.el_max_factor_ps
		f_ps_ra = self._ra.el_max_factor_ps
		f_ps_rv = self._rv.el_max_factor_ps

		delta_left = new_cont_factor_left - self._prev_cont_factor_left
		delta_right = new_cont_factor_right - self._prev_cont_factor_right

		f_ps_la = max(f_ps_la + delta_left, 0.0)
		f_ps_lv = max(f_ps_lv + delta_left, 0.0)
		f_ps_ra = max(f_ps_ra + delta_right, 0.0)
		f_ps_rv = max(f_ps_rv + delta_right, 0.0)

		self._la.el_max_factor_ps = f_ps_la
		self._lv.el_max_factor_ps = f_ps_lv
		self._ra.el_max_factor_ps = f_ps_ra
		self._rv.el_max_factor_ps = f_ps_rv

		self.cont_factor_left = new_cont_factor_left
		self.cont_factor_right = new_cont_factor_right

	def set_relaxation(self, new_relax_factor_left, new_relax_factor_right):
		"""Adjust persistent chamber relaxation factors (left/right)."""
		f_ps_la = self._la.el_min_factor_ps
		f_ps_lv = self._lv.el_min_factor_ps
		f_ps_ra = self._ra.el_min_factor_ps
		f_ps_rv = self._rv.el_min_factor_ps

		delta_left = new_relax_factor_left - self._prev_relax_factor_left
		delta_right = new_relax_factor_right - self._prev_relax_factor_right

		f_ps_la = max(f_ps_la + delta_left, 0.0)
		f_ps_lv = max(f_ps_lv + delta_left, 0.0)
		f_ps_ra = max(f_ps_ra + delta_right, 0.0)
		f_ps_rv = max(f_ps_rv + delta_right, 0.0)

		self._la.el_min_factor_ps = f_ps_la
		self._lv.el_min_factor_ps = f_ps_lv
		self._ra.el_min_factor_ps = f_ps_ra
		self._rv.el_min_factor_ps = f_ps_rv

		self.relax_factor_left = new_relax_factor_left
		self.relax_factor_right = new_relax_factor_right

	def gaussian(self, t, amp, center, width):
		"""Return Gaussian pulse value for ECG waveform synthesis."""
		return amp * math.exp(-((t - center) ** 2) / (2.0 * width * width))
