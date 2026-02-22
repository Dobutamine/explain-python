# explain-python

## Documentation

- [Model Structure](docs/model_structure.md)
- Heart system components include [HeartChamber](derived_models/heart_chamber.py).

## Setup (PyPy)

```bash
pypy3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
python model_engine.py
```

## ModelEngine Usage

Load a model definition from JSON:

```python
from model_engine import ModelEngine

engine = ModelEngine().load_json_file("definitions/example_minimal.json")
print(engine.is_initialized)
print(sorted(engine.models.keys()))
```

Build directly from a Python dictionary:

```python
from model_engine import ModelEngine

definition = {
	"general": {"modeling_stepsize": 0.01},
	"components": {
		"C1": {"model_type": "capacitance", "is_enabled": True, "vol": 0.2, "u_vol": 0.1, "el_base": 5.0},
		"R1": {"model_type": "resistor", "is_enabled": True, "comp_from": "C1", "comp_to": "C1", "r_for": 100.0, "r_back": 100.0}
	}
}

engine = ModelEngine().build(definition)
engine.step_model()
```

## Translation Scenario Coverage

Use these isolated definitions to validate translated JS→Python system models quickly:

```bash
python scripts/smoke_translations.py
```

| Scenario | Definition | Primary model(s) | Quick check |
| --- | --- | --- | --- |
| Baseline integration | `definitions/baseline.json` | `PDA`, `MOB`, `SHUNTS`, `MVU` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/baseline.json'); e.step_model(); print(e.is_initialized)"` |
| Patent ductus arteriosus | `definitions/pda.json` | `PDA` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/pda.json'); e.step_model(); print(round(e.models['PDA'].res_ao,3), round(e.models['PDA'].res_pa,3))"` |
| Cardiac shunts | `definitions/shunts.json` | `SHUNTS` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/shunts.json'); e.step_model(); s=e.models['SHUNTS']; print(round(s.res_fo,3), round(s.res_vsd,3))"` |
| Placental circulation | `definitions/placenta.json` | `PLACENTA` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/placenta.json'); e.step_model(); p=e.models['PLACENTA']; print(round(p.umb_art_flow,6), round(p.umb_ven_flow,6))"` |
| Fluid administration | `definitions/fluids.json` | `FL` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/fluids.json'); fl=e.models['FL']; b=e.models['VLB'].vol; fl.add_volume(30, in_time=0.03, fluid_in='normal_saline', site='VLB'); e.step_model(); e.step_model(); print(round(b,6), round(e.models['VLB'].vol,6))"` |
| ANS afferent/efferent | `definitions/ans.json` | `ANS_AFF`, `ANS_EFF` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/ans.json'); b=e.models['R1'].r_factor_ps; e.step_model(); print(round(b,6), round(e.models['R1'].r_factor_ps,6))"` |
| ECLS device model | `definitions/ecls.json` | `ECLS` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/ecls.json'); [e.step_model() for _ in range(120)]; x=e.models['ECLS']; print(x.ecls_running, round(x.blood_flow,6), round(x.p_art,3))"` |
| Mechanical ventilator | `definitions/ventilator.json` | `VENT` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/ventilator.json'); [e.step_model() for _ in range(120)]; v=e.models['VENT']; print(v.vent_mode, round(v.pres,3), round(v.flow,3))"` |
| Resuscitation controller | `definitions/resuscitation.json` | `RESUS` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/resuscitation.json'); r=e.models['RESUS']; r.switch_cpr(True); [e.step_model() for _ in range(300)]; print(r.cpr_enabled, round(r.chest_comp_pres,3), e.models['VENT'].vent_mode)"` |
| Physiologic monitor | `definitions/monitor.json` | `MON` | `python -c "from model_engine import ModelEngine; e=ModelEngine().load_json_file('definitions/monitor.json'); [e.step_model() for _ in range(120)]; m=e.models['MON']; print(round(m.heart_rate,3), round(m.abp_signal,3), round(m.etco2,3))"` |

Helper translations also include `helpers/realtime_moving_average.py`, and `ECLS` now reuses this shared helper implementation.

## Blood Composition Example

```python
from functions.blood_composition import calc_blood_composition

bc = {
	"name": "arterial",
	"temp": 37.0,
	"tco2": 24.0,
	"to2": 8.0,
	"prev_ph": 7.37,
	"prev_po2": 18.7,
	"solutes": {
		"na": 140.0,
		"k": 4.0,
		"ca": 1.2,
		"mg": 0.8,
		"cl": 104.0,
		"lact": 1.0,
		"albumin": 42.0,
		"phosphates": 1.2,
		"uma": 0.0,
		"hemoglobin": 9.0,
	},
}

calc_blood_composition(bc)

print(bc["ph"], bc["pco2"], bc["hco3"], bc["be"], bc["po2"], bc["so2"])
```

## Gas Composition Example

```python
from functions.gas_composition import calc_gas_composition

gc = {
	"name": "alveolar_gas",
	"pres": 760.0,
}

calc_gas_composition(gc, fio2=0.21, temp=37.0, humidity=1.0, fico2=0.0004)

print(gc["po2"], gc["pco2"], gc["pn2"], gc["fo2"], gc["fco2"], gc["fn2"])
```
