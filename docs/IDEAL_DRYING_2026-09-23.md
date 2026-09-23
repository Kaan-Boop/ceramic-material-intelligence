# Ideal energy-limited water-removal benchmark

## Delivered and boundary

Framework-independent `research/thermal/drying.py` implements a deliberately
restricted lumped warm-up/boiling calculation. It is NOT a porous clay drying
model. The CoolProp 8.0.0 provider is optional; unit tests need no external solver.
No UI, database migration, new package installation or physical test is included.

The specimen is a uniform-temperature inert solid plus free water at a specified
constant absolute pressure. Solid heat capacity is constant. Net heat input is
nonnegative and constant: it is not kiln nameplate power. There is no evaporation
below the boiling point in this benchmark, although real clay does lose water
below that point. No transport coefficient, humidity, pore pressure, bound-water
release, shrinkage, reaction or cracking calculation is implied.

## Equations and bookkeeping

Let md be dry solid mass, mw initial free-water mass, cp solid heat capacity,
T0 initial temperature and Ts saturation temperature at the supplied pressure.
CoolProp supplies liquid enthalpy hl(T,p) and saturated vapor enthalpy hv(Ts,p).

```
Qwarm(T) = md cp (T-T0) + mw [hl(T,p)-hl(T0,p)]
L = hv(Ts,p)-hl(Ts,p)
Qin = Pnet t
Qcapacity = Qwarm(Ts) + mw L
```

Before boiling, invert Qwarm(T)=Qin by bisection. At boiling, emitted mass is
`min(mw, (Qin-Qwarm(Ts))/L)`. Temperature is held at Ts. After exhaustion the
model ends; additional heat is explicitly outside_model_energy_j, not a prediction
of the dry solid temperature. The sample grid does not control numerical time
integration because this particular constant-power problem is solved by energy.

The energy ledger is `Qin = sensible_energy + latent_energy + outside_model_energy`.
Here sensible energy is cumulative warm-up energy, NOT the enthalpy currently
stored in the remaining specimen. After evaporation, part of the warmed water's
enthalpy has left with vapor. The equivalent open-system balance uses remaining
liquid enthalpy plus emitted vapor enthalpy relative to the initial liquid reference.
Do not add a second vapor outflow enthalpy to this cumulative ledger.

## Sources reviewed before implementation

- CoolProp official high-level API describes saturation quality inputs and latent
  heat as saturated vapor minus liquid enthalpy:
  https://coolprop.org/coolprop/HighLevelAPI.html
- COMSOL official moisture/heat theory describes coupled evaporation mass and
  latent-heat terms:
  https://doc.comsol.com/6.3/doc/com.comsol.help.heat/heat_ug_theory.07.086.html

These are method references, not an independent validation of this specimen model.
No COMSOL software or model was downloaded, copied or required. This implementation
is a project-specific ideal conservation benchmark, not the full model described
in those documents. CoolProp's equation-of-state output is estimated; a broad
sanity range is not an independent reference-table validation.

## Reproduction and acceptance

```powershell
& .\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m unittest discover -s tests
& .\storage\engine-dependencies\2026-09-23\environment\Scripts\python.exe -X utf8 scripts/check_ideal_drying.py
```

Eight added unit tests use explicitly synthetic property constants and independently
derived analytic values. They cover warm-up, half evaporation, exhaustion, energy
and mass balance, zero power, invalid inputs, grid independence and scaling.
The complete existing-plus-new test suite passed: 216 tests in 6.488 seconds.
The optional CoolProp example produced 41 samples and a maximum absolute energy
residual of 4.191e-9 J. Its specimen is synthetic, not a named commercial clay.
Results are PREDICTED / DETERMINISTIC / IDEAL_ENERGY_LIMITED_BENCHMARK;
physical_validation=NOT_PERFORMED and uncertainty=null.

Output: `data/manifests/ideal-drying-probe-2026-09-23.json`.

## Next acceptance gate

Independently check property values against published water reference data. Obtain
a legally reusable, numerical drying/TGA time-temperature-mass series and identify
the free-water region before fitting any kinetics. A realistic sub-boiling drying
model additionally needs humidity, surface area, heat/mass transfer, and eventually
porous transport data. Existing raw TGA files are not yet accepted validation series.
Do not infer a real clay drying time, kiln program or defect probability from this
benchmark.
