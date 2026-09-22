"""Pure, framework-independent process checks. All temperatures are Celsius.

Reported firing windows are not measured heatwork or a glaze-fit model.
Even complete context does not turn evidence requirements into predictions.
"""
from copy import deepcopy
import hashlib
import json
import math

VERSION = 'process-assessment/1.0.0'


class ProcessInputError(ValueError):
    pass


def number(value, path, low=0, high=1800):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ProcessInputError(f'INVALID_NUMBER:{path}')
    return float(value)


def firing_window(window, peak_c):
    """Compare a declared peak with a sourced, reported product interval only."""
    if window is None:
        return {'status': 'UNAVAILABLE', 'code': 'NO_REPORTED_WINDOW', 'source_ref': None}
    for key in ('product_id', 'source_ref', 'conditions'):
        if not isinstance(window.get(key), str) or not window[key].strip():
            raise ProcessInputError(f'MISSING_WINDOW_METADATA:{key}')
    low = number(window.get('min_c'), 'min_c')
    high = number(window.get('max_c'), 'max_c')
    if low > high:
        raise ProcessInputError('INVERTED_WINDOW')
    if peak_c is None:
        return {'status': 'UNAVAILABLE', 'code': 'NO_PEAK_TEMPERATURE', 'source_ref': window['source_ref']}
    peak = number(peak_c, 'peak_c')
    code = 'BELOW_REPORTED_WINDOW' if peak < low else 'ABOVE_REPORTED_WINDOW' if peak > high else 'WITHIN_REPORTED_WINDOW'
    return {'status': 'AVAILABLE', 'code': code, 'source_ref': window['source_ref']}


def schedule_duration(schedule):
    """Sum abs(delta T)/rate + hold for a declared plan, never actual heatwork."""
    if schedule is None:
        return {'status': 'UNAVAILABLE', 'known_duration_minutes': None, 'total_duration_minutes': None,
                'peak_c': None, 'code': 'NO_SCHEDULE'}
    current = number(schedule.get('start_c'), 'start_c')
    peak = current
    segments = schedule.get('segments')
    if not isinstance(segments, list) or not 1 <= len(segments) <= 100:
        raise ProcessInputError('INVALID_SEGMENTS')
    minutes = 0.0
    partial = False
    for i, segment in enumerate(segments):
        target = number(segment.get('target_c'), f'segments.{i}.target_c')
        hold = number(segment.get('hold_minutes', 0), f'segments.{i}.hold_minutes', high=10080)
        rate = segment.get('rate_c_per_hour')
        if rate is None:
            # Uncontrolled/natural cooling has unknown duration, not zero.
            if target >= current:
                raise ProcessInputError('NATURAL_COOLING_MUST_DESCEND')
            partial = True
        else:
            rate = number(rate, f'segments.{i}.rate_c_per_hour', low=0.01, high=10000)
            minutes += abs(target - current) / rate * 60
        minutes += hold
        peak = max(peak, target)
        current = target
    return {'status': 'PARTIAL' if partial else 'AVAILABLE', 'known_duration_minutes': minutes,
            'total_duration_minutes': None if partial else minutes, 'peak_c': peak,
            'code': 'UNCONTROLLED_COOLING_DURATION_UNKNOWN' if partial else 'PLANNED_DURATION_ONLY'}


