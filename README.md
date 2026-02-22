# explain-python

## Documentation

- [Model Structure](docs/model_structure.md)

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
