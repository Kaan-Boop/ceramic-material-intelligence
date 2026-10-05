"""Loopback-only prototype with scoped indicators, no calibrated outcome probabilities.

No database or kiln control. Recipe chemistry and optional property-based models
remain distinct; models never infer missing material properties from names.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import os
import sys
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from research.chemistry.foundation import ChemistryInputError, SOURCE_METADATA, digest
from research.chemistry.recipe import analyze_recipe
from research.chemistry.recipe_demo import demo
from research.process.assessment import assess_process, ProcessInputError
from research.process.outcomes import assess_outcomes, OutcomeInputError
from research.process.validation import compare_temperature
from research.chemistry.reaction_explorer import explore
from research.material_library import build_library
from research.local_recipe_archive import search_recipes, get_staged_record
from research.simulation.capabilities import assess_capabilities
from research.simulation.chemistry import ScenarioChemistryError, analyze_layer, scenario_material_roles
from research.material_resolver import MaterialResolutionError, resolve_engine_analysis, resolve_material, resolve_materials
from research.external.openglaze_adapter import OpenGlazeReferenceError, run_umf_reference
from research.external.comparison import compare_calculated_reports
from research.simulation.scenario import (
    FiringSchedule as ScenarioFiringSchedule,
    FiringSegment as ScenarioFiringSegment,
    GeometrySpec as ScenarioGeometrySpec,
    LayerSpec as ScenarioLayerSpec,
    MaterialRef as ScenarioMaterialRef,
    SimulationScenario,
    SimulationTarget as ScenarioTarget,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


Amount = Annotated[float, Field(strict=True, ge=0, le=1_000_000)]


class Ingredient(StrictModel):
    analysis_id: Annotated[str, Field(min_length=1, max_length=100)]
    amount: Amount
    role: Literal["BASE", "ADDITION"] = "BASE"

    @field_validator("amount")
    @classmethod
    def practical_precision(cls, value):
        if 0 < value < 0.000001:
            raise ValueError("Non-zero prototype amounts must be at least 0.000001")
        return value


class ReportedWindow(StrictModel):
    product_id: Annotated[str, Field(min_length=1, max_length=160)]
    source_ref: Annotated[str, Field(min_length=1, max_length=500)]
    conditions: Annotated[str, Field(min_length=1, max_length=1000)]
    min_c: Annotated[float, Field(strict=True, ge=0, le=1800)]
    max_c: Annotated[float, Field(strict=True, ge=0, le=1800)]


class FiringSegment(StrictModel):
    target_c: Annotated[float, Field(strict=True, ge=0, le=1800)]
    rate_c_per_hour: Annotated[float | None, Field(strict=True, ge=0.01, le=10000)]
    hold_minutes: Annotated[float, Field(strict=True, ge=0, le=10080)] = 0


class FiringSchedule(StrictModel):
    start_c: Annotated[float, Field(strict=True, ge=0, le=1800)]
    segments: Annotated[list[FiringSegment], Field(min_length=1, max_length=100)]


class FiringContext(StrictModel):
    # Recorded intent only: none of these fields changes the oxide calculation.
    cone: Literal["UNKNOWN", "06", "04", "6", "8", "10"] = "UNKNOWN"
    temperature_c: Annotated[float | None, Field(strict=True, ge=0, le=1800)] = None
    atmosphere: Literal["UNKNOWN", "OXIDATION", "REDUCTION", "OTHER"] = "UNKNOWN"
    clay_body: Annotated[str, Field(max_length=160)] = ""
    body_window: ReportedWindow | None = None
    glaze_window: ReportedWindow | None = None
    schedule: FiringSchedule | None = None


class AnalysisRequest(StrictModel):
    recipe_name: Annotated[str, Field(min_length=1, max_length=120)]
    ingredients: Annotated[list[Ingredient], Field(min_length=1, max_length=100)]
    base_mass_g: Annotated[float, Field(strict=True, ge=0.000001, le=1_000_000)] = 100
    context: FiringContext = Field(default_factory=FiringContext)


class Availability(StrictModel):
    status: Literal["AVAILABLE", "UNAVAILABLE"]
    unavailable_reason: str | None


class Ratio(Availability):
    value: float | None


class UMF(Availability):
    values: dict[str, float] | None


class NormalizedIngredient(Ingredient):
    original_amount: float
    percent_of_base: float
    dry_mass_g: float


class Predictions(StrictModel):
    status: Literal["UNAVAILABLE"]
    reason: str


class ChemistryResult(StrictModel):
    schema_version: str
    engine_version: str
    evidence_kind: Literal["CALCULATED"]
    method_kind: Literal["DETERMINISTIC"]
    qualifier: str
    input_snapshot: dict[str, JsonValue]
    constant_set_id: str
    constant_set_sha256: str
    umf_convention: str
    input_hash: str
    normalized_ingredients: list[NormalizedIngredient]
    oxide_mass_g: dict[str, float]
    oxide_moles: dict[str, float]
    oxide_mol_pct: dict[str, float]
    retained_oxide_wt_pct: dict[str, float]
    loi_mass_g: float
    retained_oxide_mass_g: float
    total_dry_batch_mass_g: float
    umf: UMF
    flux_distribution: dict[str, float] | None
    ratios: dict[str, Ratio]
    warnings: list[str]
    predictions: Predictions


class Material(StrictModel):
    analysis_id: str
    name: str
    formula: str
    version: str
    qualifier: str
    basis: str
    loi_pct: float
    oxides: dict[str, float]
    source_ref: str
    source_url: str


class Catalogue(StrictModel):
    materials: list[Material]
    example: AnalysisRequest
    notice: str


class WindowCheck(StrictModel):
    status: Literal['AVAILABLE', 'UNAVAILABLE']
    code: str
    source_ref: str | None


class ScheduleCheck(StrictModel):
    status: Literal['AVAILABLE', 'PARTIAL', 'UNAVAILABLE']
    known_duration_minutes: float | None
    total_duration_minutes: float | None
    peak_c: float | None
    code: str


class ProcessStage(StrictModel):
    id: str
    title: str
    status: Literal['UNAVAILABLE']
    evidence_kind: Literal['PREDICTED']
    probability: None
    reason: str
    required_evidence: list[str]
    next_step: str


class ProcessReport(StrictModel):
    engine_version: str
    input_hash: str
    input_snapshot: dict[str, JsonValue]
    status: Literal['PARTIAL']
    checks_evidence_kind: Literal['CALCULATED']
    checks_method_kind: Literal['DETERMINISTIC']
    checks_qualifier: str
    body_window: WindowCheck
    glaze_window: WindowCheck
    schedule: ScheduleCheck
    stages: list[ProcessStage]
    warnings: list[str]
    limitations: list[str]


class AnalysisReport(StrictModel):
    schema_version: Literal["prototype-report/1"] = "prototype-report/1"
    report_id: str
    request: AnalysisRequest
    chemistry: ChemistryResult
    process: ProcessReport
    materials: list[Material]
    notices: list[str]
    persistence: Literal["NOT_STORED_EXPORT_TO_KEEP"] = "NOT_STORED_EXPORT_TO_KEEP"


class ErrorItem(StrictModel):
    code: str
    path: list[str]
    message: str
    severity: Literal["ERROR"] = "ERROR"


class ErrorResponse(StrictModel):
    errors: list[ErrorItem]


class OutcomeRequest(StrictModel):
    # Per-method domain contracts reject missing/unknown fields; no silent defaults.
    fit: dict[str, JsonValue] | None = None
    flow: dict[str, JsonValue] | None = None
    wetting: dict[str, JsonValue] | None = None
    porosity: dict[str, JsonValue] | None = None
    gloss: dict[str, JsonValue] | None = None


NAMES = {
    "ideal_k_feldspar": "İdeal potasyum feldspat",
    "pure_silica": "Saf silika",
    "ideal_kaolinite": "İdeal kaolinit",
    "pure_calcite": "Saf kalsit",
}
NOTICES = [
    "Bu katalog teorik formüllerden türetilmiştir; üretici veya lot analizi değildir.",
    "Yalnızca kuru kütleler kullanılır. Baz miktarları parçadır; ilaveler bazın yüzdesidir.",
    "LOI bir kütle bütçesidir; gaz türünü, salım sıcaklığını veya hızını belirlemez.",
    "Oksit hesabı faz, redoks, uçuculuk, sır yüzeyi veya gıda güvenliği tahmini değildir.",
    "Pişirim ve bünye alanları bağlam kaydıdır; mevcut kimya hesabını değiştirmez. Cone tek bir °C değildir.",
    "Sabit seti periodictable 2.1.0 sürümüne bağlıdır; güncel CIAAW tablosu olduğu iddia edilmez.",
]


@lru_cache(maxsize=1)
def _reference():
    return demo()["input_snapshot"]


def material_list():
    return [Material(analysis_id=key, name=NAMES[key], formula=a["formula"], version=a["version"],
                     qualifier=a["qualifier"], basis=a["basis"], loi_pct=a["loi_pct"],
                     oxides=a["oxides"], source_ref=a["source_ref"], source_url=SOURCE_METADATA["source_url"])
            for key, a in _reference()["analyses"].items()]


app = FastAPI(title="Ceramic Glaze Lab — Local Research Prototype", version="0.1.0")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])


@app.get("/api/v1/health", response_model=dict[str, str])
def health() -> dict[str, str]:
    """Deployment probe; does not load the research archive or run chemistry."""
    return {"status": "ok", "service": "ceramic-api", "version": app.version}


@app.middleware("http")
async def local_boundary(request: Request, call_next):
    # No public deployment/auth is offered by this prototype. Bound streamed body too.
    if request.method == "POST":
        origin = request.headers.get("origin")
        if origin and origin not in {"http://127.0.0.1:3000", "http://localhost:3000"}:
            return JSONResponse(status_code=403, content={"errors": [{"code": "ORIGIN_DENIED", "path": [], "message": "Yerel erişim gerekli.", "severity": "ERROR"}]})
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 65536:
                return JSONResponse(status_code=413, content={"errors": [{"code": "BODY_TOO_LARGE", "path": [], "message": "İstek 64 KiB sınırını aşıyor.", "severity": "ERROR"}]})
        request._body = bytes(body)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    # Do not echo input values/private recipes in errors.
    return JSONResponse(status_code=422, content=ErrorResponse(errors=[
        ErrorItem(code="INVALID_INPUT", path=[str(x) for x in e["loc"]],
                  message="Alan türünü, izin verilen değeri ve sayısal sınırları kontrol edin.")
        for e in exc.errors()
    ]).model_dump())


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "mode": "LOCAL_RESEARCH_PROTOTYPE"}


class SimulationMaterialRef(StrictModel):
    analysis_id: Annotated[str, Field(min_length=1, max_length=200)]
    role: Literal["BODY", "ENGOBE", "GLAZE", "ADDITION", "OVERGLAZE"]
    amount_g: Annotated[float | None, Field(strict=True, gt=0, le=1_000_000)] = None
    layer_id: Annotated[str | None, Field(min_length=1, max_length=120)] = None


class SimulationLayer(StrictModel):
    layer_id: Annotated[str, Field(min_length=1, max_length=120)]
    materials: Annotated[list[SimulationMaterialRef], Field(min_length=1, max_length=100)]
    application_method: Literal["NONE", "DIP", "BRUSH", "SPRAY", "POUR", "SCREEN", "OTHER"] = "NONE"
    coat_count: Annotated[int, Field(strict=True, ge=0, le=100)] = 0
    dry_thickness_um: Annotated[float | None, Field(strict=True, ge=0, le=1_000_000)] = None
    wet_thickness_um: Annotated[float | None, Field(strict=True, ge=0, le=1_000_000)] = None
    drying_minutes: Annotated[float | None, Field(strict=True, ge=0, le=1_000_000)] = None


class SimulationFiringSegment(StrictModel):
    target_c: Annotated[float, Field(strict=True, ge=0, le=1800)]
    rate_c_per_hour: Annotated[float | None, Field(strict=True, gt=0, le=10000)] = None
    hold_minutes: Annotated[float, Field(strict=True, ge=0, le=10080)] = 0


class SimulationFiringSchedule(StrictModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    start_c: Annotated[float, Field(strict=True, ge=0, le=1800)]
    segments: Annotated[list[SimulationFiringSegment], Field(min_length=1, max_length=100)]
    atmosphere: Annotated[str, Field(min_length=1, max_length=80)] = "UNKNOWN"


class SimulationGeometry(StrictModel):
    kind: Literal["TILE", "PLATE", "CYLINDER", "SPHERE", "CUSTOM"]
    thickness_mm: Annotated[float, Field(strict=True, gt=0, le=10_000)]
    length_mm: Annotated[float | None, Field(strict=True, ge=0, le=100_000)] = None
    width_mm: Annotated[float | None, Field(strict=True, ge=0, le=100_000)] = None
    diameter_mm: Annotated[float | None, Field(strict=True, ge=0, le=100_000)] = None


class SimulationTarget(StrictModel):
    objective: Annotated[str, Field(min_length=1, max_length=500)]
    requested_outputs: Annotated[list[str], Field(max_length=50)] = Field(default_factory=list)
    reference_temperature_c: Annotated[float | None, Field(strict=True, ge=0, le=1800)] = None


class SimulationScenarioRequest(StrictModel):
    scenario_id: Annotated[str, Field(min_length=1, max_length=160)]
    body: SimulationLayer
    layers: Annotated[list[SimulationLayer], Field(max_length=100)] = Field(default_factory=list)
    bisque: SimulationFiringSchedule | None = None
    final_firing: SimulationFiringSchedule
    geometry: SimulationGeometry
    target: SimulationTarget
    metadata: dict[str, str] = Field(default_factory=dict)


class ScenarioRecipeIngredient(StrictModel):
    analysis_id: Annotated[str, Field(min_length=1, max_length=200)]
    amount: Annotated[float, Field(strict=True, ge=0, le=1_000_000)]
    role: Literal["BASE", "ADDITION"]

    @field_validator("amount")
    @classmethod
    def recipe_amount_precision(cls, value):
        if 0 < value < 0.000001:
            raise ValueError("Non-zero recipe amounts must be at least 0.000001")
        return value


class ScenarioRecipeLayer(StrictModel):
    layer_id: Annotated[str, Field(min_length=1, max_length=120)]
    base_mass_g: Annotated[float, Field(strict=True, gt=0, le=1_000_000)] = 100
    ingredients: Annotated[list[ScenarioRecipeIngredient], Field(min_length=1, max_length=100)]


class SimulationChemistryRequest(StrictModel):
    scenario: SimulationScenarioRequest
    recipes: Annotated[list[ScenarioRecipeLayer], Field(min_length=1, max_length=100)]


def _scenario_layer(layer: SimulationLayer) -> ScenarioLayerSpec:
    return ScenarioLayerSpec(
        layer_id=layer.layer_id,
        materials=tuple(
            ScenarioMaterialRef(
                analysis_id=material.analysis_id,
                role=material.role,
                amount_g=material.amount_g,
                layer_id=material.layer_id,
            )
            for material in layer.materials
        ),
        application_method=layer.application_method,
        coat_count=layer.coat_count,
        dry_thickness_um=layer.dry_thickness_um,
        wet_thickness_um=layer.wet_thickness_um,
        drying_minutes=layer.drying_minutes,
    )


def _scenario_schedule(schedule: SimulationFiringSchedule) -> ScenarioFiringSchedule:
    return ScenarioFiringSchedule(
        name=schedule.name,
        start_c=schedule.start_c,
        segments=tuple(
            ScenarioFiringSegment(
                target_c=segment.target_c,
                rate_c_per_hour=segment.rate_c_per_hour,
                hold_minutes=segment.hold_minutes,
            )
            for segment in schedule.segments
        ),
        atmosphere=schedule.atmosphere,
    )


def _scenario_from_request(payload: SimulationScenarioRequest) -> SimulationScenario:
    return SimulationScenario(
        scenario_id=payload.scenario_id,
        body=_scenario_layer(payload.body),
        layers=tuple(_scenario_layer(layer) for layer in payload.layers),
        bisque=_scenario_schedule(payload.bisque) if payload.bisque else None,
        final_firing=_scenario_schedule(payload.final_firing),
        geometry=ScenarioGeometrySpec(
            kind=payload.geometry.kind,
            thickness_mm=payload.geometry.thickness_mm,
            length_mm=payload.geometry.length_mm,
            width_mm=payload.geometry.width_mm,
            diameter_mm=payload.geometry.diameter_mm,
        ),
        target=ScenarioTarget(
            objective=payload.target.objective,
            requested_outputs=tuple(payload.target.requested_outputs),
            reference_temperature_c=payload.target.reference_temperature_c,
        ),
        metadata=dict(payload.metadata),
    )


@app.post('/api/v1/simulations/capabilities', response_model=dict[str, JsonValue], responses={422: {'model': ErrorResponse}})
def simulation_capabilities(payload: SimulationScenarioRequest):
    """Validate a generic scenario and report supported outputs only.

    This endpoint is intentionally a capability gate. It does not run a kiln,
    infer material properties, or return surface/defect probabilities.
    """
    try:
        scenario = _scenario_from_request(payload)
        material_ids = tuple(ref.analysis_id for ref in scenario.body.materials)
        material_ids += tuple(ref.analysis_id for layer in scenario.layers for ref in layer.materials)
        records, inventory = resolve_materials(material_ids)
        report = assess_capabilities(scenario, inventory)
        report["material_resolutions"] = [
            {
                "analysis_id": record["id"],
                "version": record["version"],
                "status": record["status"],
                "engine_eligible": record["engine_eligible"],
                "source_name": record["source_name"],
                "source_url": record["source_url"],
            }
            for record in records
        ]
        report["property_inventory_source"] = "SERVER_RESOLVED_LOCAL_LIBRARY"
        return report
    except MaterialResolutionError as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code='UNKNOWN_MATERIAL_ANALYSIS',
            path=['scenario', 'materials'],
            message='Malzeme adı yerine katalogdaki exact analysis_id ve sürüm kullanılmalı.',
        )]).model_dump())
    except ValueError as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code='INVALID_SIMULATION_SCENARIO',
            path=['scenario'],
            message=str(exc),
        )]).model_dump())


@app.post('/api/v1/simulations/chemistry', response_model=dict[str, JsonValue], responses={422: {'model': ErrorResponse}})
def simulation_chemistry(payload: SimulationChemistryRequest):
    """Calculate deterministic dry-batch chemistry for declared scenario layers.

    This is intentionally not a firing or surface simulator. Every recipe row
    is resolved from the server's exact local analysis snapshot and research-
    only catalogue records are rejected instead of being treated as chemistry.
    """
    try:
        scenario = _scenario_from_request(payload.scenario)
        material_ids = tuple(ref.analysis_id for ref in scenario.body.materials)
        material_ids += tuple(ref.analysis_id for layer in scenario.layers for ref in layer.materials)
        records, _inventory = resolve_materials(material_ids)
        role_map = scenario_material_roles(scenario)
        layer_results = []
        for recipe in payload.recipes:
            result = analyze_layer(
                layer_id=recipe.layer_id,
                ingredients=[item.model_dump() for item in recipe.ingredients],
                base_mass_g=recipe.base_mass_g,
                scenario_materials=role_map,
            )
            layer_results.append(result)
        return {
            'schema_version': 'simulation-chemistry-v1',
            'evidence_kind': 'CALCULATED',
            'method_kind': 'DETERMINISTIC',
            'scenario_input_hash': scenario.input_hash(),
            'layer_results': layer_results,
            'material_resolutions': [
                {
                    'analysis_id': record['id'],
                    'version': record['version'],
                    'status': record['status'],
                    'engine_eligible': record['engine_eligible'],
                    'source_name': record['source_name'],
                    'source_url': record['source_url'],
                }
                for record in records
            ],
            'limitations': [
                'Katman raporları kuru baz oksit, mol ve UMF muhasebesidir.',
                'Pişirim, faz, erime, viskozite, yüzey ve kusur sonucu hesaplanmaz.',
                'Aynı senaryodaki bünye ve kaplama kimyaları ayrı raporlanır; arayüz reaksiyonu çıkarılmaz.',
            ],
        }
    except MaterialResolutionError as exc:
        code = 'MATERIAL_NOT_ENGINE_ELIGIBLE' if 'MATERIAL_NOT_ENGINE_ELIGIBLE' in str(exc) else 'UNKNOWN_MATERIAL_ANALYSIS'
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code=code,
            path=['recipes', 'ingredients'],
            message='Her kimya girdisi exact ve engine-eligible bir analiz sürümüne bağlanmalıdır.',
        )]).model_dump())
    except ScenarioChemistryError as exc:
        code = 'MATERIAL_NOT_ENGINE_ELIGIBLE' if 'MATERIAL_NOT_ENGINE_ELIGIBLE' in str(exc) else 'SCENARIO_CHEMISTRY_UNAVAILABLE'
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code=code,
            path=['recipes'],
            message=str(exc),
        )]).model_dump())
    except ChemistryInputError as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code='INVALID_CHEMISTRY_INPUT',
            path=['recipes'],
            message=str(exc),
        )]).model_dump())
    except ValueError as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code='INVALID_SIMULATION_SCENARIO',
            path=['scenario'],
            message=str(exc),
        )]).model_dump())


class ComparisonRequest(StrictModel):
    prediction: dict[str, JsonValue]
    observation: dict[str, JsonValue]


class ReactionExplorerRequest(StrictModel):
    mass_g: Annotated[float, Field(strict=True, ge=0.000001, le=1000000)]
    conversion: Annotated[float, Field(strict=True, ge=0, le=1)]


class ExternalReferenceIngredient(StrictModel):
    name: Annotated[str, Field(min_length=1, max_length=160)]
    amount: Annotated[float, Field(strict=True, gt=0, le=1000000)]


class OpenGlazeReferenceRequest(StrictModel):
    ingredients: Annotated[list[ExternalReferenceIngredient], Field(min_length=1, max_length=100)]
    cone: Annotated[int, Field(strict=True, ge=-20, le=20)]

    @field_validator('cone')
    @classmethod
    def nonzero_cone(cls, value: int) -> int:
        if value == 0:
            raise ValueError('Cone 0 geçerli bir referans değildir.')
        return value


class ChemistryComparisonRequest(StrictModel):
    ingredients: Annotated[list[Ingredient], Field(min_length=1, max_length=100)]
    base_mass_g: Annotated[float, Field(strict=True, gt=0, le=1_000_000)] = 100
    cone: Annotated[int, Field(strict=True, ge=-20, le=20)]
    external_names: dict[str, Annotated[str, Field(min_length=1, max_length=160)]] = Field(default_factory=dict)

    @field_validator('cone')
    @classmethod
    def nonzero_cone(cls, value: int) -> int:
        if value == 0:
            raise ValueError('Cone 0 geçerli bir referans değildir.')
        return value


@app.post('/api/v1/reactions/calcite', response_model=dict[str, JsonValue])
def calcite_explorer(payload: ReactionExplorerRequest):
    return explore(payload.mass_g, payload.conversion)


@app.post('/api/v1/references/openglaze/umf', response_model=dict[str, JsonValue])
def openglaze_umf_reference(payload: OpenGlazeReferenceRequest):
    """Run the optional OpenGlaze CLI as an explicitly external reference.

    The route is disabled unless ``OPENGLAZE_REPO_ROOT`` points to a locally
    downloaded, license-reviewed checkout. Its result never replaces the
    deterministic Ceramic Material Intelligence chemistry report.
    """
    configured_root = os.environ.get('OPENGLAZE_REPO_ROOT', '').strip()
    bundled_root = Path(__file__).resolve().parents[3] / 'storage' / 'external' / 'openglaze' / 'source' / 'openglaze-master'
    repo_root = configured_root or (str(bundled_root) if bundled_root.is_dir() else '')
    if not repo_root:
        return JSONResponse(status_code=503, content={
            'status': 'UNAVAILABLE',
            'code': 'EXTERNAL_REFERENCE_NOT_CONFIGURED',
            'message': 'OpenGlaze referans kaynağı bu çalışma ortamında etkin değil.',
            'evidence_kind': 'CALCULATED',
            'method_kind': 'DETERMINISTIC_EXTERNAL_REFERENCE',
        })
    try:
        return run_umf_reference(
            [item.model_dump() for item in payload.ingredients],
            cone=payload.cone,
            repo_root=repo_root,
            python_executable=os.environ.get('OPENGLAZE_PYTHON', sys.executable),
        )
    except OpenGlazeReferenceError:
        return JSONResponse(status_code=503, content={
            'status': 'UNAVAILABLE',
            'code': 'EXTERNAL_REFERENCE_EXECUTION_FAILED',
            'message': 'OpenGlaze referans hesabı çalıştırılamadı; çekirdek rapor kullanılmaya devam eder.',
            'evidence_kind': 'CALCULATED',
            'method_kind': 'DETERMINISTIC_EXTERNAL_REFERENCE',
        })


@app.post('/api/v1/references/openglaze/compare', response_model=dict[str, JsonValue])
def compare_with_openglaze(payload: ChemistryComparisonRequest):
    """Compare our exact local chemistry snapshot with OpenGlaze.

    This endpoint is a reproducibility aid, not a consensus engine. It only
    compares UMF-equivalent fields and preserves the external report and
    material-name limitations separately.
    """
    if any(row.role == 'ADDITION' for row in payload.ingredients):
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code='EXTERNAL_REFERENCE_ADDITIONS_UNSUPPORTED',
            path=['ingredients'],
            message='OpenGlaze karşılaştırması şu anda yalnızca BASE parçalarını destekler; ADDITION satırları ayrı semantics gerektirir.',
        )]).model_dump())
    try:
        records, _inventory = resolve_materials(tuple(row.analysis_id for row in payload.ingredients))
        analyses = {row.analysis_id: resolve_engine_analysis(row.analysis_id) for row in payload.ingredients}
        internal = analyze_recipe([row.model_dump() for row in payload.ingredients], analyses, base_mass_g=payload.base_mass_g)
        by_id = {record['id']: record for record in records}
        external_ingredients = [
            {
                'name': payload.external_names.get(row.analysis_id, by_id[row.analysis_id]['name']),
                'amount': row.amount,
            }
            for row in payload.ingredients
        ]
        configured_root = os.environ.get('OPENGLAZE_REPO_ROOT', '').strip()
        bundled_root = Path(__file__).resolve().parents[3] / 'storage' / 'external' / 'openglaze' / 'source' / 'openglaze-master'
        repo_root = configured_root or (str(bundled_root) if bundled_root.is_dir() else '')
        if not repo_root:
            return {
                'schema_version': 'comparison-run-v1',
                'status': 'PARTIAL',
                'evidence_kind': 'CALCULATED',
                'method_kind': 'DETERMINISTIC',
                'internal': internal,
                'external': {'status': 'UNAVAILABLE', 'reason': 'EXTERNAL_REFERENCE_NOT_CONFIGURED'},
                'differences': {},
                'warnings': ['Harici OpenGlaze kaynağı etkin değil; yalnızca kendi motorumuzun raporu üretildi.'],
                'limitations': ['Bu bir motor karşılaştırmasıdır; deneysel doğrulama değildir.'],
            }
        external = run_umf_reference(
            external_ingredients,
            cone=payload.cone,
            repo_root=repo_root,
            python_executable=os.environ.get('OPENGLAZE_PYTHON', sys.executable),
        )
        return compare_calculated_reports(
            internal,
            external,
            external_ingredients=external_ingredients,
            cone=payload.cone,
        )
    except (MaterialResolutionError, ChemistryInputError, OpenGlazeReferenceError) as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code='REFERENCE_COMPARISON_UNAVAILABLE',
            path=['ingredients'],
            message=str(exc),
        )]).model_dump())
@app.post('/api/v1/validation/temperature', response_model=dict[str, JsonValue])
def temperature_comparison(payload: ComparisonRequest):
    try:
        return compare_temperature(payload.prediction, payload.observation)
    except OutcomeInputError as exc:
        return JSONResponse(status_code=422, content={'errors': [{
            'code': str(exc), 'message': 'Bağlamı, kaynakları ve eşleşen zaman/sıcaklık değerlerini kontrol edin.',
            'path': ['comparison'], 'severity': 'ERROR'}]})


@app.post('/api/v1/outcomes/assess', response_model=dict[str, JsonValue], responses={422: {'model': ErrorResponse}})
def outcome_indicators(payload: OutcomeRequest):
    try:
        return assess_outcomes(payload.model_dump(exclude_none=True))
    except OutcomeInputError as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code=str(exc).split(':')[0], path=['outcomes'],
            message='Ölçüm birimlerini, kaynak alanlarını ve modelin geçerlilik koşullarını kontrol edin.'
        )]).model_dump())


@app.get("/api/v1/materials", response_model=Catalogue)
def materials():
    return Catalogue(materials=material_list(), notice=NOTICES[0], example=AnalysisRequest(
        recipe_name="İlk araştırma · teorik karışım", ingredients=deepcopy(_reference()["ingredients"]),
        context=FiringContext(cone="6", atmosphere="OXIDATION")))


@app.get('/api/v1/library', response_model=dict[str, JsonValue])
def library():
    return {'version':'local-library/1','scope':'LOCAL_RESEARCH_NOT_PUBLIC_RELEASE',
            'records':build_library([m.model_dump() if hasattr(m,'model_dump') else m for m in material_list()])}


@app.get('/api/v1/material-analyses/{analysis_id:path}', response_model=dict[str, JsonValue])
def material_analysis(analysis_id: str):
    """Return one exact local analysis record with provenance and eligibility."""
    try:
        record = resolve_material(analysis_id)
    except MaterialResolutionError:
        return JSONResponse(status_code=404, content={'error': 'MATERIAL_ANALYSIS_NOT_FOUND'})
    return {
        'analysis_id': record['id'],
        'name': record['name'],
        'version': record['version'],
        'status': record['status'],
        'engine_eligible': record['engine_eligible'],
        'basis': record['basis'],
        'formula': record['formula'],
        'oxides': record['oxides'],
        'loi_pct': record['loi'],
        'source_name': record['source_name'],
        'source_url': record['source_url'],
        'license': record['license'],
        'flags': record['flags'],
        'windows': record['windows'],
        'uses': record['uses'],
        'note': record['note'],
    }


@app.get('/api/v1/research/archive/recipes', response_model=dict[str, JsonValue])
def research_archive_recipes(q: str = Query('', max_length=200), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), category: str = Query('', pattern='^(|RECIPE|GLAZE|CLAY_BODY|ANALYSIS)$')):
    return search_recipes(q, page, page_size, category)


@app.get('/api/v1/research/archive/recipes/{source_id}', response_model=dict[str, JsonValue])
def research_archive_recipe(source_id: int):
    record = get_staged_record(source_id)
    if record is None:
        return JSONResponse(status_code=404, content={'error': 'RESEARCH_RECORD_NOT_FOUND'})
    return record


@app.post("/api/v1/analyses", response_model=AnalysisReport, responses={422: {"model": ErrorResponse}})
def analyze(payload: AnalysisRequest):
    analyses = deepcopy(_reference()["analyses"])
    try:
        process = assess_process(payload.context.model_dump())
        result = analyze_recipe([r.model_dump() for r in payload.ingredients], analyses,
                                base_mass_g=payload.base_mass_g)
    except ProcessInputError as exc:
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code=str(exc).split(':')[0], path=['context'],
            message='Pişirim aralığını, kaynak bilgilerini ve program hız/yönünü kontrol edin.'
        )]).model_dump())
    except ChemistryInputError as exc:
        code = str(exc)
        translations = {
            "ZERO_BASE_TOTAL": "Baz reçetenin toplamı sıfır olamaz. En az bir pozitif baz miktarı girin.",
            "UNKNOWN_ANALYSIS": "Malzeme analizi bulunamadı. Katalogdan bir analiz seçin.",
        }
        return JSONResponse(status_code=422, content=ErrorResponse(errors=[ErrorItem(
            code=code, path=["ingredients"], message=translations.get(code, "Bilimsel girdi doğrulaması başarısız; analiz bazını ve miktarları kontrol edin.")
        )]).model_dump())
    selected = {r.analysis_id for r in payload.ingredients}
    return AnalysisReport(report_id=digest({"request": payload.model_dump(), "chemistry_hash": result["input_hash"], "process_hash": process['input_hash']}),
                          request=payload, chemistry=ChemistryResult(**result), process=process,
                          materials=[m for m in material_list() if m.analysis_id in selected], notices=NOTICES)