STAGES = (
    ('application', 'Uygulama ve kuruma',
     'Ham sır tabakasının bisküvi yüzeyine bağlanması; pişmiş sırın dayanımıyla aynı ölçüm değildir.',
     ['Bisküvi su emmesi ve yüzey durumu', 'Süspansiyon/reoloji ve bağlayıcı bilgisi', 'Uygulama kalınlığı ve kuruma gözlemi'],
     'Aynı bünyede kontrollü kalınlıklarla uygulama ve kuruma gözlemlerini kaydet.'),
    ('interface', 'Pişirimde ıslanma ve arayüz',
     'Sır eriyiği ile bünyenin teması; yalnızca element listesiyle bağlanma kuvveti hesaplanamaz.',
     ['Sıcaklığa bağlı eriyik davranışı/ıslanma ölçümü', 'Bünye ve sır ürün/analiz sürümleri', 'Gerçek sıcaklık–zaman ve atmosfer kaydı'],
     'Eşlenmiş test numunesi ve gerekirse kesit/arayüz incelemesiyle değerlendirilir.'),
    ('fit', 'Soğuma sonrası sır–bünye uyumu',
     'Çatlama ve kavlama, uygulama tutunmasından ayrı değerlendirilir.',
     ['Uyumlu koşullarda ölçülmüş genleşme eğrileri', 'Kalınlık, geometri ve gerilme gevşemesi', 'İlk ve gecikmiş çatlama/kavlama gözlemleri'],
     'Sır–bünye çiftini gerçek pişirimlerde karşılaştır; tek CTE farkını çatlama yüzdesi sayma.'),
    ('surface', 'Matlık, parlaklık ve kristaller',
     'UMF tek başına son yüzeyi belirlemez; bu sürüm bir yüzey olasılığı modeli içermiyor.',
     ['Reçete/analiz ve uygulama kalınlığı', 'Gerçek tepe, bekleme ve soğuma kaydı', 'Eşlenmiş yüzey gözlemleri veya parlaklık ölçümleri'],
     'Aynı reçeteyi kontrollü kalınlık ve soğuma değişkenleriyle ayrı numuneler olarak kaydet.'),
    ('color', 'Renk ve atmosfer',
     'Renklendirici miktarı, kimyasal durumu ve yapı birlikte önemlidir; fotoğraf gerçek renk ölçümü değildir.',
     ['Renklendiriciler ve atmosfer geçmişi', 'Bünye rengi ve sır kalınlığı', 'Kalibre renk ölçümü veya kontrollü çekim'],
     'Isıtma ve soğuma atmosferlerini ayrı kaydet; renk çıkarımını çalışma kapsamıyla sınırla.'),
    ('body', 'Bünyenin olgunlaşması ve dayanımı',
     'Beyaz stoneware adı tek başına küçülme, porozite veya dayanım modeli tanımlamaz.',
     ['Ürün/lot, mineralojik ve tane boyutu bilgisi', 'Pişirim koşuluna bağlı emme/küçülme ölçümleri', 'Tanımlı yöntemle mekanik ölçüm'],
     'Üretici özelliklerini yalnızca belirtildikleri pişirim ve deney koşullarıyla karşılaştır.'),
)


def assess_process(context):
    """Input is a resolved JSON-compatible snapshot; no I/O, no hidden defaults."""
    context = deepcopy(context)
    peak = context.get('temperature_c')
    if peak is not None:
        number(peak, 'temperature_c')
    duration = schedule_duration(context.get('schedule'))
    body = firing_window(context.get('body_window'), peak)
    glaze = firing_window(context.get('glaze_window'), peak)
    warnings = ['Aralık içinde olmak tutunma, olgunlaşma, güvenlik veya başarılı yüzey garantisi değildir.',
                'Cone sabit bir °C değeri değildir. Bu kontrol heatwork eşdeğerliği hesaplamaz.',
                'Fırın markası tek başına sonuç belirlemez; gerçek program, yük, konum ve ölçümler gerekir.']
    if peak is not None and duration['peak_c'] is not None and not math.isclose(peak, duration['peak_c'], abs_tol=0.01):
        warnings.append('Bildirilen tepe sıcaklığı ile programın tepe sıcaklığı farklı; değerler sessizce birleştirilmedi.')
    stages = [{'id': id_, 'title': title, 'status': 'UNAVAILABLE', 'evidence_kind': 'PREDICTED',
               'probability': None, 'reason': reason, 'required_evidence': required, 'next_step': next_step}
              for id_, title, reason, required, next_step in STAGES]
    encoded = json.dumps({'version': VERSION, 'input': context}, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    return {'engine_version': VERSION, 'input_hash': hashlib.sha256(encoded).hexdigest(),
            'input_snapshot': context, 'status': 'PARTIAL',
            'checks_evidence_kind': 'CALCULATED', 'checks_method_kind': 'DETERMINISTIC',
            'checks_qualifier': 'COMPARISON_OF_REPORTED_INPUTS_NOT_PHYSICAL_VALIDATION',
            'body_window': body, 'glaze_window': glaze, 'schedule': duration,
            'stages': stages, 'warnings': warnings,
            'limitations': ['No calibrated outcome model or matched specimen database is connected.',
                            'No gas, energy, phase or stress coupling is performed by this module.']}
