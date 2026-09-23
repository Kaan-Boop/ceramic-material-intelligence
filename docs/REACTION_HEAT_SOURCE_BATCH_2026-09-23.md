# Reaction and heat source batch — 2026-09-23

## Delivered

Official documentation and licenses were reviewed before acquisition. The local pool is
`storage/reaction-heat-pool/2026-09-23/`. Its acquisition manifest records 23 files,
61,866,976 bytes, including a reused NumPy wheel. This is stored size, not a claim
that every byte was newly downloaded. Source URLs, commit identifiers, hashes,
retrieval times and license references are in
`data/manifests/reaction-heat-acquisition-2026-09-23.json`.

| Project | Acquired | Executed here | Intended role and boundary |
|---|---|---|---|
| Cantera | Full v3.2.0 source ZIP, license, pinned Windows wheel | Installed in an isolated environment; fixed gas benchmark | Chemical equilibrium and reaction kinetics; a valid mechanism is required for each application |
| FiPy | Full pinned source ZIP and license | No | Candidate for coupled heat/diffusion PDEs; not an already calibrated ceramic model |
| pycalphad | Full pinned development snapshot and license | No | Phase-equilibrium candidate; appropriate assessed thermodynamic databases remain necessary |
| Thermo | License, README and selected heat-capacity code | No | Property-method research; not the full repository or installed package |
| Chemicals | License, README and selected heat-capacity/reaction code | No | Thermochemistry/property-method research; not the full repository or installed package |

Cantera uses BSD-3-Clause; pycalphad, Thermo and Chemicals code use MIT.
FiPy has NIST government-work notices and its own permission/disclaimer text,
not an MIT license. Retain each original notice. Software licensing does not
automatically license every bundled mechanism, scientific database or cited
third-party dataset for republication/training. No third-party ceramic database
was imported into production by this batch. Acquisition receipt status records
the download stage; the execution status above records the subsequent benchmark.

## Working addition

`research/chemistry/reaction_probe.py` is a bounded optional-backend probe,
not a replacement for the chemistry core. It uses Cantera 3.2.0 and the bundled
H/O/Ar example mechanism, whose content hash is recorded in the output.

It calculates equilibrium under constant temperature/pressure (TP), equilibrium
under constant enthalpy/pressure (HP), and 11 samples of an adiabatic,
constant-pressure kinetic trajectory. These are different constraints;
equilibrium itself does not predict a reaction duration. This numerical example
is not a physical experiment instruction or kiln operating program.

Output: `data/manifests/cantera-probe-2026-09-23.json`.
Labels: PREDICTED / DETERMINISTIC / ILLUSTRATIVE_GAS_BENCHMARK.
Physical validation: NOT_PERFORMED.

### Verification actually run

- Six optional-backend tests passed: elemental conservation, enthalpy conservation,
  TP/HP distinction, changing kinetic state, repeatability and archive integrity.
- All acquired files matched recorded SHA-256; ZIP/wheel CRC checks passed.
- 208 existing tests passed in the simulation environment.
- Isolated reaction environment `pip check`: no broken requirements.
- Maximum absolute elemental mass-fraction deviation: 3.504e-13.
- Maximum relative adiabatic enthalpy deviation: 1.102e-9.
- Maximum mass-fraction sum deviation: 2.221e-16.

These are software and internal conservation checks, not independent experimental
validation of reaction rates or ceramic outcomes. API/browser tests were not
rerun in this batch; no UI feature was added.

## Reproduction (PowerShell, repository root)

```powershell
& .\storage\reaction-heat-pool\2026-09-23\environment\Scripts\python.exe -X utf8 -m research.chemistry.reaction_probe
& .\storage\reaction-heat-pool\2026-09-23\environment\Scripts\python.exe -X utf8 scripts/verify_reaction_dependency.py
& .\storage\reaction-heat-pool\2026-09-23\environment\Scripts\python.exe -m pip check
& .\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m unittest discover -s tests
```

`requirements-reaction-win-py312.lock` pins five installed distributions and wheel
hashes. Downloads and virtual environments stay outside Git. The acquisition
script refuses an existing destination/manifest to protect this snapshot.

## What remains unavailable

This gas example has no ceramic melt, mineral decomposition, glaze/body interface,
porous drying, kiln heat loss or calibrated defect-probability model. It cannot
predict adhesion, matte/gloss finish, final color or a success percentage.
Downloaded pycalphad source does not supply an assessed glaze-system database.

The next useful integration is a bounded drying model with conserved water mass
and energy, building on the existing water-property adapter. It needs independently
checked water-property references and experimentally supported material inputs.
Dehydroxylation/decarbonation require separate, traceable reaction and TGA evidence;
the hydrogen example must not be repurposed as clay kinetics. Existing TGA raw
records are not yet an accepted numerical validation series. Do not install and
wire all candidate solvers into the application before selecting a validated task.

## Primary references inspected

- Cantera: https://cantera.org/
- Cantera license: https://github.com/Cantera/cantera/blob/v3.2.0/License.txt
- Reactor example: https://www.cantera.org/3.2/examples/python/reactors/reactor1.html
- Example mechanism: https://www.cantera.org/3.2/examples/input/h2o2.html
- FiPy documentation: https://pages.nist.gov/fipy/en/stable/
- FiPy source: https://github.com/usnistgov/fipy
- pycalphad documentation: https://pycalphad.org/docs/latest/api/pycalphad.core.html
- pycalphad source: https://github.com/pycalphad/pycalphad
- Thermo source: https://github.com/CalebBell/thermo
- Chemicals source: https://github.com/CalebBell/chemicals
- Reaction properties: https://chemicals.readthedocs.io/chemicals.reaction.html
