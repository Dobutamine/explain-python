# Explain Model — Complete Documentation

## 1) What this project is

**Explain** is a modular physiology simulation engine in Python. It builds a runtime model graph from JSON definitions, initializes model components, and advances the entire system in fixed simulation time steps.

At the center is `ModelEngine`, which:

- loads a model definition from JSON or Python dict,
- resolves each `model_type` to a Python class,
- initializes all models,
- and calls `step_model()` for each active model during simulation.

---

## 2) Repository map

### Core runtime

- `model_engine.py` — engine lifecycle (load/build/step), model resolution, definition normalization.
- `base_models/base_model.py` — abstract base behavior for all models (`init_model`, `step_model`, `calc_model`).

### Mechanical base models (`base_models/`)

- `base_model.py`
- `capacitance.py`
- `time_varying_elastance.py`
- `resistor.py`
- `valve.py`
- `container.py`

These provide generic pressure/volume/flow primitives and shared lifecycle behavior.

### Composite models (`composite_models/`)

- `blood_vessel.py`
- `micro_vascular_unit.py`

These compose multiple lower-level elements into reusable higher-level structures.

### Derived models (`derived_models/`)

- `blood_capacitance.py`
- `blood_diffusor.py`
- `blood_time_varying_elastance.py`
- `gas_capacitance.py`
- `gas_diffusor.py`
- `gas_exchanger.py`
- `heart_chamber.py`
- `pump.py`

These specialize base mechanics with blood/gas composition behavior and domain-specific coupling.

### System models (`system_models/`)

- `ans.py`, `ans_afferent.py`, `ans_efferent.py`
- `blood.py`, `gas.py`
- `heart.py`, `circulation.py`, `respiration.py`, `breathing.py`
- `placenta.py`, `pda.py`, `shunts.py`, `ductus_arteriosus.py`, `dustus_arteriosus.py`
- `fluids.py`, `metabolism.py`, `mob.py`

These coordinate whole physiological subsystems and cross-component control loops.

### Device models (`device_models/`)

- `ventilator.py`, `mechanical_ventilator.py`
- `ecls.py`
- `monitor.py`
- `resuscitation.py`

These model clinical devices and intervention controllers around the physiology core.

### Helper and function modules

- `helpers/`
  - `data_collector.py`
  - `realtime_moving_average.py`
  - `task_scheduler.py`
- `functions/`
  - `blood_composition.py`
  - `gas_composition.py`

### Definitions, scenarios, and scripts

- `definitions/`
  - `baseline_neonate.json`
- `scenarios/`
  - `aop.ipynb`, `aph.ipynb`, `mas.ipynb`, `pda.ipynb`
- `scripts/`
  - `smoke_translations.py`
  - `soak_test_baseline_mongo.py`

### Documentation and notebooks

- `README.md`
- `docs/model_structure.md`
- `docs/explain_class_reference.md`
- `explain.ipynb`
- `explain_interactive_manual.ipynb`

---

## 3) Runtime architecture

## 3.1 Main objects

### `ModelEngine`

Responsible for:

1. Loading and validating the model definition.
2. Applying global settings (e.g. `modeling_stepsize`).
3. Extracting model configs from `models`, `components`, and `helpers` sections.
4. Resolving classes by `model_type` across model packages.
5. Instantiating and initializing model objects.
6. Executing simulation steps with `step_model()`.

### `BaseModel`

Defines common model contract:

- `init_model(args)` — assign supported config fields and initialize nested components.
- `step_model()` — run model update when enabled and initialized.
- `calc_model()` — abstract method each concrete class must implement.

Also includes component auto-initialization and model class resolution for nested components.

## 3.2 Lifecycle

```mermaid
flowchart TD
    A[Load JSON/Python definition] --> B[Apply general settings]
    B --> C[Merge model configs from models/components/helpers]
    C --> D[Resolve model_type to class]
    D --> E[Instantiate models]
    E --> F[init_model for each model]
    F --> G[Engine is_initialized = True]
    G --> H[Simulation loop: step_model()]
    H --> I[Each enabled model runs calc_model()]
```

## 3.3 Class resolution behavior

`ModelEngine` and `BaseModel` resolve `model_type` by searching these packages in order:

1. `base_models`
2. `composite_models`
3. `derived_models`
4. `system_models`
5. `device_models`

Legacy aliases are supported (for example `BloodPump` → `Pump`).

---

## 4) Model definition format

The engine supports definitions as either:

- a JSON file (`load_json_file(path)`), or
- an in-memory dictionary (`build(definition)`).

Typical top-level sections:

- `general`: global runtime settings.
- `models`: named model configurations.
- `components`: additional named model configurations.
- `helpers`: optional helper model configurations.

Example shape:

```json
{
  "general": {
    "modeling_stepsize": 0.0005
  },
  "components": {
    "C1": {
      "model_type": "capacitance",
      "is_enabled": true,
      "vol": 0.2,
      "u_vol": 0.1,
      "el_base": 5.0
    },
    "R1": {
      "model_type": "resistor",
      "is_enabled": true,
      "comp_from": "C1",
      "comp_to": "C1",
      "r_for": 100.0,
      "r_back": 100.0
    }
  }
}
```

