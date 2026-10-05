"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type Catalogue, type SimulationCapabilityReport, type SimulationChemistryReport } from "../lib/api";
import { firingLabel, kinds, statuses, type LibraryRecord } from "../lib/library";
import CompositionChart from "./composition-chart";

type RecipeRow = { analysis_id: string; amount: string; role: "BASE" | "ADDITION" };
type BodyOption = { id: string; name: string; brand: string; kind: string; status: string; engine_eligible: boolean; windows: LibraryRecord["windows"]; note: string; source_name: string };
type ChemistryRecipe = { layer_id: string; base_mass_g: number; ingredients: Array<{ analysis_id: string; amount: number; role: "BASE" | "ADDITION" }> };

const OUTPUTS = [
  ["oxide_composition", "Oksit bileşimi", "Reçete analizlerinden hesaplanır."],
  ["umf", "UMF / Seger", "Flux ve mol girdileri tamamlanırsa hesaplanır."],
  ["firing_timeline", "Pişirim zaman çizelgesi", "Yalnızca planlanan programı gösterir."],
  ["fit_risk", "Sır–bünye uyumu göstergesi", "CTE verisi yoksa sınırlı kalır."],
  ["melt_fraction", "Erime fraksiyonu", "Doğrulanmış sıcaklık-bağımlı model henüz yok."],
  ["viscosity", "Viskozite", "Sıcaklık ve bileşim eğrisi gerekir."],
  ["surface_state", "Yüzey durumu", "Gerçek deney veya kalibre model gerekir."],
  ["defect_risk", "Kusur riski", "Doğrulanmış deney serisi gerekir."],
] as const;

const statusLabel: Record<SimulationCapabilityReport["outputs"][string]["status"], string> = {
  AVAILABLE: "KULLANILABİLİR",
  PARTIAL: "KISMİ",
  UNAVAILABLE: "HAZIR DEĞİL",
};

