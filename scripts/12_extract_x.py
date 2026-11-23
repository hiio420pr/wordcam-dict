"""kaikki en.wiktionary 의 다른 언어(ja, zh, es, de) 사전 → work/<lang>_min.jsonl (낱말, 품사, 영어 뜻풀이, 꼴, 다른 표기). 
실행: python3 -I 12_extract_x.py <lang_code> <in.jsonl.gz> <out.jsonl>"""
import gzip, json, sys
lc, src, dst = sys.argv[1:4]
n = 0
with gzip.open(src, 'rt', encoding='utf-8') as f, open(dst, 'w', encoding='utf-8') as o:
    for line in f:
        try: d = json.loads(line)
        except Exception: continue
        if d.get('lang_code') != lc: continue
        w = d.get('word'); p = d.get('pos')
        if not isinstance(w, str) or len(w) > 40: continue
        se = []
        for s in (d.get('senses') or [])[:12]:
            gl = s.get('glosses') or []
            fo = [x.get('word') for x in (s.get('form_of') or []) + (s.get('alt_of') or []) if x.get('word')]
            se.append({'g': (gl[-1] if gl else '')[:200], 'tg': s.get('tags') or [], 'fo': fo[:2]})
        fm = []
        for x in d.get('forms') or []:
            fx = x.get('form')
            tg = x.get('tags') or []
            if fx and len(fx) < 40 and 'romanization' not in tg and 'table-tags' not in tg and 'inflection-template' not in tg:
                fm.append([fx, tg])
        o.write(json.dumps({'w': w, 'p': p, 'se': se, 'fm': fm[:250], 'rd': (d.get('redirects') or [])[:3]}, ensure_ascii=False) + '\n'); n += 1
print(lc, 'kept', n)
