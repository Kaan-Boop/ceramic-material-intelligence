"use client";

import { useEffect, useRef, useState } from "react";
import ProcessReport from './process-report';
import MaterialLibrary from './material-library';
import BodyPicker from './body-picker';
import CompositionChart from './composition-chart';
import SimulationPanel from './simulation-panel';
import {
  api,
  numberTR as fmt,
  type Catalogue,
  type Report,
  type AnalysisRequest,
} from "../lib/api";

type Draft = {
  name: string;
  mass: string;
  rows: { analysis_id: string; amount: string; role: "BASE" | "ADDITION" }[];
  cone: "UNKNOWN" | "06" | "04" | "6" | "8" | "10";
  temperature: string;
  atmosphere: "UNKNOWN" | "OXIDATION" | "REDUCTION" | "OTHER";
  clay: string;
  bodyWindow?: WindowDraft;
  glazeWindow?: WindowDraft;
};
type WindowDraft = { product: string; min: string; max: string; source: string; conditions: string };
const EMPTY_WINDOW: WindowDraft = { product: '', min: '', max: '', source: '', conditions: '' };
function windowRequest(w?: WindowDraft) {
  if (!w || Object.values(w).every(v => !v.trim())) return null;
  const min = parse(w.min), max = parse(w.max);
  if (!w.product.trim() || !w.source.trim() || !w.conditions.trim() || !Number.isFinite(min) || !Number.isFinite(max) || min < 0 || max > 1800 || min > max)
    throw new Error('Pişirim aralığı için ürün, kaynak, koşullar ve geçerli alt/üst °C sınırı birlikte gerekli.');
  return { product_id: w.product.trim(), min_c: min, max_c: max, source_ref: w.source.trim(), conditions: w.conditions.trim() };
}
function WindowFields({ title, value, onChange }: { title: string; value?: WindowDraft; onChange: (v: WindowDraft) => void }) {
  const w = value ?? EMPTY_WINDOW;
  return <details><summary>{title} · isteğe bağlı kaynaklı aralık</summary>
    <p className="helper">Üretici belgesi veya deney referansını girin. Cone değerini tahminen °C’ye çevirmeyin. Boş bırakmak uygundur.</p>
    <div className="field-grid">{([
      ['product', 'Ürün / analiz sürümü', 160], ['min', 'Alt sınır · °C', 12], ['max', 'Üst sınır · °C', 12],
      ['source', 'Kaynak URL / belge referansı', 500], ['conditions', 'Atmosfer, hız ve diğer kaynak koşulları', 1000],
    ] as const).map(([key, label, limit]) => <label className="field" key={key}>{title} · {label}
      <input value={w[key]} maxLength={limit} inputMode={key === 'min' || key === 'max' ? 'decimal' : 'text'} onChange={e => onChange({ ...w, [key]: e.target.value })} />
    </label>)}</div>
  </details>;
}
const STORAGE = "ceramic-lab-draft-v1";
const INITIAL: Draft = {
  name: "",
  mass: "100",
  rows: [],
  cone: "UNKNOWN",
  temperature: "",
  atmosphere: "UNKNOWN",
  clay: "",
};
const parse = (s: string) =>
  s.trim() === "" ? NaN : Number(s.trim().replace(",", "."));
const errorText = (e: unknown) =>
  e instanceof Error ? e.message : "Beklenmeyen bir hata oluştu.";

function fromExample(e: AnalysisRequest): Draft {
  return {
    name: e.recipe_name,
    mass: String(e.base_mass_g ?? 100),
    rows: e.ingredients.map((r) => ({
      analysis_id: r.analysis_id,
      amount: String(r.amount),
      role: r.role ?? "BASE",
    })),
    cone: e.context?.cone ?? "UNKNOWN",
    temperature:
      e.context?.temperature_c == null ? "" : String(e.context.temperature_c),
    atmosphere: e.context?.atmosphere ?? "UNKNOWN",
    clay: e.context?.clay_body ?? "",
  };
}

