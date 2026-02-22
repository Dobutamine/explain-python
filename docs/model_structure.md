# Model Structure

## Overview
This project is organized around an object-oriented model hierarchy.

- `BaseModel` defines the shared lifecycle (`init_model`, `step_model`, `calc_model`).
- Component models implement physiology/physics behavior in `component_models`.
- Composition helper functions live in `functions` and are called by components that need blood/gas chemistry updates.

## Core Base Class
- Base class: [base_models/base_model.py](base_models/base_model.py)
- Required behavior:
  - `calc_model(self)` must be implemented by subclasses.
  - `step_model(self)` calls `calc_model(self)` when `is_enabled` is `True`.
  - `init_model(self, args)` safely maps dictionary config into existing instance attributes.

## Component Models
Folder: [component_models](component_models)

### Primary mechanical models
- [component_models/capacitance.py](component_models/capacitance.py): nonlinear pressure-volume capacitance
- [component_models/time_varying_elastance.py](component_models/time_varying_elastance.py): activation-driven elastance chamber
- [component_models/resistor.py](component_models/resistor.py): pressure-driven flow resistance between components
- [component_models/valve.py](component_models/valve.py): directional flow resistance/valve behavior
- [component_models/container.py](component_models/container.py): aggregates contained component volumes and applies external pressure

### Blood-specialized models
- [component_models/blood_capacitance.py](component_models/blood_capacitance.py): `Capacitance` + blood composition state (solutes, gases, drugs)
- [component_models/blood_time_varying_elastance.py](component_models/blood_time_varying_elastance.py): `TimeVaryingElastance` + blood composition state
- [component_models/blood_diffusor.py](component_models/blood_diffusor.py): diffusion between two blood components (O2, CO2, solutes)
- [component_models/pump.py](component_models/pump.py): blood pump extending blood capacitance with pump pressure coupling

### Gas-specialized models
- [component_models/gas_capacitance.py](component_models/gas_capacitance.py): `Capacitance` + gas composition/temperature/humidity handling
- [component_models/gas_diffusor.py](component_models/gas_diffusor.py): diffusion between two gas components
- [component_models/gas_exchanger.py](component_models/gas_exchanger.py): gas-blood exchange between one blood and one gas component

## Composition Functions
Folder: [functions](functions)

- [functions/blood_composition.py](functions/blood_composition.py): computes blood acid-base and oxygenation state from total contents
- [functions/gas_composition.py](functions/gas_composition.py): computes gas partial pressures/fractions from gas state

## Inheritance Map
- `BaseModel`
  - `Capacitance`
    - `BloodCapacitance`
      - `Pump`
    - `GasCapacitance`
  - `TimeVaryingElastance`
    - `BloodTimeVaryingElastance`
  - `Resistor`
  - `Valve`
  - `Container`
  - `BloodDiffusor`
  - `GasDiffusor`
  - `GasExchanger`

```mermaid
classDiagram
    BaseModel <|-- Capacitance
    BaseModel <|-- TimeVaryingElastance
    BaseModel <|-- Resistor
    BaseModel <|-- Valve
    BaseModel <|-- Container
    BaseModel <|-- BloodDiffusor
    BaseModel <|-- GasDiffusor
    BaseModel <|-- GasExchanger

    Capacitance <|-- BloodCapacitance
    BloodCapacitance <|-- Pump
    Capacitance <|-- GasCapacitance

    TimeVaryingElastance <|-- BloodTimeVaryingElastance
```

## Runtime Interaction Pattern
1. Components are instantiated with `model_ref` and `name`.
2. Properties are populated via `init_model(args)` from model definitions.
3. Simulation loop calls `step_model()` per enabled model.
4. `calc_model()` performs each component’s physics/physiology update.
5. Specialized components call composition helpers when needed:
   - Blood models can call `calc_blood_composition(...)`.
   - Gas models can call `calc_gas_composition(...)`.

## Notes
- `model_ref` is currently used as a component lookup map for cross-component references.
- Diffusors and exchangers rely on `_t` (time-step) being set by the model engine.
- Volume transfer APIs support passing source component context where composition mixing is required.
