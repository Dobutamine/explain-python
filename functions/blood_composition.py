import math


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
KW = 2.5119e-11
KC = 7.94328235e-4
KD = 6.0255959e-8
ALPHA_CO2P = 0.03067
LEFT_HP_WIDE = 5.848931925e-6
RIGHT_HP_WIDE = 3.16227766017e-4
DELTA_PH_LIMITS = 0.1
N_HILL = 2.7
LEFT_O2_WIDE = 0.0
RIGHT_O2_WIDE = 800.0
DELTA_O2_LIMITS = 10.0
BRENT_ACCURACY = 1e-8
MAX_ITERATIONS = 100
GAS_CONSTANT = 62.36367


# -----------------------------------------------------------------------------
# Independent variables
# -----------------------------------------------------------------------------
P50_0 = 20.0
P50 = 0.0
LOG10_P50 = 0.0
P50_N = 0.0
LEFT_O2 = LEFT_O2_WIDE
RIGHT_O2 = RIGHT_O2_WIDE
LEFT_HP = LEFT_HP_WIDE
RIGHT_HP = RIGHT_HP_WIDE


# -----------------------------------------------------------------------------
# State variables
# -----------------------------------------------------------------------------
PH = 0.0
PO2 = 0.0
SO2 = 0.0
PCO2 = 0.0
HCO3 = 0.0
BE = 0.0
TO2 = 0.0
HEMOGLOBIN = 0.0
DPG = 5.0
TEMP = 0.0
TCO2 = 0.0
SID = 0.0
ALBUMIN = 0.0
PHOSPHATES = 0.0
UMA = 0.0
PREV_PH = 7.37
PREV_PO2 = 18.7


def _bc_get(container, key, default=None):
	if isinstance(container, dict):
		return container.get(key, default)
	return getattr(container, key, default)


def _bc_set(container, key, value):
	if isinstance(container, dict):
		container[key] = value
	else:
		setattr(container, key, value)


def calc_blood_composition(bc):
	_calc_blood_composition_py(bc)


def _calc_blood_composition_py(bc):
	global TCO2, TO2, SID, ALBUMIN, PHOSPHATES, UMA, HEMOGLOBIN, TEMP
	global PREV_PH, PREV_PO2, LEFT_HP, RIGHT_HP, PH, PCO2, HCO3, BE
	global LOG10_P50, P50, P50_N, LEFT_O2, RIGHT_O2

	solutes = _bc_get(bc, "solutes", {}) or {}

	TCO2 = _bc_get(bc, "tco2", 0.0)
	TO2 = _bc_get(bc, "to2", 0.0)

	SID = (
		solutes.get("na", 0.0)
		+ solutes.get("k", 0.0)
		+ 2.0 * solutes.get("ca", 0.0)
		+ 2.0 * solutes.get("mg", 0.0)
		- solutes.get("cl", 0.0)
		- solutes.get("lact", 0.0)
	)

	ALBUMIN = solutes.get("albumin", 0.0)
	PHOSPHATES = solutes.get("phosphates", 0.0)
	UMA = solutes.get("uma", 0.0)
	HEMOGLOBIN = solutes.get("hemoglobin", 0.0)
	TEMP = _bc_get(bc, "temp", 37.0)

	PREV_PH = _bc_get(bc, "prev_ph", 7.37) or 7.37
	PREV_PO2 = _bc_get(bc, "prev_po2", 18.7) or 18.7

	LEFT_HP = LEFT_HP_WIDE
	RIGHT_HP = RIGHT_HP_WIDE

	if PREV_PH > 0:
		LEFT_HP = math.pow(10.0, -(PREV_PH + DELTA_PH_LIMITS)) * 1000.0
		RIGHT_HP = math.pow(10.0, -(PREV_PH - DELTA_PH_LIMITS)) * 1000.0

	hp = _brent_root_finding(_net_charge_plasma, LEFT_HP, RIGHT_HP, MAX_ITERATIONS, BRENT_ACCURACY)
	if hp <= 0:
		LEFT_HP = max(LEFT_HP_WIDE, 0.0)
		RIGHT_HP = RIGHT_HP_WIDE
		hp = _brent_root_finding(_net_charge_plasma, LEFT_HP, RIGHT_HP, MAX_ITERATIONS, BRENT_ACCURACY)

	if hp > 0:
		BE = (HCO3 - 25.1 + (2.3 * HEMOGLOBIN + 7.7) * (PH - 7.4)) * (1.0 - 0.023 * HEMOGLOBIN)
		_bc_set(bc, "ph", PH)
		_bc_set(bc, "pco2", PCO2)
		_bc_set(bc, "hco3", HCO3)
		_bc_set(bc, "be", BE)

	dp_h = PH - 7.40
	dp_co2 = PCO2 - 40.0
	delta_temp = TEMP - 37.0
	delta_dpg = DPG - 5.0

	LOG10_P50 = math.log10(P50_0) - 0.48 * dp_h + 0.014 * dp_co2 + 0.024 * delta_temp + 0.051 * delta_dpg
	P50 = math.pow(10.0, LOG10_P50)
	P50_N = math.pow(P50, N_HILL)

	dynamic_limits_used = False
	LEFT_O2 = LEFT_O2_WIDE
	RIGHT_O2 = RIGHT_O2_WIDE

	if PREV_PO2 > 0:
		LEFT_O2 = max(PREV_PO2 - DELTA_O2_LIMITS, 0.0)
		RIGHT_O2 = PREV_PO2 + DELTA_O2_LIMITS
		dynamic_limits_used = True

	po2_value = _brent_root_finding(_do2_content, LEFT_O2, RIGHT_O2, MAX_ITERATIONS, BRENT_ACCURACY)
	if po2_value <= -1 and dynamic_limits_used:
		LEFT_O2 = LEFT_O2_WIDE
		RIGHT_O2 = RIGHT_O2_WIDE
		po2_value = _brent_root_finding(_do2_content, LEFT_O2, RIGHT_O2, MAX_ITERATIONS, BRENT_ACCURACY)

	if po2_value > -1:
		_bc_set(bc, "po2", po2_value)
		_bc_set(bc, "so2", SO2 * 100.0)
		_bc_set(bc, "prev_po2", po2_value)


