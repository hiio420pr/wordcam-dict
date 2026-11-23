"""빠른 점검(파이썬, 모델 없음): 시험 문제 base 꼴을 사전에서 찾을 수 있나, 정답이 카드(앞 4묶음) 안에 있나, 첫 묶음 첫 낱말이 맞나(품사는 category 로 근사).
실행: python3 -I 30_quick_eval.py <senses.tsv> <forms.tsv> <testset.csv> [miss_out.tsv]"""
import sys, csv, collections, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade_lib import match
sen, frm, ts = sys.argv[1:4]
D = collections.defaultdict(lambda: collections.OrderedDict())
for l in open(sen, encoding='utf-8'):
    w, p, i, lab, ko, src = l.rstrip('\n').split('\t')
    D[w].setdefault(p, []).append((lab, ko.split('|'), src))
F = collections.defaultdict(list)
for l in open(frm, encoding='utf-8'):
    f, ls = l.rstrip('\n').split('\t'); F[f] = ls.split('|')
def lemmas(tok):
    out = [tok]
    for t in (tok, tok.lower()):
        if t not in out: out.append(t)
        out += [x for x in F.get(t, []) if x not in out]
    return out
def lookup(target):
    toks = target.replace(' ... ', ' ').replace('...', ' ').split()
    keys = []
    if len(toks) == 1:
        keys = lemmas(toks[0])
    else:
        for l0 in lemmas(toks[0]):
            keys.append(' '.join([l0] + toks[1:]))
            keys.append(' '.join([l0] + [t.lower() for t in toks[1:]]))
    for k in keys:
        if k in D: return k, D[k]
    # 재귀·전치사 붙은 꼴: 'sich freuen auf' → 'sich freuen' → 'freuen', 'acordarse de' → 'acordarse' → 'acordar'
    t = re.sub(r'\s*\+.*$', '', target).strip()
    cands = [t]
    toks = t.split()
    if len(toks) > 1: cands.append(' '.join(toks[:-1]))
    for c in list(cands):
        if c.startswith('sich '): cands += [c[5:], c[5:].split()[0]] if c[5:] else []
        if re.search(r'(arse|erse|irse)( |$)', c): cands.append(re.sub(r'se( |$)', r'\1', c, count=1).strip())
    for c in cands:
        if c in D: return c, D[c]
        for x in F.get(c, []):
            if x in D: return x, D[x]
    return None, None
POSC = {'noun': 'noun', 'verb': 'verb', 'adj': 'adj', 'adv': 'adv', 'phrasal_verb': 'verb'}
rows = list(csv.DictReader(open(ts, encoding='utf-8')))
st = collections.Counter(); miss = []
for r in rows:
    g = r['set'] + '/' + r['category']
    acc = r['acceptable_ko'].split('|'); wrong = [x for x in r['wrong_but_plausible_ko'].split('|') if x]
    k, e = lookup(r['target_as_appears'] if r['lang'] == 'en' else r['base_form'])
    if e is None: k, e = lookup(r['base_form'])
    st[g, 'n'] += 1; st[r['set'], 'n'] += 1
    if not e:
        miss.append((r['id'], r['base_form'], 'NOENTRY', '')); continue
    st[g, 'found'] += 1; st[r['set'], 'found'] += 1
    p = POSC.get(r['category'])
    order = ([p] if p in e else []) + [x for x in e if x != p]
    groups = [gg for x in order for gg in e[x]]
    card = groups[:4] if True else groups
    inall = any(match(kw, acc) for gg in groups for kw in gg[1])
    incard = any(match(kw, acc) for gg in card for kw in gg[1])
    first = match(groups[0][1][0], acc) and not (wrong and match(groups[0][1][0], wrong))
    for name, v in (('all', inall), ('card', incard), ('first', first)):
        st[g, name] += v; st[r['set'], name] += v
    if not inall: miss.append((r['id'], r['base_form'], 'NOTIN', ' / '.join('|'.join(gg[1]) for gg in groups[:6])))
print(f"{'group':28s} n found first card4 any")
for key in sorted({k[0] for k in st}):
    print(f"{key:28s} {st[key,'n']:3d} {st[key,'found']:4d} {st[key,'first']:4d} {st[key,'card']:4d} {st[key,'all']:4d}")
if len(sys.argv) > 4:
    with open(sys.argv[4], 'w', encoding='utf-8') as o:
        for m in miss: o.write('\t'.join(m) + '\n')
