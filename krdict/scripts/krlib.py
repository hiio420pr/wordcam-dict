"""한국어기초사전 거꾸로 찾기 공용: 읽기·순위 매기기·원형 찾기."""
import csv, sqlite3, json, collections

POSC = {'명사': 'n', '대명사': 'n', '의존 명사': 'n', '수사': 'n', '동사': 'v', '보조 동사': 'v',
        '형용사': 'a', '보조 형용사': 'a', '관형사': 'a', '부사': 'd', '감탄사': 'i'}


def load(tsv):
    """key → [row dict]"""
    idx = collections.defaultdict(list)
    with open(tsv, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            for k in ('lvl', 'sn', 'pi', 'np', 'kind'):
                r[k] = int(r[k])
            r['pc'] = POSC.get(r['pos'], 'o')
            idx[r['key']].append(r)
    return idx


def rank_key(r, variant='level'):
    """작을수록 앞. level: 초급>중급>고급 먼저 / exact: 대역어 칸에 이 말 하나뿐인 것 먼저"""
    unit = 0 if r['unit'] == '단어' else 1
    exact = 0 if (r['np'] == 1) else (1 if r['pi'] == 0 else 2)
    if variant == 'score':      # 한 줄 점수: 수준 1점/단계, 뜻 번호 2.5점/번(최대 4), 조각 자리 0.5, 조각 여럿 0.5
        sc = r['lvl'] + 2.5 * min(r['sn'] - 1, 4) + 0.5 * min(r['pi'], 4) + 0.5 * (r['np'] > 1)
        return (unit, r['kind'] > 0, sc, r['sn'], r['pi'])
    if variant == 'exact':
        return (unit, r['kind'] > 0, exact, r['sn'] > 1, r['lvl'], r['sn'], r['pi'])
    if variant == 'first':      # 조각 순서·뜻 번호만(수준 안 씀) — 비교용
        return (unit, r['kind'] > 0, r['pi'], r['sn'], r['np'])
    return (unit, r['kind'] > 0, r['lvl'], exact, r['sn'], r['pi'])


def ranked(rows, variant='level'):
    """같은 한국어 표제어는 가장 좋은 줄 하나만 → [(ko, best_row)]"""
    best = {}
    for r in rows:
        k = r['rank'] if 'rank' in r else rank_key(r, variant)
        cur = best.get(r['ko'])
        if cur is None or k < cur[0]:
            best[r['ko']] = (k, r)
    return [(ko, r) for ko, (k, r) in sorted(best.items(), key=lambda x: x[1][0])]


# 원형 찾기: 1.2 위키 사전의 꼴 표(f)와 규칙(lemma_rules.json)을 그대로 씀 — 앱 WordDict.lookup 과 같은 순서
class Lemmatizer:
    def __init__(self, wikt_sqlite, rules_json, lang):
        self.db = sqlite3.connect(wikt_sqlite)
        self.lang = lang
        R = json.load(open(rules_json, encoding='utf-8')).get(lang, {})
        self.steps = R.get('steps', 1)
        self.rules = [tuple(x) for x in R.get('rules', []) if len(x) == 2]
        self.prefix = [tuple(x) for x in R.get('prefix_rules', []) if len(x) == 4]

    def forms(self, f):
        r = self.db.execute('select h from f where f=?', (f,)).fetchone()
        return r[0].split('|') if r else []

    def rule_forms(self, w):
        seen, frontier, found = {w}, [w], []
        for _ in range(self.steps):
            nxt = []
            for x in frontier:
                cands = [x[:-len(s)] + r for s, r in self.rules if x.endswith(s) and len(x) > len(s)]
                cands += [pp + x[len(p):len(x) - len(s)] + rp for p, pp, s, rp in self.prefix
                          if x.startswith(p) and x.endswith(s) and len(x) > len(p) + len(s) + 1]
                for c in cands:
                    if c not in seen:
                        seen.add(c); nxt.append(c); found.append(c)
            frontier = nxt
        return found

    def keys(self, surface):
        """[(열쇠, tier)] tier 0 꼴 표 원형, 1 그대로, 2 규칙 원형"""
        out = []
        def add(k, t):
            if k and all(k != o[0] for o in out):
                out.append((k, t))
        vs = list(dict.fromkeys([surface, surface.lower(), surface[:1].upper() + surface[1:].lower()]))
        for v in vs:
            for l in self.forms(v):
                if l != surface:
                    add(l, 0)
        for v in vs:
            add(v, 1)
        for v in vs:
            for l in self.rule_forms(v):
                add(l, 2)
        return out
