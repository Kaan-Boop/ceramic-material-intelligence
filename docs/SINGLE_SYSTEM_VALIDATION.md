# Single-system validation pilot

## Scope decision — 2026-09-27

First observable: specimen temperature history, not gloss, adhesion probability or failure risk. This is a validation harness; no new thermal solver or calibrated material law is delivered here.

Physical body/glaze pair: NOT_SELECTED. Existing scheelite data concern bodies without a matched glaze. NBS 710 is a reference glass, not the missing body/glaze system. Neither is relabelled as a complete pilot.

## Required chain

Immutable body + glaze analyses/revisions → application thickness/preparation → firing run → sensor location/calibration + specimen temperatures → separately generated model predictions at identical timestamps → residual report.

`research.process.validation.compare_temperature` reports bias (prediction minus observation), MAE, RMSE and maximum absolute error in degrees C. It requires exact context/time/unit matching and rejects programmed-kiln temperatures as specimen observations. No interpolation or implicit conversion occurs. Metrics weight points equally, not elapsed time. Unknown uncertainty remains null.

Repeated time samples count as one specimen, not many independent experiments. Identity checks validate supplied identifiers, not the truth of their source records. Real and synthetic records cannot be paired. Synthetic checks are not physical validation. Acceptance remains NOT_ASSESSED; thresholds require a documented instrument uncertainty and use-case decision.

## Focused model roles

1. Chemistry: composition and reproducible recipe snapshot; not outcome prediction.
2. Thermal: first model to compare with actual specimen data; property curves and boundary conditions must be measured or defensibly sourced.
3. Viscosity/flow: conditional follow-on only after a property model covers the selected glaze. Ideal film travel cannot be compared directly with glaze edge displacement.
4. Expansion: compare compatible dilatometry curves; free contraction mismatch is not crack probability.
5. Wetting: keep as optional ideal indicator; not bond strength.
6. Porosity/gloss: measured outcomes and reductions of measurements, not predictive models yet.

## Next acceptance gates

- Find one legally usable matched body/glaze study or collect a user experiment with chemistry, preparation, schedule and actual specimen-temperature measurements.
- Fix study identity, replicate/firing grouping, calibration subset and independent evaluation subset before fitting.
- Verify sensor placement and instrument uncertainty; define an acceptable error in C before evaluating.
- Run the existing thermal solver only with supported properties/conditions, then feed its output through this comparator.
- Add a second observable only when corresponding measurements and a suitable model exist.

No frontend/API integration, production approval or real paired validation is claimed in this delivery. Existing endpoints and scientific formulas are unchanged.

## Candidate screening — 2026-09-28

See `THERMAL_PILOT_CANDIDATES_2026-09-28.md` and
`data/manifests/thermal-pilot-candidates-2026-09-28.json` for three research
candidates and their evidence gaps. No candidate has passed admission;
the physical body/glaze pair remains NOT_SELECTED. Publisher-text screening
is not full-text review or raw experimental-data acquisition.
