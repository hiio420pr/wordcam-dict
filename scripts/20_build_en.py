"""영한 사전 만들기: work/en_min.jsonl + work/ko_min.jsonl → out/en-ko.senses.tsv, out/en-ko.forms.tsv
뜻 묶음 = en.wiktionary 번역표(한국어) 묶음, 순서는 번역표 순서. 번역표가 없거나 그 품사가 없으면
en.wiktionary 한국어 표제어의 영어 뜻풀이를 거꾸로 찾아(그 영어 낱말이 뜻풀이 첫머리 쪽에 있는 한국어 낱말) 채운다(src=rev).
실행: python3 -I 20_build_en.py <work_dir> <out_dir>"""
import sys, json, collections, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clean_ko, split_gloss, short_label, BAD_TAGS
work, out = sys.argv[1], sys.argv[2]
KEEP_POS = {'noun', 'verb', 'adj', 'adv', 'name', 'phrase', 'prep_phrase', 'intj', 'num', 'pron', 'det', 'prep', 'conj', 'proverb', 'particle', 'contraction'}
POSMAP = {'prep_phrase': 'phrase', 'proverb': 'phrase', 'contraction': 'phrase'}
KO2EN = {'noun': 'noun', 'verb': 'verb', 'adj': 'adj', 'adv': 'adv', 'intj': 'intj', 'num': 'num', 'pron': 'pron', 'phrase': 'phrase', 'det': 'det', 'name': 'name'}
FORM_TAGS = {'plural', 'past', 'participle', 'present', 'third-person', 'comparative', 'superlative', 'gerund'}
MAXG, MAXKO = 8, 3

# 1) 한국어 표제어 거꾸로 색인: 영어 구 → [(자리, 한국어, 품사, 영어 뜻풀이)]
rev = collections.defaultdict(list)
for l in open(os.path.join(work, 'ko_min.jsonl'), encoding='utf-8'):
    d = json.loads(l)
    w = clean_ko(d['w'])
    if not w or d['p'] not in KO2EN: continue
    for s in d['se']:
        if set(s['tg']) & BAD_TAGS or s['fo']: continue
        items = split_gloss(s['g'])
        for k, e in enumerate(items):
            rev[e].append((k, len(items), w, KO2EN[d['p']], s['g']))

# 한국어 낱말 흔함 정도: en.wiktionary 번역표 전체에 한국어 낱말이 몇 번 나오나(자료 안 빈도 대용)
kofreq = collections.Counter()
for l in open(os.path.join(work, 'en_min.jsonl'), encoding='utf-8'):
    if '"ko": []' in l: continue
    d = json.loads(l)
    for t in d['ko']:
        k = clean_ko(t['w'])
        if k: kofreq[k] += 1
import math
def rscore(c):
    k, n, kw, kp, gl = c
    return -(math.log(kofreq[kw] + 1) * 1.0 - 0.8 * k - 0.15 * n)

# 2) 영어 표제어
entries = collections.OrderedDict()   # (hw,pos) → list of [label, [ko]]
lemmas = set(); forms = collections.defaultdict(list); is_form_only = set()
for l in open(os.path.join(work, 'en_min.jsonl'), encoding='utf-8'):
    d = json.loads(l)
    w, p = d['w'], d['p']
    if p not in KEEP_POS: continue
    p = POSMAP.get(p, p)
    real = [s for s in d['se'] if not s['fo']]
    fo = [s for s in d['se'] if s['fo'] and ('form-of' in s['tg'] or 'alt-of' in s['tg'] or 'alternative' in s['g'].lower() or 'spelling of' in s['g'].lower())]
    for s in fo:
        if set(s['tg']) & FORM_TAGS or 'alt-of' in s['tg'] or any(x in s['g'] for x in ('plural', 'past', 'participle', 'spelling of', 'alternative form', 'comparative', 'superlative', 'present')):
            if not (set(s['tg']) & {'obsolete', 'archaic', 'nonstandard', 'misspelling', 'dialectal', 'rare'}):
                forms[w].append(s['fo'][0])
    if real: lemmas.add((w, p))
    for f, tags in d['fm']:
        if set(tags) & FORM_TAGS and not set(tags) & {'obsolete', 'archaic', 'nonstandard', 'rare', 'dialectal'} and f != w and ' ' not in f.replace(w, ''):
            forms[f].append(w)
    groups = entries.setdefault((w, p), [])
    for t in d['ko']:
        if set(t['t']) & BAD_TAGS: continue
        k = clean_ko(t['w'])
        if not k: continue
        lab = short_label(re.sub(r'^\(.*?\)\s*', '', t['s'] or (real[0]['g'] if real else '')))
        g = next((g for g in groups if g[0] == lab), None)
        if g is None:
            g = [lab, [], 'wikt']; groups.append(g)
        if k not in g[1] and len(g[1]) < MAXKO: g[1].append(k)

# 같은 한국어 묶음 합치기, 빈 것 지우기
for key, groups in list(entries.items()):
    seen = []; ng = []
    for g in groups:
        s = tuple(sorted(g[1]))
        if not s or s in seen: continue
        # 앞 묶음과 첫 한국어가 같으면 합침
        prev = next((x for x in ng if x[1][0] == g[1][0]), None)
        if prev:
            for k in g[1]:
                if k not in prev[1] and len(prev[1]) < MAXKO: prev[1].append(k)
            continue
        seen.append(s); ng.append(g)
    entries[key] = ng[:MAXG]

