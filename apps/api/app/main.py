"""Loopback-only research prototype. No database, kiln control or predictions."""
from copy import deepcopy
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from research.chemistry.foundation import ChemistryInputError, SOURCE_METADATA, digest
from research.chemistry.recipe import analyze_recipe
from research.chemistry.recipe_demo import demo


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


class FiringContext(StrictModel):
    # Recorded intent only: none of these fields changes the oxide calculation.
    cone: Literal["UNKNOWN", "06", "04", "6", "8", "10"] = "UNKNOWN"
    temperature_c: Annotated[float | None, Field(strict=True, ge=0, le=1800)] = None
    atmosphere: Literal["UNKNOWN", "OXIDATION", "REDUCTION", "OTHER"] = "UNKNOWN"
    clay_body: Annotated[str, Field(max_length=160)] = ""


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


class AnalysisReport(StrictModel):
    schema_version: Literal["prototype-report/1"] = "prototype-report/1"
    report_id: str
    request: AnalysisRequest
    chemistry: ChemistryResult
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


@app.get("/api/v1/materials", response_model=Catalogue)
def materials():
    return Catalogue(materials=material_list(), notice=NOTICES[0], example=AnalysisRequest(
        recipe_name="İlk araştırma · teorik karışım", ingredients=deepcopy(_reference()["ingredients"]),
        context=FiringContext(cone="6", atmosphere="OXIDATION")))


@app.post("/api/v1/analyses", response_model=AnalysisReport, responses={422: {"model": ErrorResponse}})
def analyze(payload: AnalysisRequest):
    analyses = deepcopy(_reference()["analyses"])
    try:
        result = analyze_recipe([r.model_dump() for r in payload.ingredients], analyses,
                                base_mass_g=payload.base_mass_g)
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
    return AnalysisReport(report_id=digest({"request": payload.model_dump(), "chemistry_hash": result["input_hash"]}),
                          request=payload, chemistry=ChemistryResult(**result),
                          materials=[m for m in material_list() if m.analysis_id in selected], notices=NOTICES)
