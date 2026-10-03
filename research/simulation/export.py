"""Derived JSON/VTK/offline HTML; original solver fields are never overwritten."""
import html
import json
from pathlib import Path
import numpy as np
import plotly.graph_objects as go


def write_vtk(path, domain, temperature, mechanics):
    """Legacy ASCII unstructured tetrahedral VTK, readable by ParaView."""
    p, t = domain.mesh.p.T, domain.mesh.t.T
    lines = ["# vtk DataFile Version 3.0", "SYNTHETIC linear thermoelastic research", "ASCII", "DATASET UNSTRUCTURED_GRID", f"POINTS {len(p)} double"]
    lines += [" ".join(map(str, row)) for row in p]
    lines += [f"CELLS {len(t)} {5 * len(t)}"]
    lines += ["4 " + " ".join(map(str, row)) for row in t]
    lines += [f"CELL_TYPES {len(t)}"] + ["10"] * len(t)
    lines += [f"POINT_DATA {len(p)}", "SCALARS temperature_degC double 1", "LOOKUP_TABLE default"]
    lines += [str(v) for v in temperature]
    lines += ["VECTORS displacement_m double"]
    lines += [" ".join(map(str, row)) for row in mechanics["displacement_m"]]
    lines += [f"CELL_DATA {len(t)}", "SCALARS material_id int 1", "LOOKUP_TABLE default"]
    lines += [str(v) for v in domain.region]
    lines += ["TENSORS stress_Pa double"]
    for tensor in mechanics["cell_stress_pa"]:
        lines += [" ".join(map(str, row)) for row in tensor]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_viewer(path, case, domain, temperature, mechanics, report):
    mesh = domain.mesh
    facets = mesh.boundary_facets()
    triangles = mesh.facets[:, facets]
    owners = mesh.f2t[0, facets]
    points = mesh.p.T * 1000
    displacement = mechanics["displacement_m"]
    # A viewer-only multiplier: physical quantities remain unscaled in exports.
    scale = 50.0
    deformed = points + scale * displacement * 1000
    stress = mechanics["cell_max_principal_pa"][owners] / 1e6
    base = dict(i=triangles[0], j=triangles[1], k=triangles[2], flatshading=True,
                lighting=dict(ambient=.8, diffuse=.5), showscale=True)
    traces = [
        go.Mesh3d(x=points[:, 0], y=points[:, 1], z=points[:, 2], intensity=domain.region[owners], intensitymode="cell", colorscale=[[0,"#8dbaa9"],[1,"#e7b566"]], cmin=0,cmax=1, colorbar=dict(title="Katman",tickvals=[0,1],ticktext=["Bünye","Sır"]), name="Katmanlar", **base),
        go.Mesh3d(x=points[:, 0], y=points[:, 1], z=points[:, 2], intensity=temperature, intensitymode="vertex", colorscale="Thermal", visible=False, colorbar=dict(title="°C"), name="Sıcaklık", **base),
        go.Mesh3d(x=deformed[:, 0], y=deformed[:, 1], z=deformed[:, 2], intensity=stress, intensitymode="cell", colorscale="RdBu_r", visible=False, colorbar=dict(title="σ₁ / MPa"), name="Gerilme", **base),
        go.Mesh3d(x=deformed[:, 0], y=deformed[:, 1], z=deformed[:, 2], intensity=np.linalg.norm(displacement,axis=1)*1e6, intensitymode="vertex", colorscale="Viridis", visible=False, colorbar=dict(title="|u| / µm"), name="Yer değiştirme", **base),
    ]
    titles = ["Katmanlar · orijinal geometri", "Sıcaklık · orijinal geometri", "En büyük asal gerilme · şekil değişimi ×50", "Yer değiştirme · şekil değişimi ×50"]
    fig = go.Figure(traces)
    fig.update_layout(template="plotly_dark", paper_bgcolor="#101d22", plot_bgcolor="#101d22", margin=dict(l=0,r=30,t=85,b=0), height=580,
        title=titles[0], scene=dict(aspectmode="data", xaxis_title="x / mm",yaxis_title="y / mm",zaxis_title="z / mm"),
        updatemenus=[dict(type="dropdown", x=0, y=1.08, buttons=[dict(label=title,method="update",args=[{"visible":[i==j for j in range(4)]},{"title":title}]) for i,title in enumerate(titles)])])
    fragment = fig.to_html(full_html=False, include_plotlyjs=True, config={"responsive":True,"displaylogo":False}, div_id="simulation-3d")
    safe_case = html.escape(case["case_id"])
    safe_report = html.escape(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    page = f'''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ceramic Lab · 3B araştırma</title>
<style>body{{background:#101d22;color:#e8eeea;font:16px/1.6 system-ui;margin:0}}main{{max-width:1180px;margin:auto;padding:28px}}h1{{font-size:clamp(24px,4vw,38px);margin:6px 0}}.eyebrow{{color:#8dbaa9;letter-spacing:.18em;font-size:12px}}.warning{{border-left:4px solid #e7b566;background:#243039;padding:14px 18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:20px 0}}.card{{padding:16px;border:1px solid #385058;border-radius:8px}}small{{color:#b9c9c9}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}}a{{color:#8dbaa9}}</style><main>
<div class="eyebrow">CERAMIC MATERIAL INTELLIGENCE · RESEARCH 0.1</div><h1>Sır–bünye / 3B termoelastik deney</h1>
<p>{safe_case} · PREDICTED / DETERMINISTIC / SYNTHETIC</p>
<div class="warning">Sentetik malzemeler. Pişmiş katı idealizasyonu; gerçek reçete veya pişirim tahmini değildir. Ham çamur, erime, reaksiyonlar, sinterleme ve çatlama olasılığı bu modelde çözülmüyor. Ağ bağımsızlığı henüz gösterilmedi; fiziksel doğrulama yapılmadı.</div>
<div class="grid"><div class="card"><small>Ağ</small><br>{mesh.nvertices} düğüm / {mesh.nelements} tetrahedron</div><div class="card"><small>Sıcaklık / gerilmesiz referans</small><br>{temperature.min():.1f}–{temperature.max():.1f} °C / {case['thermal']['reference_c']:.1f} °C</div><div class="card"><small>En büyük yer değiştirme</small><br>{mechanics['diagnostics']['max_displacement_m']*1e6:.3f} µm</div></div>
<p>Modeli fareyle veya dokunarak döndürebilirsin. Görünümü grafiğin üstündeki menüden değiştir. Gerilme renkleri hücre ortalamalarıdır; pozitif değer çekmedir, kırılma ölçütü değildir.</p>
{fragment}<p><small>Gerilme ve yer değiştirme görünümlerinde deformasyon 50 kat büyütülür; renk skalası gerçek hesap değerini gösterir. Üç referans noktası yalnızca rijit cisim hareketini kaldırır. Serbest kenarlardaki tepe gerilmeler ağdan etkilenebilir.</small></p>
<details><summary>Varsayımlar, girdiler ve sayısal kontroller</summary><pre>{safe_report}</pre></details>
<p><a href="result.json">Hesap raporu (JSON)</a> · <a href="fields.vtk">3B alanlar (VTK / ParaView)</a></p>
<small>Hesap Python/FEM motorunda yapıldı. HTML yalnızca sonuç görüntüleyicisidir; reçete düzenleyici değildir. İnternet veya NVIDIA hesabı gerektirmez.</small></main></html>'''
    path.write_text(page, encoding="utf-8")
