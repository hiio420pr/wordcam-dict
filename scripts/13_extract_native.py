"""각 언어 위키낱말사전(de/es/ja/zh.wiktionary, kaikki 추출본) → 그 언어 표제어 중 한국어 번역이 있는 것:
낱말, 품사, 뜻 묶음별 한국어·영어 번역. 실행: python3 -I 13_extract_native.py <lang> <in.gz> <out.jsonl>"""
import gzip, json, sys
lc, src, dst = sys.argv[1:4]
n = 0
with gzip.open(src, 'rt', encoding='utf-8') as f, open(dst, 'w', encoding='utf-8') as o:
    for line in f:
        if '"ko"' not in line: continue
        try: d = json.loads(line)
        except Exception: continue
        if d.get('lang_code') != lc: continue
        trs = list(d.get('translations') or [])
        for s in d.get('senses') or []: trs += s.get('translations') or []
        groups = {}
        for t in trs:
            if t.get('lang_code') not in ('ko', 'en') or not t.get('word'): continue
            key = str(t.get('sense_index') or t.get('sense') or '')
            g = groups.setdefault(key, {'s': t.get('sense') or '', 'ko': [], 'en': []})
            g[t['lang_code']].append(t['word'])
        groups = [g for g in groups.values() if g['ko']]
        if not groups: continue
        gl = [((s.get('glosses') or [''])[-1])[:120] for s in (d.get('senses') or [])[:8]]
        o.write(json.dumps({'w': d.get('word'), 'p': d.get('pos'), 'g': groups, 'gl': gl}, ensure_ascii=False) + '\n'); n += 1
print(lc, n)