# 3) 거꾸로 색인으로 채우기/더하기
#    - 그 품사에 번역표 묶음이 없으면: 같은 품사 한국어(없으면 다른 품사도) 최대 4묶음
#    - 번역표 묶음이 있어도: 뜻풀이 첫머리(k==0)가 그 낱말인 흔한 한국어를 뒤에 최대 2묶음 더함(src=rev+)
added = extra = 0
lemma_words = collections.defaultdict(set)
for w, p in lemmas: lemma_words[w].add(p)
def rev_groups(w, p, have, limit, kmax, allow_other):
    cands = rev.get(w.lower()) or []
    same = [c for c in cands if c[3] == p or (p == 'phrase' and c[3] == 'verb') or (p == 'verb' and ' ' in w and c[3] in ('verb', 'adj')) or (p == 'adj' and c[3] == 'verb')]
    if not same and allow_other:
        same = [c for c in cands if c[3] in ('noun', 'verb', 'adj', 'adv')]
    groups = []
    for c in sorted(same, key=rscore):
        k, n, kw, kp, gl = c
        if k > kmax or kw in have or any(kw in g[1] for g in groups): continue
        groups.append([short_label(gl), [kw], 'rev'])
        if len(groups) >= limit: break
    return groups
REV_FILL_ONLY_EMPTY = os.environ.get('REV_V2') is not None   # 실험 v2(효과 없어 끔): 번역표가 하나도 없는 표제어만 채움(품사 빈칸 채우기 안 함)
for w, ps in lemma_words.items():
    if w.lower() not in rev: continue
    word_has_wikt = any(entries.get((w, q)) for q in ps)
    for p in ps:
        g0 = entries.get((w, p))
        if not g0:
            if REV_FILL_ONLY_EMPTY and word_has_wikt: continue
            gs = rev_groups(w, p, set(), 4, 2, not REV_FILL_ONLY_EMPTY)
            if gs: entries[(w, p)] = gs; added += 1
        else:
            have = {k for g in g0 for k in g[1]}
            gs = rev_groups(w, p, have, 2, 0, False)
            gs = [g for g in gs if kofreq[g[1][0]] >= 2]
            if gs:
                entries[(w, p)] = (g0 + gs)[:MAXG]; extra += 1
print('rev-filled', added, 'rev-extra', extra)

# 3b) 다른 언어 위키낱말사전 번역표에서 같은 뜻 묶음에 영어·한국어 번역이 같이 있는 것(en↔ko 짝, src=nat)
nat = collections.defaultdict(list)
for L in ('de', 'es', 'ja', 'zh'):
    fp = os.path.join(work, f'{L}wikt_ko.jsonl')
    if not os.path.exists(fp): continue
    for l in open(fp, encoding='utf-8'):
        d = json.loads(l)
        for g in d['g']:
            kos = [k for k in (clean_ko(x) for x in g['ko']) if k]
            ens = [e.strip() for e in g['en'] if e and len(e) < 40]
            if not kos or not ens: continue
            for e in ens:
                nat[e].append((POSMAP.get(d['p'], d['p']), kos[:2], ', '.join(ens[:3]), L))
nadd = nex = 0
for w, ps in lemma_words.items():
    cs = nat.get(w)
    if not cs: continue
    for p in ps:
        same = [c for c in cs if c[0] == p]
        if not same: continue
        g0 = entries.get((w, p)) or []
        have = {k for g in g0 for k in g[1]}
        # 여러 언어 사전이 같은 한국어를 내면 앞으로
        cnt = collections.Counter(c[1][0] for c in same)
        gs = []
        for c in sorted(same, key=lambda c: -cnt[c[1][0]]):
            if c[1][0] in have or any(c[1][0] in g[1] for g in gs): continue
            gs.append([short_label(c[2]), c[1], 'nat'])
        if not gs: continue
        if not g0: entries[(w, p)] = gs[:4]; nadd += 1
        else: entries[(w, p)] = (g0 + gs[:2])[:MAXG]; nex += 1
print('nat-filled', nadd, 'nat-extra', nex)

# 3c) v2: 묶음 안 한국어는 흔한 것 먼저(번역표 전체에 나온 횟수, 같으면 원래 순서)
if os.environ.get('REV_V2') is not None:
    for key, groups in entries.items():
        for g in groups:
            g[1] = sorted(g[1], key=lambda k: -kofreq[k])

# 4) 쓰기
os.makedirs(out, exist_ok=True)
hw = set()
with open(os.path.join(out, 'en-ko.senses.tsv'), 'w', encoding='utf-8') as o:
    for (w, p), groups in entries.items():
        if not groups: continue
        hw.add(w)
        for i, (lab, ko, src) in enumerate(groups):
            o.write(f"{w}\t{p}\t{i}\t{lab}\t{'|'.join(ko)}\t{src}\n")
nf = 0
with open(os.path.join(out, 'en-ko.forms.tsv'), 'w', encoding='utf-8') as o:
    for f, ls in forms.items():
        ls2 = []
        for x in ls:
            if x in hw and x != f and x not in ls2: ls2.append(x)
        if ls2 and (f not in hw or True):
            o.write(f"{f}\t{'|'.join(ls2[:3])}\n"); nf += 1
print('headwords', len(hw), 'entries', sum(1 for v in entries.values() if v), 'forms', nf)