export default function SimulationPanel({ catalogue, recipeRows }: { catalogue: Catalogue; recipeRows: RecipeRow[] }) {
  const [bodyId, setBodyId] = useState(catalogue.materials[0]?.analysis_id ?? "");
  const [library, setLibrary] = useState<LibraryRecord[]>([]);
  const [libraryError, setLibraryError] = useState("");
  const [temperature, setTemperature] = useState("");
  const [selected, setSelected] = useState<string[]>(["oxide_composition", "umf", "firing_timeline", "fit_risk"]);
  const [report, setReport] = useState<SimulationCapabilityReport | null>(null);
  const [chemistry, setChemistry] = useState<SimulationChemistryReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [chemistryBusy, setChemistryBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    api<{ records: LibraryRecord[] }>("library", { signal: controller.signal })
      .then((response) => setLibrary(response.records))
      .catch((cause) => {
        if (!controller.signal.aborted) setLibraryError(cause instanceof Error ? cause.message : "Malzeme kütüphanesi yüklenemedi.");
      });
    return () => controller.abort();
  }, []);

  const bodyOptions = useMemo(() => {
    const theoretical: BodyOption[] = catalogue.materials.map((material) => ({
      id: material.analysis_id,
      name: material.name,
      brand: "Teorik referans",
      kind: "IDEAL_MATERIAL",
      status: "THEORETICAL",
      engine_eligible: true,
      windows: [],
      note: "İdeal oksit referansı; ticari çamur analizi değildir.",
      source_name: "Teorik demo kataloğu",
    }));
    const candidates = [...theoretical, ...library.filter((record) => record.kind === "CLAY_BODY")];
    return candidates.filter((record, index, all) => all.findIndex((candidate) => candidate.id === record.id) === index);
  }, [catalogue.materials, library]);

  const selectedBody = bodyOptions.find((record) => record.id === bodyId);

  function toggle(output: string) {
    setSelected((current) => current.includes(output) ? current.filter((item) => item !== output) : [...current, output]);
    setReport(null);
    setChemistry(null);
  }

  function scenarioPayload(target: number) {
    return {
      scenario_id: "ui-current-target",
      body: { layer_id: "body", materials: [{ analysis_id: bodyId, role: "BODY" }] },
      layers: recipeRows.length ? [{
        layer_id: "glaze",
        materials: recipeRows.map((row) => ({ analysis_id: row.analysis_id, role: row.role === "ADDITION" ? "ADDITION" : "GLAZE", amount_g: Number(row.amount) || undefined })),
        application_method: "NONE" as const,
        coat_count: 0,
      }] : [],
      final_firing: { name: "user-target", start_c: 20, segments: [{ target_c: target, rate_c_per_hour: null, hold_minutes: 0 }], atmosphere: "UNKNOWN" },
      geometry: { kind: "TILE" as const, thickness_mm: 8, length_mm: 100, width_mm: 100 },
      target: { objective: "Kullanıcının seçtiği hedefler", requested_outputs: selected, reference_temperature_c: 20 },
    };
  }

  async function assess() {
    const target = Number(temperature.replace(",", "."));
    if (!bodyId || !Number.isFinite(target) || target < 0 || target > 1800) {
      setError("Bünye ve 0–1800 °C aralığında bir final sıcaklığı seçin.");
      return;
    }
    if (!selected.length) {
      setError("En az bir simülasyon hedefi seçin.");
      return;
    }
    setError("");
    setReport(null);
    setChemistry(null);
    setBusy(true);
    try {
      const result = await api<SimulationCapabilityReport>("simulations/capabilities", {
        method: "POST",
        body: JSON.stringify({
          ...scenarioPayload(target),
        }),
      });
      setReport(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Simülasyon kapsamı okunamadı.");
    } finally {
      setBusy(false);
    }
  }

  async function calculateChemistry() {
    const target = Number(temperature.replace(",", "."));
    if (!bodyId || !Number.isFinite(target) || target < 0 || target > 1800) {
      setError("Katman kimyası için bünye ve 0–1800 °C aralığında bir final sıcaklığı seçin.");
      return;
    }
    setError("");
    setChemistry(null);
    setChemistryBusy(true);
    try {
      const recipes: ChemistryRecipe[] = [{ layer_id: "body", base_mass_g: 100, ingredients: [{ analysis_id: bodyId, amount: 100, role: "BASE" }] }];
      if (recipeRows.length) recipes.push({ layer_id: "glaze", base_mass_g: 100, ingredients: recipeRows.map((row) => ({ analysis_id: row.analysis_id, amount: Number(row.amount), role: row.role })) });
      const result = await api<SimulationChemistryReport>("simulations/chemistry", { method: "POST", body: JSON.stringify({ scenario: scenarioPayload(target), recipes }) });
      setChemistry(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Katman kimyası hesaplanamadı.");
    } finally {
      setChemistryBusy(false);
    }
  }

  return <section className="card simulation-panel" aria-label="Simülasyon hedefleri">
    <div className="card-heading">
      <div><span className="eyebrow">04 · KAPSAM GEÇİDİ</span><h2>Hedefe göre simülasyon</h2></div>
      <span className="tag">TAHMİN DEĞİL</span>
    </div>
    <p className="helper">Bu alan, seçtiğin kombinasyon için hangi çıktının mevcut olduğunu gösterir. Eksik fiziksel veri otomatik tamamlanmaz.</p>
    <div className="field-grid">
      <label className="field">Gövde / çamur analiz referansı<select value={bodyId} onChange={(event) => { setBodyId(event.target.value); setReport(null); }}>
        {bodyOptions.map((record) => <option key={record.id} value={record.id}>{record.name} · {record.brand} · {record.kind === "IDEAL_MATERIAL" ? "teorik" : firingLabel(record)}</option>)}
      </select></label>
      <label className="field">Final sıcaklığı · °C<input value={temperature} onChange={(event) => { setTemperature(event.target.value); setReport(null); }} inputMode="decimal" placeholder="Örn. 1220" /></label>
    </div>
    {selectedBody && <div className="simulation-material-note">
      <strong>{selectedBody.name}</strong><span className="tag">{kinds[selectedBody.kind] ?? selectedBody.kind} · {statuses[selectedBody.status] ?? selectedBody.status}</span>
      <p>{selectedBody.engine_eligible ? "Sürümü mevcut deterministik kimya hesabına bağlanabilir." : "Bu kayıt kütüphanede görünür; ancak kabul edilmiş oksit analizi olmadığı için kimya motoruna otomatik aktarılmaz."}</p>
      <small>{selectedBody.kind === "CLAY_BODY" ? firingLabel(selectedBody) : "Pişirim aralığı kayıtlı değil"} · {selectedBody.source_name}</small>
    </div>}
    {libraryError && <p className="helper">Hazır çamur kütüphanesi yüklenemedi; teorik referanslar kullanılabilir. {libraryError}</p>}
    {!libraryError && <p className="helper">Hazır ürünler kaynak aralığıyla gösterilir. Ürün adı, analiz sürümü yerine geçmez; ürünün oksit analizi yoksa sonuçlar açıkça kullanılamaz olarak kalır.</p>}
    <fieldset className="simulation-targets"><legend>İstenen çıktılar</legend><div className="simulation-target-grid">{OUTPUTS.map(([id, title, hint]) => <label key={id}><input type="checkbox" checked={selected.includes(id)} onChange={() => toggle(id)} /><span><strong>{title}</strong><small>{hint}</small></span></label>)}</div></fieldset>
    {error && <p className="message error" role="alert">{error}</p>}
    <div className="simulation-actions"><button className="primary" type="button" onClick={() => void assess()} disabled={busy || chemistryBusy}>{busy ? "Kapsam inceleniyor…" : "Simülasyon kapsamını değerlendir ↗"}</button><button className="text-button" type="button" onClick={() => void calculateChemistry()} disabled={busy || chemistryBusy}>{chemistryBusy ? "Kimya hesaplanıyor…" : "Katman kimyasını hesapla"}</button></div>
    {report && <div className="simulation-report" role="status"><div className="simulation-report-head"><strong>Bu senaryo için kapsam</strong><small>{report.input_hash.slice(0, 12)}…</small></div>{report.material_resolutions && <details className="simulation-resolutions" open><summary>Çözülen analiz sürümleri ({report.material_resolutions.length})</summary><ul>{report.material_resolutions.map((material) => <li key={material.analysis_id}><strong>{material.analysis_id}</strong><span>{material.status} · {material.version}</span><small>{material.engine_eligible ? "Kimya motoruna uygun" : "Katalogda, hesap dışı"} · {material.source_name}</small></li>)}</ul></details>}<div className="simulation-status-grid">{Object.entries(report.outputs).map(([id, item]) => <article key={id} className={`simulation-status ${item.status.toLowerCase()}`}><span className="tag">{statusLabel[item.status]}</span><strong>{OUTPUTS.find(([key]) => key === id)?.[1] ?? id}</strong><p>{item.reason}</p><small>{item.evidence_kind} · {item.method_kind}</small></article>)}</div><p className="helper">Bu rapor fiziksel sonuç veya olasılık değildir; yalnızca mevcut veri/model kapsamını bildirir.</p></div>}
    {chemistry && <div className="simulation-report chemistry-report" role="status"><div className="simulation-report-head"><strong>Katman kimyası · CALCULATED</strong><small>{chemistry.scenario_input_hash.slice(0, 12)}…</small></div><p className="helper">Bu sonuç kuru baz oksit muhasebesidir. Bünye ve kaplama ayrı hesaplanır; arayüz reaksiyonu veya pişmiş yüzey tahmini değildir.</p><div className="chemistry-layer-grid">{chemistry.layer_results.map((layer) => <article className="simulation-status" key={layer.layer_id}><strong>{layer.layer_id}</strong><CompositionChart oxides={layer.retained_oxide_wt_pct} basis="DRY · retained oxide"/><small>UMF: {layer.umf.status === "AVAILABLE" ? "mevcut" : layer.umf.unavailable_reason ?? "kullanılamaz"} · SiO₂/Al₂O₃: {layer.ratios.SiO2_to_Al2O3_molar?.value == null ? "—" : layer.ratios.SiO2_to_Al2O3_molar.value.toLocaleString("tr-TR", { maximumFractionDigits: 3 })}</small></article>)}</div><p className="helper">{chemistry.limitations.join(" ")}</p></div>}
  </section>;
}