Notes:

- Every model entry must define `model_type`.
- Model names are dictionary keys (or `name` if list format is used).
- Unknown config keys are tolerated at init level for compatibility.

---

## 5) Running the model

## 5.1 Environment setup

The recommended Python implementation for Explain is **PyPy3** (better runtime performance for this model in typical long simulations).

Install PyPy3 first:

### Windows

Option A (winget):

```powershell
winget install -e --id Python.PyPy.3.10
```

Option B (manual installer):

1. Download PyPy3 for Windows from the official PyPy downloads page.
2. Add PyPy to your `PATH`.
3. Verify:

```powershell
pypy3 --version
```

### macOS

Using Homebrew:

```bash
brew update
brew install pypy3
pypy3 --version
```

### Linux

Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y pypy3 pypy3-venv
pypy3 --version
```

Fedora:

```bash
sudo dnf install -y pypy3
pypy3 --version
```

After PyPy3 is available, create and activate the project environment:

### macOS / Linux

```bash
pypy3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
pypy3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Windows (Command Prompt / cmd)

```bat
pypy3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

## 5.2 Load and step from Python

```python
from model_engine import ModelEngine

engine = ModelEngine().load_json_file("definitions/baseline_neonate.json")
print(engine.is_initialized)
print(len(engine.models))

for _ in range(100):
    engine.step_model()
```

## 5.3 Build from dict directly

```python
from model_engine import ModelEngine

definition = {
    "general": {"modeling_stepsize": 0.01},
    "components": {
        "C1": {
            "model_type": "capacitance",
            "is_enabled": True,
            "vol": 0.2,
            "u_vol": 0.1,
            "el_base": 5.0,
        }
    },
}

engine = ModelEngine().build(definition)
engine.step_model()
```

---

## 6) Blood and gas composition utilities

## 6.1 Blood composition

`functions/blood_composition.py` computes blood chemistry and oxygenation fields from total content state.

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

## 6.2 Gas composition

`functions/gas_composition.py` computes gas partial pressures and fractions from gas state.

```python
from functions.gas_composition import calc_gas_composition

gc = {"name": "alveolar_gas", "pres": 760.0}
calc_gas_composition(gc, fio2=0.21, temp=37.0, humidity=1.0, fico2=0.0004)
print(gc["po2"], gc["pco2"], gc["pn2"], gc["fo2"], gc["fco2"], gc["fn2"])
```

---

## 7) Interactive notebooks and scenarios

### Main notebooks

- `explain.ipynb` — general interactive exploration.
- `explain_interactive_manual.ipynb` — guided control panel + chapter tabs for subsystems.

### Scenario notebooks

- `scenarios/aop.ipynb`
- `scenarios/aph.ipynb`
- `scenarios/mas.ipynb`
- `scenarios/pda.ipynb`

These are practical entry points for scenario-specific model behavior checks.

---

## 8) Validation scripts

### `scripts/smoke_translations.py`

Runs a suite of smoke checks across supported definitions and subsystem behaviors.

### `scripts/soak_test_baseline_mongo.py`

Performs long-run stepping and tracks numeric ranges to detect non-finite drift or instability in key signals.

---

## 9) Extending Explain

## 9.1 Add a new model class

1. Create a new class inheriting `BaseModel` (or a specialized base) in the appropriate package.
2. Set a `model_type` class attribute.
3. Implement `calc_model(self)`.
4. Add default fields in `__init__` for all expected config keys.
5. Reference the new model in a JSON definition.

The engine discovers classes by `model_type` and class name normalization.

## 9.2 Add a new definition

1. Create a JSON file in `definitions/`.
2. Add `general` settings and model entries with valid `model_type` values.
3. Load with:

```python
engine = ModelEngine().load_json_file("definitions/your_definition.json")
```

4. Run smoke/soak checks and inspect outputs in the interactive notebook.

---

## 10) Troubleshooting

### Model fails to load with unknown `model_type`

- Verify the class exists in one of the recognized model folders.
- Verify `model_type` matches class/model alias conventions.

### Model initializes but behavior looks static

- Confirm `is_enabled` is `True` for target models.
- Confirm the simulation loop is calling `engine.step_model()`.

### Numeric outputs become invalid (`nan`/`inf`)

- Run soak tests to isolate the component/signal.
- Inspect recent parameter changes and time-step size.

### Import/path issues when running scripts

- Run commands from repository root.
- If needed, set:

```bash
PYTHONPATH=/absolute/path/to/repo
```

---

## 11) Recommended reading order

1. `README.md`
2. `docs/model_structure.md`
3. `docs/explain_class_reference.md`
4. `model_engine.py`
5. `base_models/base_model.py`
6. `derived_models/*` and `system_models/*`
7. `explain_interactive_manual.ipynb`
8. `scripts/smoke_translations.py` and `scripts/soak_test_baseline_mongo.py`

---

## 12) Current project note

At the time of this document, the `definitions/` folder contains:

- `baseline_neonate.json`

If more definition files are added, the architecture and workflows above remain the same; update section **2) Repository map** and **7) Interactive notebooks and scenarios** accordingly.