function requestFrom(d: Draft): AnalysisRequest {
  if (!d.name.trim()) throw new Error("Reçeteye bir ad verin.");
  const amounts = d.rows.map((r) => parse(r.amount));
  if (
    amounts.some(
      (n) => !Number.isFinite(n) || n < 0 || n > 1e6 || (n > 0 && n < 1e-6),
    )
  )
    throw new Error(
      "Miktarlar 0 veya 0,000001–1.000.000 aralığında olmalı. Boş miktar bırakmayın.",
    );
  const mass = parse(d.mass);
  if (!Number.isFinite(mass) || mass < 1e-6 || mass > 1e6)
    throw new Error("Baz kütlesi 0,000001–1.000.000 g aralığında olmalı.");
  const temperature = d.temperature.trim() === "" ? null : parse(d.temperature);
  if (
    temperature !== null &&
    (!Number.isFinite(temperature) || temperature < 0 || temperature > 1800)
  )
    throw new Error(
      "Sıcaklık boş bırakılabilir veya 0–1800 °C aralığında olmalı.",
    );
  return {
    recipe_name: d.name.trim(),
    base_mass_g: mass,
    ingredients: d.rows.map((r, i) => ({ ...r, amount: amounts[i] })),
    context: {
      cone: d.cone,
      temperature_c: temperature,
      atmosphere: d.atmosphere,
      clay_body: d.clay,
      body_window: windowRequest(d.bodyWindow),
      glaze_window: windowRequest(d.glazeWindow),
    },
  };
}

function validDraft(v: unknown, catalogue: Catalogue): v is Draft {
  if (!v || typeof v !== "object") return false;
  const d = v as Draft;
  return (
    typeof d.name === "string" &&
    d.name.length <= 120 &&
    typeof d.mass === "string" &&
    typeof d.temperature === "string" &&
    typeof d.clay === "string" &&
    d.clay.length <= 160 &&
    [d.bodyWindow, d.glazeWindow].every(w => w === undefined || (w !== null && typeof w === 'object' && ['product', 'min', 'max', 'source', 'conditions'].every(k => typeof w[k as keyof WindowDraft] === 'string' && w[k as keyof WindowDraft].length <= 1000))) &&
    ["UNKNOWN", "06", "04", "6", "8", "10"].includes(d.cone) &&
    ["UNKNOWN", "OXIDATION", "REDUCTION", "OTHER"].includes(d.atmosphere) &&
    Array.isArray(d.rows) &&
    d.rows.length > 0 &&
    d.rows.length <= 100 &&
    d.rows.every(
      (r) =>
        r &&
        typeof r.amount === "string" &&
        ["BASE", "ADDITION"].includes(r.role) &&
        catalogue.materials.some((m) => m.analysis_id === r.analysis_id),
    )
  );
}

