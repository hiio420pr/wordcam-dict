"""다른 언어 → 한국어 사전(ja, zh, es, de). 한국어가 직접 있는 공개 자료가 적어서 네 갈래를 합친다(모두 CC BY-SA 위키낱말사전):
  ① kow : ko.wiktionary 의 그 언어 표제어(한국어 뜻풀이 직접)
  ② nat : 그 언어 위키낱말사전(de/es/ja/zh.wiktionary) 번역표의 한국어
  ③ piv : en.wiktionary 의 그 언어 표제어 영어 뜻풀이 → 우리 영한 사전(en-ko) + 한국어 표제어 거꾸로 색인
  ④ 한자 보너스(ja·zh): 그 낱말 한자(구자체·번체) = 한국어 표제어 한자이고, ③ 후보에 이미 있으면 점수 더함(한자 착각을 막으려 혼자서는 넣지 않음)
뜻 묶음 순서 = en.wiktionary 뜻 순서(③), 그 다음 ②·① 에만 있는 뜻.
실행: python3 -I 40_build_x.py <lang> <work_dir> <kowikt.gz> <out_dir>"""
import sys, os, json, gzip, re, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clean_ko, split_gloss, short_label, BAD_TAGS
L, work, kowikt, out = sys.argv[1:5]
POSMAP = {'prep_phrase': 'phrase', 'proverb': 'phrase', 'contraction': 'phrase', 'abbrev': 'noun', 'counter': 'noun', 'classifier': 'noun', 'character': 'noun'}
KEEP = {'noun', 'verb', 'adj', 'adv', 'name', 'phrase', 'intj', 'num', 'pron', 'det', 'prep', 'conj', 'particle', 'postp', 'suffix', 'prefix'}
MAXG = 8

# 영한 사전
EN = collections.defaultdict(lambda: collections.defaultdict(list))
for l in open(os.path.join(out, 'en-ko.senses.tsv'), encoding='utf-8'):
    w, p, i, lab, ko, src = l.rstrip('\n').split('\t')
    EN[w.lower()][p].append((lab.lower(), ko.split('|'), src))
# 한국어 표제어: 거꾸로 색인 + 한자 색인
KO2EN = {'noun': 'noun', 'verb': 'verb', 'adj': 'adj', 'adv': 'adv', 'intj': 'intj', 'num': 'num', 'pron': 'pron', 'phrase': 'phrase', 'det': 'det', 'name': 'name'}
rev = collections.defaultdict(list); hanja = collections.defaultdict(set)
for l in open(os.path.join(work, 'ko_min.jsonl'), encoding='utf-8'):
    d = json.loads(l)
    w = clean_ko(d['w'])
    if not w: continue
    for h in d['h']:
        hanja[h].add(w)
    if d['p'] not in KO2EN: continue
    for s in d['se']:
        if set(s['tg']) & BAD_TAGS or s['fo']: continue
        items = split_gloss(s['g'])
        for k, e in enumerate(items[:4]):
            rev[e].append((k, w, KO2EN[d['p']]))
kofreq = collections.Counter()
for w, ps in EN.items():
    for p, gs in ps.items():
        for g in gs:
            for k in g[1]: kofreq[k] += 1

def pos_ok(a, b):
    return a == b or {a, b} <= {'adj', 'verb'} or (a == 'phrase' and b == 'verb') or (a == 'name' and b == 'noun')

def pivot(gloss, p):
    """영어 뜻풀이 하나 → 한국어 후보 점수"""
    items = split_gloss(gloss)[:4]
    rest = set(re.findall(r'[a-z]+', gloss.lower()))
    sc = collections.Counter()
    for i, it in enumerate(items):
        wgt = 1.0 / (1 + 0.5 * i)
        ent = EN.get(it)
        if ent:
            gs = [g for pp, glist in ent.items() if pos_ok(p, pp) for g in glist] or [g for glist in ent.values() for g in glist][:2]
            if gs:
                # 뜻풀이 남은 낱말과 이름표가 가장 많이 겹치는 묶음, 같으면 앞 묶음
                best = max(range(len(gs)), key=lambda j: (len(rest & set(re.findall(r'[a-z]+', gs[j][0]))) - 0.01 * j))
                for r, k in enumerate(gs[best][1]):
                    sc[k] += wgt * (1.0 if r == 0 else 0.6)
                if best != 0:
                    sc[gs[0][1][0]] += wgt * 0.3
        for k, kw, kp in rev.get(it, []):
            if pos_ok(p, kp) and k <= 1:
                sc[kw] += wgt * (0.5 if k == 0 else 0.25) * min(1.0, 0.3 + math.log(kofreq[kw] + 1) / 3)
    return sc

# 그 언어 표기 바꾸기(한자 보너스): 일본어 구자체·중국어 번체는 en.wiktionary forms 에 있음
def hanja_forms(d):
    hs = {d['w']}
    for f, tg in d['fm']:
        if any(t in tg for t in ('kyūjitai', 'traditional', 'Traditional-Chinese', 'alternative', 'kanji')):
            hs.add(f)
    return hs

