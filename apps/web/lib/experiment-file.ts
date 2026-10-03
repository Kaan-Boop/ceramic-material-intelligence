export const MAX_FILE_BYTES = 2 * 1024 * 1024;
export type ExperimentDraft = {
  context: Record<'body_revision'|'glaze_revision'|'application_revision'|'firing_run_id'|'specimen_id'|'sensor_location', string>;
  rows: { time: string; predicted: string; observed: string }[];
  source: string; model: string; kind: 'REAL'|'SYNTHETIC';
};
export type ExperimentFile = { format: 'ceramic-experiment'; version: 1; saved_at: string; draft: ExperimentDraft; archived_reports: unknown[] };
const contextKeys = ['body_revision','glaze_revision','application_revision','firing_run_id','specimen_id','sensor_location'];
function object(v: unknown): v is Record<string, unknown> { return v !== null && typeof v === 'object' && !Array.isArray(v); }
function keys(v: Record<string, unknown>, expected: string[]) { return Object.keys(v).sort().join('|') === [...expected].sort().join('|'); }
function text(v: unknown, max: number): v is string { return typeof v === 'string' && v.length <= max; }

export function parseExperimentFile(raw: string): ExperimentFile {
  if (new TextEncoder().encode(raw).length > MAX_FILE_BYTES) throw new Error('Dosya 2 MiB sınırını aşıyor.');
  let v: unknown;
  try { v = JSON.parse(raw); } catch { throw new Error('Geçerli bir JSON dosyası seçin.'); }
  if (!object(v) || !keys(v,['format','version','saved_at','draft','archived_reports']) || v.format !== 'ceramic-experiment' || v.version !== 1)
    throw new Error('Desteklenmeyen deney dosyası veya sürümü.');
  if (!text(v.saved_at,40) || !Number.isFinite(Date.parse(v.saved_at))) throw new Error('Kayıt tarihi geçersiz.');
  const d = v.draft;
  if (!object(d) || !keys(d,['context','rows','source','model','kind']) || !object(d.context) || !keys(d.context,contextKeys) ||
      !Object.values(d.context).every(s=>text(s,160)) || !text(d.source,500) || !text(d.model,500) || !['REAL','SYNTHETIC'].includes(String(d.kind)))
    throw new Error('Deney alanları geçersiz.');
  if (!Array.isArray(d.rows) || d.rows.length < 1 || d.rows.length > 100 || !d.rows.every(r => object(r) && keys(r,['time','predicted','observed']) && Object.values(r).every(s=>text(s,40))))
    throw new Error('Ölçüm tablosu geçersiz; en fazla 100 satır desteklenir.');
  if (!Array.isArray(v.archived_reports) || !v.archived_reports.every(r=>object(r))) throw new Error('Rapor arşivi geçersiz.');
  // Archive content is retained, never trusted/rendered as current scientific output.
  return v as unknown as ExperimentFile;
}

export function serializeExperiment(draft: ExperimentDraft, reports: unknown[]): string {
  const raw = JSON.stringify({ format:'ceramic-experiment', version:1, saved_at:new Date().toISOString(), draft, archived_reports:reports }, null, 2);
  parseExperimentFile(raw);
  return raw;
}
