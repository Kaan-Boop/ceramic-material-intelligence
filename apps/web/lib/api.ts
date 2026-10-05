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