# ① ko.wiktionary
kow = collections.defaultdict(list)
with gzip.open(kowikt, 'rt', encoding='utf-8') as f:
    for line in f:
        if f'"lang_code": "{L}"' not in line: continue
        try: d = json.loads(line)
        except Exception: continue
        if d.get('lang_code') != L: continue
        p = POSMAP.get(d.get('pos'), d.get('pos'))
        for s in d.get('senses') or []:
            g = ((s.get('glosses') or [''])[-1])
            g = re.sub(r'\([^)]*\)', '', g)
            pieces = [clean_ko(x.strip(' .')) for x in re.split(r'[,;·]', g)]
            pieces = [x for x in pieces if x and len(x) <= 8]
            if pieces:
                kow[d['word']].append((p, pieces[:3], g.strip()[:60]))
# ② 그 언어 위키낱말사전
nat = collections.defaultdict(list)
fp = os.path.join(work, f'{L}wikt_ko.jsonl')
for l in open(fp, encoding='utf-8'):
    d = json.loads(l)
    p = POSMAP.get(d['p'], d['p'])
    for g in d['g']:
        kos = [k for k in (clean_ko(x.lstrip('^')) for x in g['ko']) if k]
        if kos:
            lab = ', '.join(g['en'][:3]) if g['en'] else (g['s'] or (d['gl'][0] if d['gl'] else ''))
            nat[d['w']].append((p, kos[:3], lab[:60]))

# ③ en.wiktionary 그 언어 표제어
entries = collections.OrderedDict(); forms = collections.defaultdict(set); redirect = {}
srcn = collections.Counter()
for l in open(os.path.join(work, f'{L}_min.jsonl'), encoding='utf-8'):
    d = json.loads(l)
    w, p = d['w'], POSMAP.get(d['p'], d['p'])
    if d['p'] == 'soft-redirect':
        for r in d.get('rd') or []: redirect[w] = r
        continue
    if p not in KEEP: continue
    hs = hanja_forms(d) if L in ('ja', 'zh') else set()
    hk = set().union(*[hanja.get(h, set()) for h in hs]) if hs else set()
    groups = entries.setdefault((w, p), [])
    for s in d['se']:
        if s['fo']:
            if not set(s['tg']) & {'obsolete', 'archaic', 'misspelling'}:
                forms[w].add(s['fo'][0])
            continue
        if set(s['tg']) & BAD_TAGS or not s['g']: continue
        sc = pivot(s['g'], p)
        for k in list(sc):
            if k in hk: sc[k] += 1.0
        top = [k for k, v in sc.most_common(3) if v >= 0.25]
        if not top: continue
        if any(top[0] in g[1][:1] for g in groups):  # 같은 큰 뜻이면 합침
            continue
        groups.append([short_label(s['g']), top, 'piv'])
    for f, tg in d['fm']:
        if f != w and not set(tg) & {'romanization', 'canonical', 'obsolete', 'archaic'} and len(f) <= 30:
            forms[f].add(w)

# ②·① 합치기: 같은 품사 묶음에 같은 한국어가 있으면 그 묶음을 앞으로(신뢰↑), 없으면 뒤에 더함
allw = set(w for w, _ in entries) | set(nat) | set(kow)
for w in allw:
    for srcname, lst in (('nat', nat.get(w, [])), ('kow', kow.get(w, []))):
        for p, kos, lab in lst:
            p = p if p in KEEP else 'noun'
            gs = entries.setdefault((w, p), [])
            hit = next((g for g in gs if set(g[1]) & set(kos)), None)
            if hit:
                if srcname not in hit[2]: hit[2] += '+' + srcname
                for k in kos:
                    if k not in hit[1] and len(hit[1]) < 3: hit[1].append(k)
            else:
                gs.append([short_label(lab), kos[:3], srcname])
# 한국어가 두 갈래 이상에서 확인된 묶음(piv+nat 등)을 그 품사 안에서 맨 앞으로? → 순서는 en.wiktionary 를 따르고, 첫 묶음이 piv 혼자이고
# 뒤에 확인된 묶음이 있으면 확인된 것을 앞으로 올린다
for key, gs in entries.items():
    if len(gs) > 1 and '+' not in gs[0][2] and gs[0][2] == 'piv':
        j = next((i for i, g in enumerate(gs[:4]) if '+' in g[2]), None)
        if j: gs.insert(0, gs.pop(j))
    entries[key] = gs[:MAXG]

hw = set()
with open(os.path.join(out, f'{L}-ko.senses.tsv'), 'w', encoding='utf-8') as o:
    for (w, p), gs in entries.items():
        if not gs: continue
        hw.add(w)
        for i, (lab, kos, src) in enumerate(gs):
            o.write(f"{w}\t{p}\t{i}\t{lab}\t{'|'.join(kos)}\t{src}\n"); srcn[src.split('+')[0]] += 1
nf = 0
with open(os.path.join(out, f'{L}-ko.forms.tsv'), 'w', encoding='utf-8') as o:
    for f, r in redirect.items():
        if r in hw and f not in hw: o.write(f"{f}\t{r}\n"); nf += 1
    for f, ls in forms.items():
        ls = [x for x in ls if x in hw and x != f]
        if ls and f not in redirect: o.write(f"{f}\t{'|'.join(sorted(ls)[:3])}\n"); nf += 1
print(L, 'headwords', len(hw), 'sense groups by first source', dict(srcn), 'forms', nf)
