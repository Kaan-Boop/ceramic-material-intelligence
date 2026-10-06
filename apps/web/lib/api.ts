import type { components } from "./api-schema";

export type Catalogue = components["schemas"]["Catalogue"];
export type Report = components["schemas"]["AnalysisReport"];
export type AnalysisRequest = components["schemas"]["AnalysisRequest"];
export type Material = components["schemas"]["Material"];

export type CapabilityOutput = {
  status: "AVAILABLE" | "PARTIAL" | "UNAVAILABLE";
  evidence_kind: "CALCULATED" | "PREDICTED";
  method_kind: "DETERMINISTIC" | "UNAVAILABLE";
  reason: string;
};

export type SimulationCapabilityReport = {
  schema_version: "simulation-capabilities-v1";
  scenario_id: string;
  input_hash: string;
  material_ids: string[];
  outputs: Record<string, CapabilityOutput>;
  limitations: string[];
  material_resolutions?: Array<{
    analysis_id: string;
    version: string;
    status: string;
    engine_eligible: boolean;
    source_name: string;
    source_url: string;
  }>;
  property_inventory_source?: string;
};

export type SimulationChemistryReport = {
  schema_version: "simulation-chemistry-v1";
  evidence_kind: "CALCULATED";
  method_kind: "DETERMINISTIC";
  scenario_input_hash: string;
  layer_results: Array<{
    layer_id: string;
    layer_scope: string;
    retained_oxide_wt_pct: Record<string, number>;
    oxide_mass_g: Record<string, number>;
    oxide_mol_pct: Record<string, number>;
    umf: { status: "AVAILABLE" | "UNAVAILABLE"; values: Record<string, number> | null; unavailable_reason?: string | null };
    ratios: Record<string, { status: "AVAILABLE" | "UNAVAILABLE"; value: number | null; unavailable_reason?: string | null }>;
    warnings: string[];
    limitations: string[];
  }>;
  material_resolutions: SimulationCapabilityReport["material_resolutions"];
  limitations: string[];
};

export type OpenGlazeReferenceReport = {
  evidence_kind: "CALCULATED";
  method_kind: "DETERMINISTIC_EXTERNAL_REFERENCE";
  source: "OpenGlaze";
  report: {
    success: boolean;
    umf_formula?: Record<string, number>;
    ratios?: Record<string, number>;
    thermal_expansion?: number;
    surface_prediction?: string;
    surface_confidence?: string;
    limit_warnings?: string[];
    missing_materials?: string[];
    warnings?: string[];
    recommendations?: string[];
  };
  limitations: string[];
};

export type OpenGlazeComparisonReport = {
  schema_version: "comparison-run-v1";
  status: "COMPARED" | "PARTIAL";
  evidence_kind: "CALCULATED";
  method_kind: "DETERMINISTIC";
  input_hash: string;
  internal: {
    engine_version: string;
    input_hash: string;
    umf_convention: string;
    umf: { status: "AVAILABLE" | "UNAVAILABLE"; values: Record<string, number> | null };
    ratios: Record<string, { status: "AVAILABLE" | "UNAVAILABLE"; value: number | null }>;
  };
  external: OpenGlazeReferenceReport;
  differences: {
    umf: Record<string, { status: string; internal: number | null; external: number | null; delta: number | null; delta_pct: number | null }>;
    SiO2_to_Al2O3_molar: { status: string; internal: number | null; external: number | null; delta: number | null; delta_pct: number | null };
    thermal_expansion: { status: string; reason: string };
  };
  warnings: string[];
  limitations: string[];
};

export type ComparisonReplayReport = {
  status: "PASS" | "FAIL" | "UNAVAILABLE";
  input_hash_matches?: boolean;
  differences_match?: boolean;
  recomputed_input_hash?: string;
  reason?: string;
  limitations?: string[];
};

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, {
    ...init,
    cache: "no-store",
    signal: init?.signal ?? AbortSignal.timeout(15000),
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const details = body?.errors
      ?.map(
        (e: { message: string; path: string[] }) =>
          `${e.message}${e.path?.length ? ` (${e.path.join(" / ")})` : ""}`,
      )
      .join(" ");
    throw new Error(
      details ||
        "API'ye ulaşılamadı. Yerel Python sunucusunun açık olduğunu kontrol edin.",
    );
  }
  return body as T;
}

export const numberTR = (n: number | null | undefined, digits = 3) =>
  n == null
    ? "—"
    : new Intl.NumberFormat("tr-TR", { maximumFractionDigits: digits }).format(
        n,
      );
