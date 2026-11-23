"""kaikki Korean(en.wiktionary 한국어 표제어) → work/ko_min.jsonl : 낱말, 품사, 영어 뜻풀이들, 한자. 실행: python3 -I 11_extract_ko.py <ko.jsonl.gz> <out>"""
import gzip, json, sys
src, dst = sys.argv[1], sys.argv[2]
n = 0
with gzip.open(src, 'rt', encoding='utf-8') as f, open(dst, 'w', encoding='utf-8') as o:
    for line in f:
        try: d = json.loads(line)
        except Exception: continue
        if d.get('lang_code') != 'ko': continue
        w = d.get('word'); p = d.get('pos')
        if not isinstance(w, str): continue
        han = [x['form'] for x in d.get('forms') or [] if 'hanja' in (x.get('tags') or []) and x.get('form')]
        for ht in d.get('head_templates') or []:
            h = (ht.get('args') or {}).get('hanja')
            if h and h not in han: han.append(h)
        se = []
        for s in d.get('senses') or []:
            gl = s.get('glosses') or []
            tags = s.get('tags') or []
            fo = [x.get('word') for x in (s.get('form_of') or []) + (s.get('alt_of') or []) if x.get('word')]
            se.append({'g': (gl[-1] if gl else '')[:200], 'tg': tags, 'fo': fo[:2], 'nex': len(s.get('examples') or [])})
        cats = [c.get('name', '') for c in d.get('categories') or [] if isinstance(c, dict)]
        basic = any('basic' in c.lower() or 'beginner' in c.lower() or 'intermediate' in c.lower() for c in cats)
        o.write(json.dumps({'w': w, 'p': p, 'h': han, 'se': se, 'b': basic}, ensure_ascii=False) + '\n'); n += 1
print('kept', n)
