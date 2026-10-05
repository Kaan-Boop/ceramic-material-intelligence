"use client";

import { useState } from "react";
import { api, type Catalogue, type SimulationCapabilityReport } from "../lib/api";

type RecipeRow = { analysis_id: string; amount: string; role: "BASE" | "ADDITION" };

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
  const [temperature, setTemperature] = useState("");
  const [selected, setSelected] = useState<string[]>(["oxide_composition", "umf", "firing_timeline", "fit_risk"]);
  const [report, setReport] = useState<SimulationCapabilityReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function toggle(output: string) {
    setSelected((current) => current.includes(output) ? current.filter((item) => item !== output) : [...current, output]);
    setReport(null);
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
    setBusy(true);
    try {
      const result = await api<SimulationCapabilityReport>("simulations/capabilities", {
        method: "POST",
        body: JSON.stringify({
          scenario_id: "ui-current-target",
          body: { layer_id: "body", materials: [{ analysis_id: bodyId, role: "BODY" }] },
          layers: recipeRows.length ? [{
            layer_id: "glaze",
            materials: recipeRows.map((row) => ({ analysis_id: row.analysis_id, role: row.role === "ADDITION" ? "ADDITION" : "GLAZE", amount_g: Number(row.amount) || undefined })),
            application_method: "NONE",
            coat_count: 0,
          }] : [],
          final_firing: { name: "user-target", start_c: 20, segments: [{ target_c: target, rate_c_per_hour: null, hold_minutes: 0 }], atmosphere: "UNKNOWN" },
          geometry: { kind: "TILE", thickness_mm: 8, length_mm: 100, width_mm: 100 },
          target: { objective: "Kullanıcının seçtiği hedefler", requested_outputs: selected, reference_temperature_c: 20 },
        }),
      });
      setReport(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Simülasyon kapsamı okunamadı.");
    } finally {
      setBusy(false);
    }
  }

  return <section className="card simulation-panel" aria-label="Simülasyon hedefleri">
    <div className="card-heading">
      <div><span className="eyebrow">04 · KAPSAM GEÇİDİ</span><h2>Hedefe göre simülasyon</h2></div>
      <span className="tag">TAHMİN DEĞİL</span>
    </div>
    <p className="helper">Bu alan, seçtiğin kombinasyon için hangi çıktının mevcut olduğunu gösterir. Eksik fiziksel veri otomatik tamamlanmaz.</p>
    <div className="field-grid">
      <label className="field">Gövde analiz referansı<select value={bodyId} onChange={(event) => { setBodyId(event.target.value); setReport(null); }}>{catalogue.materials.map((material) => <option key={material.analysis_id} value={material.analysis_id}>{material.name}</option>)}</select></label>
      <label className="field">Final sıcaklığı · °C<input value={temperature} onChange={(event) => { setTemperature(event.target.value); setReport(null); }} inputMode="decimal" placeholder="Örn. 1220" /></label>
    </div>
    <p className="helper">Bu prototipteki katalog teorik analizlerden oluşur; seçilen kayıt ticari stoneware veya üretici lot analizi anlamına gelmez.</p>
    <fieldset className="simulation-targets"><legend>İstenen çıktılar</legend><div className="simulation-target-grid">{OUTPUTS.map(([id, title, hint]) => <label key={id}><input type="checkbox" checked={selected.includes(id)} onChange={() => toggle(id)} /><span><strong>{title}</strong><small>{hint}</small></span></label>)}</div></fieldset>
    {error && <p className="message error" role="alert">{error}</p>}
    <button className="primary" type="button" onClick={() => void assess()} disabled={busy}>{busy ? "Kapsam inceleniyor…" : "Simülasyon kapsamını değerlendir ↗"}</button>
    {report && <div className="simulation-report" role="status"><div className="simulation-report-head"><strong>Bu senaryo için kapsam</strong><small>{report.input_hash.slice(0, 12)}…</small></div><div className="simulation-status-grid">{Object.entries(report.outputs).map(([id, item]) => <article key={id} className={`simulation-status ${item.status.toLowerCase()}`}><span className="tag">{statusLabel[item.status]}</span><strong>{OUTPUTS.find(([key]) => key === id)?.[1] ?? id}</strong><p>{item.reason}</p><small>{item.evidence_kind} · {item.method_kind}</small></article>)}</div><p className="helper">Bu rapor fiziksel sonuç veya olasılık değildir; yalnızca mevcut veri/model kapsamını bildirir.</p></div>}
  </section>;
}
