# Explain Model — Detailed Class Reference

This document catalogs all classes currently present in the Explain repository, grouped by subsystem.

Total classes documented: **42**

## Quick Index (Class → Subsystem → File)

| Class | Subsystem | File |
| --- | --- | --- |
| [ModelEngine](#modelengine) | Core Runtime | `model_engine.py` |
| [BaseModel](#basemodel) | Base Models | `base_models/base_model.py` |
| [Capacitance](#capacitance) | Base Models | `base_models/capacitance.py` |
| [Container](#container) | Base Models | `base_models/container.py` |
| [Resistor](#resistor) | Base Models | `base_models/resistor.py` |
| [TimeVaryingElastance](#timevaryingelastance) | Base Models | `base_models/time_varying_elastance.py` |
| [Valve](#valve) | Base Models | `base_models/valve.py` |
| [BloodVessel](#bloodvessel) | Composite Models | `composite_models/blood_vessel.py` |
| [MicroVascularUnit](#microvascularunit) | Composite Models | `composite_models/micro_vascular_unit.py` |
| [BloodCapacitance](#bloodcapacitance) | Derived Models | `derived_models/blood_capacitance.py` |
| [BloodDiffusor](#blooddiffusor) | Derived Models | `derived_models/blood_diffusor.py` |
| [BloodTimeVaryingElastance](#bloodtimevaryingelastance) | Derived Models | `derived_models/blood_time_varying_elastance.py` |
| [GasCapacitance](#gascapacitance) | Derived Models | `derived_models/gas_capacitance.py` |
| [GasDiffusor](#gasdiffusor) | Derived Models | `derived_models/gas_diffusor.py` |
| [GasExchanger](#gasexchanger) | Derived Models | `derived_models/gas_exchanger.py` |
| [HeartChamber](#heartchamber) | Derived Models | `derived_models/heart_chamber.py` |
| [Pump](#pump) | Derived Models | `derived_models/pump.py` |
| [Ans](#ans) | System Models | `system_models/ans.py` |
| [AnsAfferent](#ansafferent) | System Models | `system_models/ans_afferent.py` |
| [AnsEfferent](#ansefferent) | System Models | `system_models/ans_efferent.py` |
| [Blood](#blood) | System Models | `system_models/blood.py` |
| [Breathing](#breathing) | System Models | `system_models/breathing.py` |
| [Circulation](#circulation) | System Models | `system_models/circulation.py` |
| [DuctusArteriosus](#ductusarteriosus) | System Models | `system_models/ductus_arteriosus.py` |
| [DustusArteriosus](#dustusarteriosus) | System Models | `system_models/dustus_arteriosus.py` |
| [Fluids](#fluids) | System Models | `system_models/fluids.py` |
| [Gas](#gas) | System Models | `system_models/gas.py` |
| [Heart](#heart) | System Models | `system_models/heart.py` |
| [Metabolism](#metabolism) | System Models | `system_models/metabolism.py` |
| [Mob](#mob) | System Models | `system_models/mob.py` |
| [Pda](#pda) | System Models | `system_models/pda.py` |
| [Placenta](#placenta) | System Models | `system_models/placenta.py` |
| [Respiration](#respiration) | System Models | `system_models/respiration.py` |
| [Shunts](#shunts) | System Models | `system_models/shunts.py` |
| [Ecls](#ecls) | Device Models | `device_models/ecls.py` |
| [MechanicalVentilator](#mechanicalventilator) | Device Models | `device_models/mechanical_ventilator.py` |
| [Ventilator](#ventilator) | Device Models | `device_models/mechanical_ventilator.py` |
| [Monitor](#monitor) | Device Models | `device_models/monitor.py` |
| [Resuscitation](#resuscitation) | Device Models | `device_models/resuscitation.py` |
| [DataCollector](#datacollector) | Helpers | `helpers/data_collector.py` |
| [RealTimeMovingAverage](#realtimemovingaverage) | Helpers | `helpers/realtime_moving_average.py` |
| [TaskScheduler](#taskscheduler) | Helpers | `helpers/task_scheduler.py` |

## Core Runtime

### ModelEngine

- **File:** `model_engine.py`
- **Inherits:** `object`
- **Purpose:**

  Runtime engine that builds and steps model graphs from JSON definitions.

- **Methods:**

  - `__init__(self, modeling_stepsize=0.0005)` — Initialize an empty engine.
  - `load_json_file(self, file_path)` — Load a JSON model definition file and build the engine.
  - `build(self, model_definition)` — Build model instances from an in-memory definition mapping.
  - `step_model(self)` — Advance all initialized models by one simulation step.
  - `_apply_general_settings(self, model_definition)` — Apply global settings from the definition onto the engine instance.
  - `_extract_model_configs(self, model_definition)` — Collect and merge model configs from supported definition sections.
  - `_normalize_model_section(self, section_data, section_name)` — Normalize one model section into a name -> config dictionary.
  - `_resolve_model_class(self, model_type)` — Resolve a `model_type` string to a `BaseModel` subclass.

## Base Models

### BaseModel

- **File:** `base_models/base_model.py`
- **Inherits:** `ABC`
- **model_type:** `base`
- **Purpose:**

  Abstract base class for all model components.

- **Methods:**

  - `__init__(self, model_ref=None, name=None)` — Initialize shared model state.
  - `init_model(self, args=None)` — Initialize model properties from configuration and nested components.
  - `_normalize_init_args(self, args)` — Normalize initialization input into a plain dictionary.
  - `_init_components(self)` — Instantiate and initialize nested models declared in `components`.
  - `_get_model_registry(self)` — Return the active model registry dictionary if available.
  - `_resolve_model_class(self, model_type)` — Resolve a component `model_type` to a concrete `BaseModel` subclass.
  - `step_model(self)` — Execute one model step if enabled and initialized.
  - `calc_model(self)` — Compute one simulation step for the concrete model implementation.

### Capacitance

- **File:** `base_models/capacitance.py`
- **Inherits:** `BaseModel`
- **model_type:** `capacitance`
- **Purpose:**

  Generic capacitance compartment with elastance-based pressure dynamics.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize a capacitance component and its tunable parameters.
  - `calc_model(self)` — Run one capacitance update step (elastance, volume, pressure).
  - `calc_elastance(self)` — Update effective elastance terms using persistent/non-persistent factors.
  - `calc_volume(self)` — Update effective unstressed volume from configured factors.
  - `calc_pressure(self)` — Compute recoil, transmural, and total pressure for the compartment.
  - `volume_in(self, dvol, comp_from=None)` — Add incoming volume when composition is not fixed.
  - `volume_out(self, dvol)` — Remove outgoing volume when composition is not fixed.

### Container

- **File:** `base_models/container.py`
- **Inherits:** `BaseModel`
- **model_type:** `container`
- **Purpose:**

  Container model that applies pressure coupling to enclosed components.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize a container with elastance and enclosed component settings.
  - `calc_model(self)` — Run one container update step (elastance, volume aggregation, pressure).
  - `calc_elastance(self)` — Update effective container elastance terms from factor settings.
  - `calc_volume(self)` — Compute container volume from `vol_extra` plus enclosed model volumes.
  - `calc_pressure(self)` — Compute pressure and propagate external pressure to enclosed components.

### Resistor

- **File:** `base_models/resistor.py`
- **Inherits:** `BaseModel`
- **model_type:** `resistor`
- **Purpose:**

  Flow element that computes pressure-driven flow between two components.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize resistor parameters, state, and connected endpoints.
  - `calc_model(self)` — Run one resistor update step (resolve components, resistance, flow).
  - `calc_resistance(self)` — Update effective forward/backward resistance values from factors.
  - `calc_flow(self)` — Compute directional flow and transfer volume between connected models.

### TimeVaryingElastance

- **File:** `base_models/time_varying_elastance.py`
- **Inherits:** `BaseModel`
- **model_type:** `time_varying_elastance`
- **Purpose:**

  Capacitance-like chamber with activation-dependent elastance.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize chamber parameters and time-varying elastance state.
  - `calc_model(self)` — Run one chamber update step (elastance, volume, pressure).
  - `calc_elastance(self)` — Update minimum/maximum elastance and non-linear term from factors.
  - `calc_volume(self)` — Update effective unstressed volume using current scaling factors.
  - `calc_pressure(self)` — Compute pressure from diastolic/systolic blend using activation factor.
  - `volume_in(self, dvol, comp_from=None)` — Add incoming volume when composition is not fixed.
  - `volume_out(self, dvol)` — Remove outgoing volume when composition is not fixed.

### Valve

- **File:** `base_models/valve.py`
- **Inherits:** `BaseModel`
- **model_type:** `valve`
- **Purpose:**

  Valve flow element with optional no-backflow behavior.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize valve parameters, state, and connected endpoints.
  - `calc_model(self)` — Run one valve update step (resolve components, resistance, flow).
  - `calc_resistance(self)` — Update effective valve resistance terms from configured factors.
  - `calc_flow(self)` — Compute directional valve flow and transfer volume between models.

## Composite Models

### BloodVessel

- **File:** `composite_models/blood_vessel.py`
- **Inherits:** `BloodCapacitance`
- **model_type:** `blood_vessel`
- **Purpose:**

  Composite blood vessel model with embedded input resistors.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize vessel state, resistance parameters, and connector config.
  - `init_model(self, args=None)` — Initialize vessel and create input connector resistors from `inputs`.
  - `calc_model(self)` — Run one vessel step and propagate parameters to connector resistors.
  - `get_flows(self)` — Aggregate net, forward, and backward flow from all input resistors.
  - `calc_inertances(self)` — Update effective inertance using transient and persistent factors.
  - `calc_resistances(self)` — Update effective forward/backward resistance including ANS modulation.
  - `calc_elastances(self)` — Update effective elastance terms from factor and ANS contributions.

### MicroVascularUnit

- **File:** `composite_models/micro_vascular_unit.py`
- **Inherits:** `BaseModel`
- **model_type:** `micro_vascular_unit`
- **Purpose:**

  Three-segment microvascular bed (arterial, capillary, venous).

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize distribution settings and state for a microvascular unit.
  - `init_model(self, args=None)` — Initialize unit and create/configure ART, CAP, and VEN sub-vessels.
  - `_get_or_create_vessel(self, model_registry, model_ref_for_vessel, vessel_name)` — Return an existing `BloodVessel` by name or create and register one.
  - `calc_model(self)` — Run one unit step and synchronize state with underlying vessel segments.
  - `calc_resistance(self)` — Update global resistance terms and distribute them across segments.
  - `calc_elastance(self)` — Update global elastance and distribute linear/nonlinear terms.
  - `calc_elastance_dist(self, el_base, el_dist)` — Convert target total elastance into segment-specific elastances.
  - `calc_inertance(self)` — Update effective inertance from transient and persistent factors.
  - `calc_volume(self)` — Update effective unstressed volume and distribute it across segments.

## Derived Models

### BloodCapacitance

- **File:** `derived_models/blood_capacitance.py`
- **Inherits:** `Capacitance`
- **model_type:** `blood_capacitance`
- **Purpose:**

  Capacitance compartment extended with blood composition state.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize blood-specific properties on top of generic capacitance.
  - `volume_in(self, dvol, comp_from=None)` — Add volume and mix blood composition from the source compartment.

### BloodDiffusor

- **File:** `derived_models/blood_diffusor.py`
- **Inherits:** `BaseModel`
- **model_type:** `blood_diffusor`
- **Purpose:**

  Diffusive exchange model between two blood-containing compartments.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize blood diffusion settings and component references.
  - `_resolve_component(self, component_name)` — Resolve a component name from local registry or attached model engine.
  - `calc_model(self)` — Run one diffusion step for gases and configured blood solutes.

### BloodTimeVaryingElastance

- **File:** `derived_models/blood_time_varying_elastance.py`
- **Inherits:** `TimeVaryingElastance`
- **model_type:** `blood_time_varying_elastance`
- **Purpose:**

  Time-varying elastance chamber with blood composition mixing behavior.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize chamber mechanics plus blood-related state variables.
  - `volume_in(self, dvol, comp_from=None)` — Add volume and mix blood composition from incoming compartment.

### GasCapacitance

- **File:** `derived_models/gas_capacitance.py`
- **Inherits:** `Capacitance`
- **model_type:** `gas_capacitance`
- **Purpose:**

  Gas compartment with pressure, temperature, and gas-fraction dynamics.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize gas capacitance thermodynamic and composition properties.
  - `calc_model(self)` — Run one gas compartment step (heat, vapor, pressure, composition).
  - `calc_pressure(self)` — Compute pressure including atmospheric and external contributors.
  - `volume_in(self, dvol, comp_from=None)` — Add incoming volume and mix gas composition from source compartment.
  - `add_heat(self)` — Move temperature toward target and adjust volume accordingly.
  - `add_watervapour(self)` — Add/remove water vapor toward temperature-dependent equilibrium.
  - `calc_watervapour_pressure(self)` — Return saturated water vapor pressure (mmHg) for current temperature.
  - `calc_gas_composition(self)` — Recompute partial pressures and fractions from gas concentrations.

### GasDiffusor

- **File:** `derived_models/gas_diffusor.py`
- **Inherits:** `BaseModel`
- **model_type:** `gas_diffusor`
- **Purpose:**

  Diffusive exchange model between two gas-containing compartments.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize gas diffusion settings and component references.
  - `_resolve_component(self, component_name)` — Resolve a component name from local registry or attached model engine.
  - `calc_model(self)` — Run one diffusion step for configured gas species.

### GasExchanger

- **File:** `derived_models/gas_exchanger.py`
- **Inherits:** `BaseModel`
- **model_type:** `gas_exchanger`
- **Purpose:**

  Bidirectional gas exchange model between blood and gas compartments.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize exchanger connectivity, diffusion constants, and flux state.
  - `calc_model(self)` — Run one exchange step and update blood/gas concentrations.

### HeartChamber

- **File:** `derived_models/heart_chamber.py`
- **Inherits:** `TimeVaryingElastance`
- **model_type:** `heart_chamber`
- **Purpose:**

  Heart chamber model with ANS-modulated elastance and blood mixing.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize chamber mechanics and blood-related state.
  - `calc_elastance(self)` — Compute ANS-adjusted elastance bounds and current chamber elastance.
  - `volume_in(self, dvol, comp_from=None)` — Add incoming volume and mix chemistry from source compartment.

### Pump

- **File:** `derived_models/pump.py`
- **Inherits:** `BloodCapacitance`
- **model_type:** `pump`
- **Purpose:**

  Active blood pump model that applies pressure to inlet or outlet side.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize pump connectivity, operating mode, and pressure state.
  - `_resolve_component(self, component_name)` — Resolve a connected component by name from registry or engine.
  - `calc_pressure(self)` — Compute compartment pressure and apply pump-generated pressure offsets.

## System Models

### Ans

- **File:** `system_models/ans.py`
- **Inherits:** `BaseModel`
- **model_type:** `ans`
- **Purpose:**

  Autonomic nervous system coordinator for component enablement and blood-gas refresh.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize ANS state and update cadence settings.
  - `init_model(self, args=None)` — Initialize model and preserve linked component configuration.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Apply ANS enable/disable state and update blood composition targets.

### AnsAfferent

- **File:** `system_models/ans_afferent.py`
- **Inherits:** `BaseModel`
- **model_type:** `ans_afferent`
- **Purpose:**

  Afferent ANS sensor that converts input signals into firing rate.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize afferent sensor configuration and firing-rate state.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Compute afferent firing rate and push updates to configured effectors.

### AnsEfferent

- **File:** `system_models/ans_efferent.py`
- **Inherits:** `BaseModel`
- **model_type:** `ans_efferent`
- **Purpose:**

  ANS efferent pathway mapping firing-rate input to target effectors.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize efferent target mapping and response dynamics.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Update effector value and write it to target model property.
  - `update_effector(self, new_firing_rate, weight)` — Accumulate weighted firing-rate contribution from afferent pathways.

### Blood

- **File:** `system_models/blood.py`
- **Inherits:** `BaseModel`
- **model_type:** `blood`
- **Purpose:**

  Global blood composition manager and blood-gas snapshot provider.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize global blood settings and monitored blood-gas outputs.
  - `_get_models_registry(self)` — Return active model registry dictionary if available.
  - `_resolve_model(self, model_name)` — Resolve a model name from the active registry.
  - `init_model(self, args=None)` — Initialize blood-capable models with baseline blood properties.
  - `calc_model(self)` — Periodically compute and publish arterial/venous blood-gas snapshots.
  - `set_temperature(self, new_temp, bc_site='')` — Set blood temperature globally or for a specific blood compartment.
  - `set_viscosity(self, new_viscosity)` — Set blood viscosity for all blood-containing models.
  - `set_to2(self, new_to2, bc_site='')` — Set total oxygen content globally or for one blood compartment.
  - `set_tco2(self, new_tco2, bc_site='')` — Set total carbon dioxide content globally or for one compartment.
  - `set_solute(self, solute, solute_value, bc_site='')` — Set a solute concentration globally or for one blood compartment.

### Breathing

- **File:** `system_models/breathing.py`
- **Inherits:** `BaseModel`
- **model_type:** `breathing`
- **Purpose:**

  Spontaneous breathing controller producing respiratory muscle pressure.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize breathing control parameters and cycle state.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Run one respiratory control/update step and drive thorax elastance.
  - `vt_rr_controller(self, weight)` — Compute respiratory rate and target tidal volume from minute-volume goal.
  - `calc_resp_muscle_pressure(self)` — Calculate inspiratory/expiratory respiratory muscle pressure waveform.
  - `switch_breathing(self, state)` — Enable or disable spontaneous breathing.

### Circulation

- **File:** `system_models/circulation.py`
- **Inherits:** `BaseModel`
- **model_type:** `circulation`
- **Purpose:**

  High-level circulation controller for vascular factors and blood volumes.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize circulation model groups and update cadence state.
  - `init_model(self, args=None)` — Initialize grouped vessel lists for systemic and pulmonary updates.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Apply ANS/SVR/PVR updates and periodically recompute blood volumes.
  - `set_svr_factor(self, new_svr_factor)` — Set systemic vascular resistance factor across systemic vessel groups.
  - `set_pvr_factor(self, new_pvr_factor)` — Set pulmonary vascular resistance factor across pulmonary groups.
  - `calc_blood_volumes(self)` — Compute systemic/pulmonary/cardiac blood volume totals and percentages.

### DuctusArteriosus

- **File:** `system_models/ductus_arteriosus.py`
- **Inherits:** `BaseModel`
- **model_type:** `pda`
- **Purpose:**

  Ductus arteriosus geometry/hemodynamics model with adjustable resistance.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize duct dimensions, resistance parameters, and flow outputs.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Update duct resistance/velocity metrics and connected resistor settings.
  - `set_diameter(self, new_diameter)` — Set both aortic and pulmonary duct diameters to the same value.
  - `calc_closure(self)` — No method docstring available.
  - `calc_resistance(self, diameter, length=20.0, viscosity=6.0)` — Return Poiseuille-based resistance estimate for a vessel segment.

### DustusArteriosus

- **File:** `system_models/dustus_arteriosus.py`
- **Inherits:** `DuctusArteriosus`
- **model_type:** `dustus_arteriosus`
- **Purpose:**

  Backward-compatible alias for the ductus arteriosus system model.

- **Methods:**

  - _No methods declared in class body._

### Fluids

- **File:** `system_models/fluids.py`
- **Inherits:** `BaseModel`
- **model_type:** `fluids`
- **Purpose:**

  Fluid administration manager for scheduled infusions into compartments.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize fluid presets, infusion queue, and update cadence.
  - `init_model(self, args=None)` — Initialize fluid model configuration.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Advance infusion scheduler and apply queued fluid deliveries.
  - `add_volume(self, volume, in_time=10.0, fluid_in='normal_saline', site='VLB')` — Queue an infusion with volume/time/composition and target site.
  - `process_fluid_list(self)` — Process active infusions and deliver per-step volume increments.

### Gas

- **File:** `system_models/gas.py`
- **Inherits:** `BaseModel`
- **model_type:** `gas`
- **Purpose:**

  Global gas environment manager for gas-capacitance compartments.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize atmospheric settings and per-site overrides.
  - `init_model(self, args=None)` — Initialize gas compartments with pressure, temperature, and humidity.
  - `calc_model(self)` — No per-step dynamics; gas model acts as a global configuration holder.
  - `_get_models_registry(self)` — Return active model registry dictionary if available.
  - `set_atmospheric_pressure(self, new_pres_atm)` — Set atmospheric pressure for all gas-capacitance models.
  - `set_temperature(self, new_temp, sites=None)` — Set target temperature for selected gas sites.
  - `set_humidity(self, new_humidity, sites=None)` — Set humidity for selected gas sites.
  - `set_fio2(self, new_fio2, sites=None)` — Set inspired oxygen fraction and recompute composition at selected sites.

### Heart

- **File:** `system_models/heart.py`
- **Inherits:** `BaseModel`
- **model_type:** `heart`
- **Purpose:**

  Cardiac cycle controller coordinating chamber activation and timing.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize heart timing, modulation factors, and cycle state.
  - `_resolve_model(self, component_name)` — Resolve a connected model by name from registry or engine.
  - `analyze(self)` — Update derived chamber pressure/volume metrics over cycle transitions.
  - `calc_model(self)` — Run one cardiac timing step and drive chamber activation factors.
  - `calc_varying_elastance(self)` — Compute atrial/ventricular activation waveforms and apply to chambers.
  - `calc_qtc(self, hr)` — Return corrected QT duration using Bazett-style scaling.
  - `set_pericardium(self, new_el_factor, new_volume)` — Adjust persistent pericardial elastance factor.
  - `set_contractillity(self, new_cont_factor_left, new_cont_factor_right)` — Adjust persistent chamber contractility factors (left/right).
  - `set_relaxation(self, new_relax_factor_left, new_relax_factor_right)` — Adjust persistent chamber relaxation factors (left/right).
  - `gaussian(self, t, amp, center, width)` — Return Gaussian pulse value for ECG waveform synthesis.

### Metabolism

- **File:** `system_models/metabolism.py`
- **Inherits:** `BaseModel`
- **model_type:** `metabolism`
- **Purpose:**

  Whole-body metabolism model consuming O2 and producing CO2 per compartment.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize metabolism settings and active compartment distribution.
  - `set_metabolic_active_model(self, site, fvo2=None, new_fvo2=None)` — Set fractional oxygen consumption contribution for one site.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Run one metabolic step and update to2/tco2 in active compartments.

### Mob

- **File:** `system_models/mob.py`
- **Inherits:** `BaseModel`
- **model_type:** `mob`
- **Purpose:**

  Myocardial oxygen balance model with hypoxia-driven cardiac adjustments.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize myocardial oxygen-balance parameters and state variables.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `_resolve_first(self, *names)` — Resolve and return the first existing model from a list of names.
  - `calc_model(self)` — Run one myocardial oxygen-balance update and apply hypoxia effects.
  - `calc_bm(self)` — Return basal myocardial O2 consumption in mmol/s equivalent.
  - `calc_ecc(self)` — Estimate excitation-contraction coupling oxygen consumption.
  - `calc_pe(self)` — Estimate potential-energy oxygen consumption component.
  - `calc_pva(self)` — Estimate pressure-volume area oxygen consumption component.
  - `calc_hypoxia_effects(self)` — Apply hypoxia-derived factor changes to heart/chamber properties.
  - `activation_function(self, value, max_value, setpoint, min_value)` — Map a measured value to signed activation around a setpoint.

### Pda

- **File:** `system_models/pda.py`
- **Inherits:** `DuctusArteriosus`
- **model_type:** `pda`
- **Purpose:**

  Alias wrapper for the ductus arteriosus system model.

- **Methods:**

  - _No methods declared in class body._

### Placenta

- **File:** `system_models/placenta.py`
- **Inherits:** `BaseModel`
- **model_type:** `placenta`
- **Purpose:**

  Placental circulation/gas-exchange controller for fetal-maternal interface.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize placenta geometry, diffusion settings, and runtime state.
  - `_models(self)` — Return active model registry dictionary.
  - `_model(self, name)` — Resolve a model from the active registry by name.
  - `init_model(self, args=None)` — Initialize placenta structures and apply enabled/disabled state.
  - `calc_model(self)` — Run one placenta update step (flows, resistances, and composition links).
  - `switch_placenta(self, state)` — Enable or disable placenta-related components in the model graph.
  - `build_placenta(self)` — Initialize placenta circuit defaults for first-time model setup.
  - `clamp_umbilical_cord(self, state)` — Set umbilical cord clamping state.
  - `set_umbilical_arteries_resistance(self, new_res)` — Set umbilical arterial resistance.
  - `set_umbilical_vein_resistance(self, new_res)` — Set umbilical venous resistance.
  - `set_fetal_placenta_resistance(self, new_res)` — Set fetal-placental exchange resistance.
  - `set_dif_o2(self, new_dif_o2)` — Set O2 diffusion coefficient for placental exchanger.
  - `set_dif_co2(self, new_dif_co2)` — Set CO2 diffusion coefficient for placental exchanger.
  - `set_mat_to2(self, new_to2)` — Set maternal total oxygen content input to placenta.
  - `set_mat_tco2(self, new_tco2)` — Set maternal total carbon dioxide content input to placenta.

### Respiration

- **File:** `system_models/respiration.py`
- **Inherits:** `BaseModel`
- **model_type:** `respiration`
- **Purpose:**

  Respiratory system coordinator for airway resistance and elastance factors.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize respiratory model groups and control factors.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Apply pending respiratory factor changes at configured update interval.
  - `set_el_lung_factor(self, new_factor)` — Set lung elastance scaling factor across configured lung compartments.
  - `set_el_thorax_factor(self, new_factor)` — Set thorax elastance scaling factor across configured thorax models.
  - `set_upper_airway_resistance(self, new_factor)` — Set resistance factor for upper airway resistive elements.
  - `set_lower_airway_resistance(self, new_factor)` — Set resistance factor for lower airway resistive elements.
  - `set_gasexchange(self, new_factor)` — Set gas-exchange diffusion factor for configured exchanger models.

### Shunts

- **File:** `system_models/shunts.py`
- **Inherits:** `BaseModel`
- **model_type:** `shunts`
- **Purpose:**

  Septal shunt model (FO/VSD) with diameter-based resistance updates.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize shunt geometry, viscosity, and hemodynamic outputs.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `calc_model(self)` — Update shunt resistances/velocities from current diameters and flows.
  - `calc_resistance(self, diameter, length=2.0, viscosity=6.0)` — Return Poiseuille-based resistance estimate for shunt pathway.

## Device Models

### Ecls

- **File:** `device_models/ecls.py`
- **Inherits:** `BaseModel`
- **model_type:** `ecls`
- **Purpose:**

  Extracorporeal life support (ECLS/ECMO) circuit controller.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize ECLS configuration, runtime metrics, and component references.
  - `_resolve_model(self, model_name)` — Resolve a circuit component by name from registry or engine.
  - `init_model(self, args=None)` — Resolve circuit components and apply initial ECLS configuration.
  - `calc_model(self)` — Run one ECLS control/update step for flow, pressures, and gas settings.
  - `switch_ecls(self, state)` — Enable or disable ECLS blood and gas sub-circuits.
  - `set_ecls_mode(self, new_mode)` — Set ECLS operating mode and update circuit topology switches.
  - `set_clamp(self, state)` — No method docstring available.
  - `set_pump_rpm(self, new_rpm)` — No method docstring available.
  - `set_gas_flow(self, new_gas_flow)` — No method docstring available.
  - `set_fio2(self, new_fio2)` — No method docstring available.
  - `set_co2_flow(self, new_co2_flow)` — No method docstring available.
  - `set_tubing_diameter(self, new_diameter)` — No method docstring available.
  - `set_tubing_in_length(self, new_length)` — No method docstring available.
  - `set_tubing_out_length(self, new_length)` — No method docstring available.
  - `set_oxygenator_volume(self, new_volume)` — No method docstring available.
  - `set_pump_occlusive(self, state)` — No method docstring available.
  - `set_drainage_origin(self, new_target)` — No method docstring available.
  - `set_return_target(self, new_target)` — No method docstring available.
  - `set_pump_volume(self, new_volume)` — No method docstring available.
  - `switch_blood_components(self, state=True)` — No method docstring available.
  - `calc_bloodgas(self)` — No method docstring available.
  - `calc_resistances(self)` — No method docstring available.
  - `set_drainage_cannula_diameter(self, new_diameter)` — No method docstring available.
  - `set_return_cannula_diameter(self, new_diameter)` — No method docstring available.
  - `set_drainage_cannula_length(self, new_length)` — No method docstring available.
  - `set_return_cannula_length(self, new_length)` — No method docstring available.
  - `calc_tubing_volumes(self)` — No method docstring available.
  - `switch_gas_components(self, state=True)` — No method docstring available.
  - `set_gas_exchanger(self)` — No method docstring available.
  - `set_gas_volumes(self)` — No method docstring available.
  - `set_gas_compositions(self)` — Recompute gas compositions for ECLS gas compartments.
  - `_calc_tube_volume(self, diameter, length)` — Return tube volume in mL for diameter (m) and length (m).
  - `_calc_tube_resistance(self, diameter, length, viscosity=6.0)` — Return Poiseuille-based tube resistance estimate.

### MechanicalVentilator

- **File:** `device_models/mechanical_ventilator.py`
- **Inherits:** `BaseModel`
- **model_type:** `mechanical_ventilator`
- **Purpose:**

  Mechanical ventilator controller supporting PC, PRVC, and PS modes.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize ventilator settings, measured outputs, and runtime state.
  - `_resolve_model(self, model_name)` — Resolve a model by name from local registry or attached engine.
  - `init_model(self, args=None)` — Initialize linked ventilator components and baseline gas composition.
  - `calc_model(self)` — Run one ventilator control/update step for current operating mode.
  - `triggering(self)` — Evaluate patient-trigger logic for synchronized ventilation.
  - `flow_cycling(self)` — Apply flow-cycled inspiration/expiration transitions (PS mode).
  - `time_cycling(self)` — Apply time-cycled inspiration/expiration transitions (PC/PRVC).
  - `pressure_control(self)` — Update inspiratory/expiratory valve states for pressure-targeted support.
  - `pressure_regulated_volume_control(self)` — Adjust pressure target to track desired tidal volume in PRVC mode.
  - `reset_dependent_properties(self)` — Reset measured/output properties when ventilator is turned off.
  - `switch_ventilator(self, state)` — Enable or disable ventilator circuit components.
  - `calc_ettube_resistance(self, flow)` — Compute and apply ET tube resistance from calibrated flow relation.
  - `set_ettube_length(self, new_length)` — No method docstring available.
  - `set_ettube_diameter(self, new_diameter)` — No method docstring available.
  - `set_fio2(self, new_fio2)` — No method docstring available.
  - `set_humidity(self, new_humidity)` — No method docstring available.
  - `set_temp(self, new_temp)` — No method docstring available.
  - `set_pc(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0)` — No method docstring available.
  - `set_prvc(self, pip_max=18.0, peep=4.0, rate=40.0, tv=15.0, t_in=0.4, insp_flow=10.0)` — No method docstring available.
  - `set_psv(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0)` — No method docstring available.
  - `trigger_breath(self, pip=14.0, peep=4.0, rate=40.0, t_in=0.4, insp_flow=10.0)` — No method docstring available.

### Ventilator

- **File:** `device_models/mechanical_ventilator.py`
- **Inherits:** `MechanicalVentilator`
- **model_type:** `ventilator`
- **Purpose:**

  Backward-compatible alias for the mechanical ventilator model.

- **Methods:**

  - _No methods declared in class body._

### Monitor

- **File:** `device_models/monitor.py`
- **Inherits:** `BaseModel`
- **model_type:** `monitor`
- **Purpose:**

  Patient monitor aggregator computing bedside-style vital signals.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize monitor channel mappings, outputs, and rolling state.
  - `_resolve_model(self, model_name)` — Resolve a connected model by name (supports single-item list values).
  - `_safe_float(self, obj, attr_name, default=0.0)` — Safely read a numeric attribute as float with fallback default.
  - `init_model(self, args=None)` — Initialize monitor configuration and resolve component references.
  - `calc_avg_heartrate(self, hr)` — Update rolling average heart rate using adaptive beat window.
  - `calc_model(self)` — Collect pressures/flows/signals and update derived monitor channels.
  - `collect_signals(self)` — Collect raw waveform-like monitor channels from connected models.
  - `collect_pressures(self)` — Track running min/max pressure and volume envelopes for cycle metrics.
  - `collect_blood_flows(self)` — Accumulate per-step flow integrals for derived flow/cardiac output metrics.

### Resuscitation

- **File:** `device_models/resuscitation.py`
- **Inherits:** `BaseModel`
- **model_type:** `resuscitation`
- **Purpose:**

  CPR and ventilation choreography model for resuscitation scenarios.

- **Methods:**

  - `__init__(self, model_ref={}, name=None)` — Initialize CPR/ventilation settings and runtime sequencing state.
  - `_resolve_model(self, *candidate_names)` — Resolve first matching model name from candidates.
  - `init_model(self, args=None)` — Initialize linked ventilator/breathing references and FiO2 setting.
  - `calc_model(self)` — Run one CPR/ventilation sequencing step and apply chest compression forces.
  - `switch_cpr(self, state)` — Enable/disable CPR mode and configure ventilator/breathing accordingly.
  - `set_fio2(self, new_fio2)` — Set ventilation oxygen fraction used during resuscitation.

## Helpers

### DataCollector

- **File:** `helpers/data_collector.py`
- **Inherits:** `object`
- **Purpose:**

  Collects time-series snapshots from selected model properties.

- **Methods:**

  - `__init__(self, model)` — Initialize collector state, default watch items, and sample intervals.
  - `clear_data(self)` — Clear fast-sampled buffered data.
  - `clear_data_slow(self)` — Clear slow-sampled buffered data.
  - `clear_watchlist(self)` — Reset fast watchlist to core cardiac cycle counters.
  - `clear_watchlist_slow(self)` — Reset slow watchlist to an empty set.
  - `get_model_data(self)` — Return and clear buffered fast-sampled data.
  - `get_model_data_slow(self)` — Return and clear buffered slow-sampled data.
  - `set_sample_interval(self, new_interval=0.005)` — Set fast sampling interval in seconds.
  - `set_sample_interval_slow(self, new_interval=0.005)` — Set slow sampling interval in seconds.
  - `add_to_watchlist(self, properties)` — Add one or more property paths to the fast watchlist.
  - `add_to_watchlist_slow(self, properties)` — Add one or more property paths to the slow watchlist.
  - `clean_up(self)` — Remove disabled or unresolved entries from the fast watchlist.
  - `clean_up_slow(self)` — Remove disabled or unresolved entries from the slow watchlist.
  - `collect_data(self, model_clock)` — Sample watched properties at configured intervals and buffer records.
  - `_find_model_prop(self, prop)` — Resolve a dotted property path into a watchlist descriptor.

### RealTimeMovingAverage

- **File:** `helpers/realtime_moving_average.py`
- **Inherits:** `object`
- **Purpose:**

  Fixed-window real-time moving average accumulator.

- **Methods:**

  - `__init__(self, window_size)` — Initialize moving-average buffer with a minimum window of 1.
  - `add_value(self, new_value)` — Add a sample and return the updated moving average.
  - `get_current_average(self)` — Return the current moving average value.
  - `reset(self)` — Clear buffered values and reset accumulator state.
  - `addValue(self, newValue)` — Compatibility alias for `add_value`.
  - `getCurrentAverage(self)` — Compatibility alias for `get_current_average`.

### TaskScheduler

- **File:** `helpers/task_scheduler.py`
- **Inherits:** `object`
- **Purpose:**

  Lightweight in-model scheduler for delayed ramps, sets, and function calls.

- **Methods:**

  - `__init__(self, model_ref)` — Initialize scheduler state and bind to model engine.
  - `_new_task_id(self)` — Generate a unique random task identifier.
  - `add_function_call(self, new_function_call)` — Schedule a delayed function invocation on a model object.
  - `add_task(self, new_task)` — Schedule a delayed/gradual property update task.
  - `remove_task(self, task_id)` — Remove one task by numeric suffix identifier.
  - `remove_all_tasks(self)` — Clear all scheduled tasks.
  - `run_tasks(self)` — Advance scheduler and execute due tasks at scheduler interval.
  - `_set_value(self, task)` — Apply task value to direct property or nested mapping/attribute.
