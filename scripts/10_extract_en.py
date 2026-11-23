"""kaikki English JSONL.gz → 작은 중간 파일(work/en_min.jsonl). 받은 자료는 믿지 않는 데이터: json 으로만 읽는다.
실행: python3 -I 10_extract_en.py <en.jsonl.gz> <out.jsonl>"""
import gzip, json, sys
src, dst = sys.argv[1], sys.argv[2]
POS_KEEP = None  # 모두 (name, phrase, prep_phrase, proverb 포함)
n = kept = 0
with gzip.open(src, 'rt', encoding='utf-8') as f, open(dst, 'w', encoding='utf-8') as o:
    for line in f:
        n += 1
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('lang_code') != 'en':
            continue
        w = d.get('word'); pos = d.get('pos')
        if not isinstance(w, str) or not isinstance(pos, str) or len(w) > 60:
            continue
        ko = []
        for t in d.get('translations', []) or []:
            if t.get('lang_code') == 'ko' and t.get('word'):
                ko.append({'s': t.get('sense') or '', 'w': t['word'], 'a': t.get('alt') or '', 't': t.get('tags') or []})
        senses = []
        for si, s in enumerate(d.get('senses', []) or []):
            for t in s.get('translations', []) or []:
                if t.get('lang_code') == 'ko' and t.get('word'):
                    g = (s.get('glosses') or [''])[-1]
                    ko.append({'s': t.get('sense') or g, 'w': t['word'], 'a': t.get('alt') or '', 't': t.get('tags') or [], 'si': si})
            if si < 12:
                gl = s.get('glosses') or []
                senses.append({'g': (gl[-1] if gl else '')[:200], 'tg': s.get('tags') or [],
                               'fo': [x.get('word') for x in (s.get('form_of') or []) + (s.get('alt_of') or []) if x.get('word')][:3],
                               'syn': [x.get('word') for x in (s.get('synonyms') or []) if x.get('word')][:5]})
        forms = [[x.get('form'), x.get('tags') or []] for x in (d.get('forms') or []) if x.get('form') and len(x.get('form')) < 60][:40]
        rec = {'w': w, 'p': pos, 'ko': ko, 'se': senses, 'fm': forms, 'en': d.get('etymology_number')}
        o.write(json.dumps(rec, ensure_ascii=False) + '\n')
        kept += 1
print('lines', n, 'kept', kept)