def _net_charge_plasma(hp_estimate):
	global PH, HCO3, PCO2

	PH = -math.log10(hp_estimate / 1000.0)

	cco2p = TCO2 / (1.0 + KC / hp_estimate + (KC * KD) / (hp_estimate * hp_estimate))
	HCO3 = (KC * cco2p) / hp_estimate
	co3p = (KD * HCO3) / hp_estimate
	ohp = KW / hp_estimate

	PCO2 = cco2p / ALPHA_CO2P

	a_base = ALBUMIN * (0.123 * PH - 0.631) + PHOSPHATES * (0.309 * PH - 0.469)

	return hp_estimate + SID - HCO3 - 2.0 * co3p - ohp - a_base - UMA


def _calc_so2(po2_estimate):
	po2_n = math.pow(po2_estimate, N_HILL)
	denominator = po2_n + P50_N
	return po2_n / denominator


def _do2_content(po2_estimate):
	global SO2

	SO2 = _calc_so2(po2_estimate)

	to2_new_estimate = (0.0031 * po2_estimate + 1.36 * (HEMOGLOBIN / 0.6206) * SO2) * 10.0

	mmol_to_ml = (GAS_CONSTANT * (273.15 + TEMP)) / 760.0
	to2_new_estimate = to2_new_estimate / mmol_to_ml

	return TO2 - to2_new_estimate


def _brent_root_finding(function, left_bound, right_bound, max_iter, tolerance):
	f_left = function(left_bound)
	f_right = function(right_bound)

	if f_left * f_right > 0:
		return -1

	if abs(f_left) < abs(f_right):
		left_bound, right_bound = right_bound, left_bound
		f_left, f_right = f_right, f_left

	third_point = left_bound
	f_third = f_left
	previous_third = 0.0
	use_bisection = True
	iterations = 0

	try:
		while iterations < max_iter:
			if abs(f_left) < abs(f_right):
				left_bound, right_bound = right_bound, left_bound
				f_left, f_right = f_right, f_left

			if f_left != f_third and f_right != f_third:
				lag0 = (left_bound * f_right * f_third) / ((f_left - f_right) * (f_left - f_third))
				lag1 = (right_bound * f_left * f_third) / ((f_right - f_left) * (f_right - f_third))
				lag2 = (third_point * f_right * f_left) / ((f_third - f_left) * (f_third - f_right))
				new_point = lag0 + lag1 + lag2
			else:
				new_point = right_bound - (f_right * (right_bound - left_bound)) / (f_right - f_left)

			out_of_bounds = new_point < (3 * left_bound + right_bound) / 4 or new_point > right_bound
			poor_progress_bisect = use_bisection and abs(new_point - right_bound) >= abs(right_bound - third_point) / 2
			poor_progress_interp = (not use_bisection) and abs(new_point - right_bound) >= abs(third_point - previous_third) / 2
			tiny_interval_bisect = use_bisection and abs(right_bound - third_point) < tolerance
			tiny_interval_interp = (not use_bisection) and abs(third_point - previous_third) < tolerance

			if out_of_bounds or poor_progress_bisect or poor_progress_interp or tiny_interval_bisect or tiny_interval_interp:
				new_point = (left_bound + right_bound) / 2
				use_bisection = True
			else:
				use_bisection = False

			f_new = function(new_point)
			previous_third = third_point
			third_point = right_bound
			f_third = f_right

			if f_left * f_new < 0:
				right_bound = new_point
				f_right = f_new
			else:
				left_bound = new_point
				f_left = f_new

			iterations += 1

			if abs(f_new) < tolerance:
				return new_point
	except Exception:
		return -1

	return -1