export default function Lab() {
  const [tab, setTab] = useState<"analyze" | "materials" | "models" | "simulation">("analyze");
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [draft, setDraft] = useState<Draft>(INITIAL);
  const [report, setReport] = useState<Report | null>(null);
  const [baseline, setBaseline] = useState<Report | null>(null);
  const [reportKey, setReportKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [retry, setRetry] = useState(0);
  const requestId = useRef(0);
  const key = JSON.stringify(draft);
  const stale = !!report && key !== reportKey;

  useEffect(() => {
    const abort = new AbortController();
    let active = true;
    const timer = setTimeout(() => abort.abort(), 15000);
    setError("");
    api<Catalogue>("materials", { signal: abort.signal })
      .then((c) => {
        if (active) {
          setCatalogue(c);
          setDraft(fromExample(c.example));
        }
      })
      .catch((e) => {
        if (active)
          setError(
            abort.signal.aborted
              ? "Katalog isteği zaman aşımına uğradı. API sunucusunu kontrol edin."
              : errorText(e),
          );
      })
      .finally(() => clearTimeout(timer));
    return () => {
      active = false;
      clearTimeout(timer);
      abort.abort();
    };
  }, [retry]);

  const update = (patch: Partial<Draft>) => {
    requestId.current++;
    setBusy(false);
    setDraft((d) => ({ ...d, ...patch }));
    setError("");
    setNotice("");
  };
  const rowUpdate = (index: number, patch: Partial<Draft["rows"][number]>) =>
    update({
      rows: draft.rows.map((r, i) => (i === index ? { ...r, ...patch } : r)),
    });
  const materialName = (id: string) =>
    catalogue?.materials.find((m) => m.analysis_id === id)?.name ?? id;

  async function analyze() {
    setError("");
    setNotice("");
    let input: AnalysisRequest;
    try {
      input = requestFrom(draft);
    } catch (e) {
      setError(errorText(e));
      return;
    }
    const id = ++requestId.current;
    const submittedKey = key;
    setBusy(true);
    try {
      const result = await api<Report>("analyses", {
        method: "POST",
        body: JSON.stringify(input),
      });
      if (id === requestId.current) {
        setReport(result);
        setReportKey(submittedKey);
      }
    } catch (e) {
      if (id === requestId.current) setError(errorText(e));
    } finally {
      if (id === requestId.current) setBusy(false);
    }
  }

  function saveDraft() {
    try {
      localStorage.setItem(STORAGE, JSON.stringify({ version: 1, draft }));
      setNotice(
        "Taslak bu tarayıcıya kaydedildi. Bu bir yedek veya sunucu kaydı değildir.",
      );
    } catch {
      setError(
        "Tarayıcı depolaması kullanılamıyor. Raporu dosya olarak indirebilirsiniz.",
      );
    }
  }
  function loadDraft() {
    try {
      const raw = localStorage.getItem(STORAGE);
      if (!raw) {
        setNotice("Bu tarayıcıda kayıtlı taslak yok.");
        return;
      }
      const saved = JSON.parse(raw);
      if (
        !catalogue ||
        saved.version !== 1 ||
        !validDraft(saved.draft, catalogue)
      )
        throw new Error();
      update(saved.draft);
      setNotice("Yerel taslak açıldı. Güncel sonuç için yeniden analiz edin.");
    } catch {
      setError(
        "Taslak okunamadı veya bu katalogla uyumlu değil. Mevcut reçete değiştirilmedi.",
      );
    }
  }
  function download() {
    if (!report || stale) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ceramic-report-${report.report_id.slice(0, 12)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const total = draft.rows
    .filter((r) => r.role === "BASE")
    .reduce((s, r) => s + parse(r.amount), 0);
  const chemistry = report?.chemistry;
  const activeFluxes = Object.entries(
    chemistry?.flux_distribution ?? {},
  ).filter(([, n]) => n > 0);

  return (
    <div className="shell">
      <aside className="rail">
        <a className="brand" href="/" aria-label="Ceramic Glaze Lab ana sayfa">
          <span className="brand-mark">
            c<span>°</span>
          </span>
          <span>
            CERAMIC
            <br />
            <strong>GLAZE LAB</strong>
          </span>
        </a>
        <div className="rail-label">ARAŞTIRMA ALANI</div>
        <nav aria-label="Laboratuvar bölümleri">
          <button
            className={tab === "analyze" ? "nav-active" : ""}
            onClick={() => setTab("analyze")}
          >
            <span>01</span> Reçete laboratuvarı
          </button>
          <button
            className={tab === "materials" ? "nav-active" : ""}
            onClick={() => setTab("materials")}
          >
            <span>02</span> Malzeme kütüphanesi
          </button>
          <button
            className={tab === "models" ? "nav-active" : ""}
            onClick={() => setTab("models")}
          >
            <span>03</span> Model sınırları
          </button>
          <button
            className={tab === "simulation" ? "nav-active" : ""}
            onClick={() => setTab("simulation")}
          >
            <span>04</span> Simülasyon hedefi
          </button>
        </nav>
        <div className="rail-bottom">
          <span className="status-dot" /> YEREL PROTOTİP · v0.1
          <p>
            Önce hesap.
            <br />
            Sonra deney.
            <br />
            Ardından çıkarım.
          </p>
          <small>Üretim reçetesi veya güvenlik onayı vermez.</small>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <span>
            ÇALIŞMA DEFTERİ <span className="slash">/</span>{" "}
            {tab === "analyze"
              ? "REÇETE ANALİZİ"
              : tab === "materials"
                ? "MALZEMELER"
                : tab === "models"
                  ? "MODEL SINIRLARI"
                  : "SİMÜLASYON HEDEFİ"}
          </span>
          <span className="version">PYTHON ENGINE · 0.1</span>
        </header>
        <section className="heading">
          <div>
            <p className="eyebrow">CERAMIC MATERIAL INTELLIGENCE</p>
            <h1>
              {tab === "analyze" ? (
                <>
                  Malzemeden <em>kimyaya.</em>
                </>
              ) : tab === "materials" ? (
                <>
                  Analizin <em>kaynağı.</em>
                </>
              ) : tab === "models" ? (
                <>
                  Bildiğimiz ve <em>bilmediğimiz.</em>
                </>
              ) : (
                <>
                  Hedefini <em>tanımla.</em>
                </>
              )}
            </h1>
            <p className="intro">
              {tab === "analyze"
                ? "Reçeteni oluştur, kimyasını incele, bir sonraki deneyini bilinçli planla."
                : tab === "materials"
                  ? "Her hesap, seçilen malzeme analizinin varsayımları kadar anlamlıdır."
                  : tab === "models"
                    ? "Hesaplanan değer, ölçülmüş sonuç ve tahmin aynı şey değildir."
                    : "Farklı malzeme kombinasyonları için hangi çıktının desteklendiğini seç ve gör."}
            </p>
          </div>
          <span className="edition">
            ARAŞTIRMA
            <br />
            <b>01 / PROTOTİP</b>
          </span>
        </section>
        <div className="demo-banner">
          <span className="banner-icon">i</span>
          <div>
            <strong>{tab==='materials'?'Kaynaklı araştırma kütüphanesi':tab==='simulation'?'Senaryo kapsam geçidi':'Teorik demo kataloğu'}</strong>
            <p>
              {tab==='materials'?'Kayıt bulunması analiz onayı değildir. Teorik girdiler, ürün kimlikleri ve inceleme bekleyen analizler ayrı etiketlenir.':tab==='simulation'?'Bu ekran fiziksel sonuç üretmez; seçilen hedef için veri ve model kapsamını açıkça raporlar.':'Bu dört malzeme ideal kimyasal formüllerdir; ticari ürün veya lot analizi değildir. Çıktılar teorik oksit hesabıdır.'}
            </p>
          </div>
          <span className="tag amber">{tab==='materials'?'ARAŞTIRMA DİZİNİ':tab==='simulation'?'KAPSAM · HESAP DEĞİL':'THEORETICAL'}</span>
        </div>
        {error && (
          <div className="message error" role="alert">
            {error}
            {!catalogue && (
              <button onClick={() => setRetry((n) => n + 1)}>
                Yeniden bağlan
              </button>
            )}
          </div>
        )}
        {notice && (
          <div className="message" role="status">
            {notice}
          </div>
        )}
        {!catalogue ? (
          <section className="card">
            <h2>Katalog bağlantısı</h2>
            <p>
              {error
                ? "Python API sunucusu başlatıldıktan sonra yeniden deneyin."
                : "Kaynaklı teorik analizler yükleniyor…"}
            </p>
          </section>
        ) : (
          <>
            {tab === "analyze" && (
              <div className="workspace">
                <section className="card recipe-card">
                  <div className="card-heading">
                    <div>
                      <span className="eyebrow">01 · GİRDİ</span>
                      <h2>Reçeten</h2>
                    </div>
                    <span className="tag">KURU BAZ</span>
                  </div>
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      void analyze();
                    }}
                  >
                    <label className="field">
                      Reçete adı
                      <input
                        value={draft.name}
                        maxLength={120}
                        onChange={(e) => update({ name: e.target.value })}
                        placeholder="Araştırmana bir ad ver"
                      />
                    </label>
                    <div className="ingredients-head">
                      <span>Malzeme / analiz</span>
                      <span>Miktar</span>
                    </div>
                    <div className="ingredient-list">
                      {draft.rows.map((r, i) => (
                        <div className="ingredient" key={i}>
                          <span className="row-number">
                            {String(i + 1).padStart(2, "0")}
                          </span>
                          <div className="material-select">
                            <select
                              aria-label={`Malzeme ${i + 1}`}
                              value={r.analysis_id}
                              onChange={(e) =>
                                rowUpdate(i, { analysis_id: e.target.value })
                              }
                            >
                              {catalogue.materials.map((m) => (
                                <option
                                  key={m.analysis_id}
                                  value={m.analysis_id}
                                >
                                  {m.name}
                                </option>
                              ))}
                            </select>
                            <span>
                              theoretical-v1 ·{" "}
                              {
                                catalogue.materials.find(
                                  (m) => m.analysis_id === r.analysis_id,
                                )?.formula
                              }
                            </span>
                            <details className="ingredient-info"><summary>Malzeme bilgisi ⓘ</summary><p>İdeal formül referansı; ticari ürün veya üretici analizi değildir.</p><CompositionChart oxides={catalogue.materials.find(m=>m.analysis_id===r.analysis_id)?.oxides??{}} basis="DRY"/><a href={`/materials/${r.analysis_id}`} target="_blank" rel="noreferrer">Ayrıntılı analiz ve kaynak ↗</a></details>
                          </div>
                          <input
                            className="amount"
                            aria-label={`Miktar ${i + 1}`}
                            inputMode="decimal"
                            value={r.amount}
                            onChange={(e) =>
                              rowUpdate(i, { amount: e.target.value })
                            }
                          />
                          <select
                            className="role"
                            aria-label={`Rol ${i + 1}`}
                            value={r.role}
                            onChange={(e) =>
                              rowUpdate(i, {
                                role: e.target.value as "BASE" | "ADDITION",
                              })
                            }
                          >
                            <option value="BASE">Baz</option>
                            <option value="ADDITION">İlave %</option>
                          </select>
                          <button
                            type="button"
                            className="remove"
                            aria-label={`Satır ${i + 1} sil`}
                            disabled={draft.rows.length === 1}
                            onClick={() =>
                              update({
                                rows: draft.rows.filter((_, j) => j !== i),
                              })
                            }
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                    <div className="recipe-summary">
                      <button
                        className="text-button"
                        type="button"
                        disabled={draft.rows.length >= 100}
                        onClick={() =>
                          update({
                            rows: [
                              ...draft.rows,
                              {
                                analysis_id: catalogue.materials[0].analysis_id,
                                amount: "0",
                                role: "BASE",
                              },
                            ],
                          })
                        }
                      >
                        ＋ Malzeme ekle
                      </button>
                      <span>
                        Baz toplamı{" "}
                        <b>{Number.isFinite(total) ? fmt(total) : "—"}</b> parça
                      </span>
                    </div>
                    <label className="field mass-field">
                      Hazırlanacak baz kütlesi{" "}
                      <div className="unit-input">
                        <input
                          aria-label="Baz kütlesi"
                          inputMode="decimal"
                          value={draft.mass}
                          onChange={(e) => update({ mass: e.target.value })}
                        />
                        <span>g</span>
                      </div>
                    </label>
                    <p className="helper">
                      Baz parçaları %100’e normalize edilir. İlave %2, baz
                      kütlesinin üzerine eklenir; baz toplamına katılmaz.
                    </p>
                    <div className="divider" />
                    <div className="card-heading small">
                      <h3>Pişirim bağlamı</h3>
                      <span className="tag">KAYIT · TAHMİN DEĞİL</span>
                    </div>
                    <div className="field-grid">
                      <label className="field">
                        Hedef cone
                        <select
                          value={draft.cone}
                          onChange={(e) =>
                            update({ cone: e.target.value as Draft["cone"] })
                          }
                        >
                          <option value="UNKNOWN">Belirtilmedi</option>
                          {["06", "04", "6", "8", "10"].map((c) => (
                            <option key={c} value={c}>
                              Cone {c}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label className="field">
                        Hedef sıcaklık · °C
                        <input
                          inputMode="decimal"
                          value={draft.temperature}
                          onChange={(e) =>
                            update({ temperature: e.target.value })
                          }
                          placeholder="İsteğe bağlı"
                        />
                      </label>
                      <label className="field">
                        Atmosfer
                        <select
                          value={draft.atmosphere}
                          onChange={(e) =>
                            update({
                              atmosphere: e.target.value as Draft["atmosphere"],
                            })
                          }
                        >
                          <option value="UNKNOWN">Belirtilmedi</option>
                          <option value="OXIDATION">Oksidasyon</option>
                          <option value="REDUCTION">Redüksiyon</option>
                          <option value="OTHER">Diğer</option>
                        </select>
                      </label>
                      <BodyPicker value={draft.clay} onChange={(clay,bodyWindow)=>update({clay,bodyWindow})}/>
                    </div>
                    <WindowFields title="Bünye" value={draft.bodyWindow} onChange={bodyWindow => update({ bodyWindow })} />
                    <WindowFields title="Sır" value={draft.glazeWindow} onChange={glazeWindow => update({ glazeWindow })} />
                    <p className="helper">
                      Cone ve sıcaklık eşdeğer değildir. Bu bilgiler mevcut
                      kimya hesabını değiştirmez.
                    </p>
                    <button
                      className="primary analyze-button"
                      type="submit"
                      disabled={busy}
                    >
                      {busy ? "Hesaplanıyor…" : "Reçeteyi analiz et"}
                      <span aria-hidden="true">↗</span>
                    </button>
                  </form>
                  <div className="draft-actions">
                    <button onClick={saveDraft}>Taslağı kaydet</button>
                    <button onClick={loadDraft}>Taslağı aç</button>
                  </div>
                  <p className="helper center">
                    Yalnızca bu tarayıcıda · otomatik sunucu kaydı yok
                  </p>
                </section>
                <section
                  className="results"
                  aria-label="Analiz sonuçları"
                  aria-busy={busy}
                >
                  <div className="card result-header">
                    <div className="card-heading">
                      <div>
                        <span className="eyebrow">02 · ÇIKTI</span>
                        <h2>Kimya raporu</h2>
                      </div>
                      <span className={`tag ${report ? "green" : ""}`}>
                        {report ? "CALCULATED" : "HENÜZ HESAPLANMADI"}
                      </span>
                    </div>
                    {!report ? (
                      <div className="empty-result">
                        <div className="empty-orbit" aria-hidden="true">
                          <span>Si</span>
                          <span>Al</span>
                          <span>O</span>
                        </div>
                        <h3>İlk hesabın burada başlayacak.</h3>
                        <p>
                          Reçeteyi analiz ettiğinde oksit bileşimi, UMF ve mol
                          oranlarını gerçek Python motorundan alacaksın.
                        </p>
                        <div className="empty-steps">
                          <span>REÇETE</span>
                          <b>→</b>
                          <span>OKSİTLER</span>
                          <b>→</b>
                          <span>UMF</span>
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="report-name">
                          {report.request.recipe_name}
                        </p>
                        {stale && (
                          <div className="message stale" role="status">
                            Girdi değişti. Bu rapor önceki reçeteye ait; yeniden
                            analiz edin.
                          </div>
                        )}
                        <div className="metrics">
                          <div>
                            <span>SiO₂ / Al₂O₃</span>
                            <strong>
                              {fmt(chemistry?.ratios.SiO2_to_Al2O3_molar.value)}
                            </strong>
                            <small>Oksit mol oranı</small>
                          </div>
                          <div>
                            <span>TEORİK OKSİT</span>
                            <strong>
                              {fmt(chemistry?.retained_oxide_mass_g, 2)}
                              <small> g</small>
                            </strong>
                            <small>LOI hariç kütle</small>
                          </div>
                          <div>
                            <span>LOI</span>
                            <strong>
                              {fmt(chemistry?.loi_mass_g, 2)}
                              <small> g</small>
                            </strong>
                            <small>Gaz türü belirlenmez</small>
                          </div>
                        </div>
                        <div className="result-actions">
                          <button
                            onClick={() => {
                              setBaseline(report);
                              setNotice(
                                "Bu rapor karşılaştırma referansı olarak sabitlendi. Reçeteyi değiştirip tekrar analiz edin.",
                              );
                            }}
                            disabled={stale}
                          >
                            Karşılaştırma için sabitle
                          </button>
                          <button onClick={download} disabled={stale}>
                            JSON raporu indir ↓
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                  {report && chemistry && (
                    <>
                      <section className="card">
                        <div className="card-heading">
                          <h3>Oksitler & UMF</h3>
                          <span className="tag green">CALCULATED</span>
                        </div>
                        <p className="helper">
                          Oksit % değerleri LOI hariç teorik oksit toplamına
                          göredir. UMF: seçilmiş akıların mol toplamı = 1.
                        </p>
                        <CompositionChart oxides={chemistry.retained_oxide_wt_pct} basis="LOI hariç teorik oksit toplamı"/>
                        {chemistry.umf.status === "UNAVAILABLE" && (
                          <p className="message">
                            UMF hesaplanamıyor: akı mol toplamı sıfır.
                          </p>
                        )}
                        <div className="table-scroll">
                          <table>
                            <thead>
                              <tr>
                                <th>Oksit</th>
                                <th>Kütle · g</th>
                                <th>Oksit %</th>
                                <th>Mol %</th>
                                <th>UMF</th>
                              </tr>
                            </thead>
                            <tbody>
                              {Object.entries(chemistry.oxide_mass_g).map(
                                ([oxide, mass]) => (
                                  <tr key={oxide}>
                                    <th>{oxide}</th>
                                    <td>{fmt(mass)}</td>
                                    <td>
                                      {fmt(
                                        chemistry.retained_oxide_wt_pct[oxide],
                                        2,
                                      )}
                                    </td>
                                    <td>
                                      {fmt(chemistry.oxide_mol_pct[oxide], 2)}
                                    </td>
                                    <td className="umf-cell">
                                      {fmt(chemistry.umf.values?.[oxide])}
                                    </td>
                                  </tr>
                                ),
                              )}
                            </tbody>
                          </table>
                        </div>
                        <div className="ratios-line">
                          <span>
                            Atomik Si / Al{" "}
                            <b>{fmt(chemistry.ratios.atomic_Si_to_Al.value)}</b>
                          </span>
                          <span>
                            RO / R₂O{" "}
                            <b>{fmt(chemistry.ratios.RO_to_R2O.value)}</b>
                          </span>
                        </div>
                        <p className="helper">
                          “—” sıfır payda nedeniyle hesaplanamayan değerdir;
                          sıfır değildir.
                        </p>
                      </section>
                      <section className="card">
                        <div className="card-heading">
                          <h3>Akı dağılımı</h3>
                          <span className="eyebrow">MOL PAYI</span>
                        </div>
                        {activeFluxes.length ? (
                          <div className="flux-bars">
                            {activeFluxes.map(([oxide, value], i) => (
                              <div className="flux-row" key={oxide}>
                                <strong>{oxide}</strong>
                                <div className="bar-track">
                                  <span
                                    className={`bar bar-${i % 3}`}
                                    style={{ width: `${value * 100}%` }}
                                  />
                                </div>
                                <span>{fmt(value * 100, 1)}%</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p>
                            Akı dağılımı hesaplanamıyor; seçilmiş akıların mol
                            toplamı sıfır.
                          </p>
                        )}
                      </section>
                      {baseline && (
                        <section className="card">
                          <div className="card-heading">
                            <h3>Kimyasal karşılaştırma</h3>
                            <button
                              className="text-button"
                              onClick={() => setBaseline(null)}
                            >
                              Kaldır
                            </button>
                          </div>
                          <p className="helper">
                            Referans: {baseline.request.recipe_name} ·{" "}
                            {baseline.report_id.slice(0, 8)}. Sonuç benzerliği
                            veya başarı olasılığı değildir.
                          </p>
                          <div className="table-scroll">
                            <table>
                              <thead>
                                <tr>
                                  <th>UMF</th>
                                  <th>Sabitlenen</th>
                                  <th>Son rapor</th>
                                  <th>Fark</th>
                                </tr>
                              </thead>
                              <tbody>
                                {Array.from(
                                  new Set([
                                    ...Object.keys(
                                      baseline.chemistry.oxide_mass_g,
                                    ),
                                    ...Object.keys(chemistry.oxide_mass_g),
                                  ]),
                                )
                                  .sort()
                                  .map((o) => {
                                    const a = baseline.chemistry.umf.values
                                      ? (baseline.chemistry.umf.values[o] ?? 0)
                                      : null;
                                    const b = chemistry.umf.values
                                      ? (chemistry.umf.values[o] ?? 0)
                                      : null;
                                    return (
                                      <tr key={o}>
                                        <th>{o}</th>
                                        <td>{fmt(a)}</td>
                                        <td>{fmt(b)}</td>
                                        <td>
                                          {a !== null && b !== null
                                            ? fmt(b - a)
                                            : "—"}
                                        </td>
                                      </tr>
                                    );
                                  })}
                              </tbody>
                            </table>
                          </div>
                        </section>
                      )}
                      <section className="card">
                        <div className="card-heading">
                          <h3>Normalize reçete</h3>
                          <span className="eyebrow">
                            {fmt(chemistry.total_dry_batch_mass_g)} g TOPLAM
                          </span>
                        </div>
                        <div className="table-scroll">
                          <table>
                            <thead>
                              <tr>
                                <th>Malzeme</th>
                                <th>Rol</th>
                                <th>Bazın %’si</th>
                                <th>Kuru g</th>
                              </tr>
                            </thead>
                            <tbody>
                              {chemistry.normalized_ingredients.map((r, i) => (
                                <tr key={i}>
                                  <th>{materialName(r.analysis_id)}</th>
                                  <td>{r.role === "BASE" ? "Baz" : "İlave"}</td>
                                  <td>{fmt(r.percent_of_base)}</td>
                                  <td>{fmt(r.dry_mass_g)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </section>
                      <section className="card limits">
                        <h3>Bu raporu nasıl okumalı?</h3>
                        <ul>
                          {report.notices.map((n) => (
                            <li key={n}>{n}</li>
                          ))}
                        </ul>
                        <details>
                          <summary>Kaynaklar & yeniden üretim bilgisi</summary>
                          <p>
                            Motor: {chemistry.engine_version}
                            <br />
                            Sabit seti: {chemistry.constant_set_id}
                            <br />
                            UMF convention: {chemistry.umf_convention}
                          </p>
                          <p className="hash">
                            Girdi SHA-256: {chemistry.input_hash}
                          </p>
                          {report.materials.map((m) => (
                            <p key={m.analysis_id}>
                              <strong>{m.name}</strong> · {m.version}
                              <br />
                              <code>{m.source_ref}</code>
                              <br />
                              <a
                                href={m.source_url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                Sabit setinin kaynak kodu ↗
                              </a>
                            </p>
                          ))}
                          <p>
                            Tam analiz snapshot’ı JSON raporuna dahildir. Rapor
                            sunucuda saklanmaz.
                          </p>
                        </details>
                      </section>
                    </>
                  )}
                  {report && <ProcessReport report={report.process} />}
                  <div className="prediction-note">
                    <span>◌</span>
                    <div>
                      <strong>Fiziksel sonuç henüz tahmin edilmiyor.</strong>
                      <p>
                        Renk, yüzey, çatlama ve gıda güvenliği için bu hesap
                        yeterli değildir. Gerçek test ve doğrulanmış modeller
                        gerekir.
                      </p>
                    </div>
                  </div>
                </section>
              </div>
            )}
            {tab === "materials" && (
              <MaterialLibrary />
            )}
            {tab === "simulation" && (
              <SimulationPanel catalogue={catalogue} recipeRows={draft.rows} />
            )}
            {tab === "models" && (
              <section className="card model-card">
                <h2>Bir hesaplayıcıdan laboratuvara</h2>
                <p>
                  Bu ekran model çalıştırmaz; mevcut araştırma bileşenlerinin
                  sınırlarını gösterir.
                </p>
                <div className="model-list">
                  {[
                    [
                      "CALCULATED",
                      "Reçete kimyası",
                      "Bu prototipte çalışır. Kuru baz, oksit kütlesi, mol, UMF ve açık oranlar. Faz veya yüzey tahmini değildir.",
                    ],
                    [
                      "OBSERVED",
                      "Gerçek deneyler",
                      "Fotoğraf, uygulama, pişirim ve ölçüm kaydı sonraki teslimde. Teorik katalog deney verisi değildir.",
                    ],
                    [
                      "PREDICTED · DENEYSEL",
                      "Isı, genleşme ve buhar",
                      "Araştırma kodunda ayrı modeller var. Bu arayüze bağlı değiller; birleşik ve deneysel doğrulanmış sanal fırın değiller.",
                    ],
                    [
                      "UNAVAILABLE",
                      "Yüzey ve kusur olasılığı",
                      "Kalibre model henüz yok. Matlık, renk veya çatlama yüzdesi gösterilmez.",
                    ],
                  ].map(([label, title, text]) => (
                    <div key={title}>
                      <span className="tag">{label}</span>
                      <h3>{title}</h3>
                      <p>{text}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
        <footer>
          <span>CERAMIC GLAZE LAB</span>
          <span>Hesap ≠ gözlem ≠ tahmin</span>
        </footer>
      </main>
    </div>
  );
}
