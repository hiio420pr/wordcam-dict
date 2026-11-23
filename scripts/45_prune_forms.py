"""규칙 원형 찾기(lemma_rules.json, 앱 Swift 와 같은 방식)로 맞게 풀리는 꼴은 forms 표에서 뺀다 → drop-forms-<lang>.txt
en 은 NLTagger lemma 로 풀리는 꼴도 뺀다(drop-forms-en.txt 에 이미 있으면 합침). 실행: python3 -I 45_prune_forms.py <out_dir> <lang>"""
import sys, os, json, re
out, L = sys.argv[1], sys.argv[2]
R = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lemma_rules.json'), encoding='utf-8'))[L]
hw = set(l.split('\t', 1)[0] for l in open(os.path.join(out, f'{L}-ko.senses.tsv'), encoding='utf-8'))
def rule_lemmas(w):
    seen = {w}; frontier = [w]; found = []
    for _ in range(R['steps']):
        nxt = []
        for x in frontier:
            cands = [x[:-len(s)] + r for s, r in R['rules'] if x.endswith(s) and len(x) > len(s)]
            for pre, prep, suf, rep in R.get('prefix_rules', []):
                if x.startswith(pre) and x.endswith(suf) and len(x) > len(pre) + len(suf) + 1:
                    cands.append(prep + x[len(pre):-len(suf)] + rep)
            for c in cands:
                if c in seen: continue
                seen.add(c); nxt.append(c)
                for v in (c, c.lower(), c[:1].upper() + c[1:]):
                    if v in hw and v not in found: found.append(v)
        frontier = nxt
    return found
drop = set()
p0 = os.path.join(out, f'drop-forms-{L}.txt')
if L == 'en' and os.path.exists(p0): drop |= set(x for x in open(p0, encoding='utf-8').read().split('\n') if x)
n = 0
for l in open(os.path.join(out, f'{L}-ko.forms.tsv'), encoding='utf-8'):
    f, h = l.rstrip('\n').split('\t'); n += 1
    hs = h.split('|')
    if f in drop: continue
    # 띄어 쓴 꼴(조동사·관사 붙은 꼴: 'haben geklappt', 'eine ruhmvolle')·로마자 일본어·너무 긴 꼴은 뺀다(앱은 낱말 하나씩 찾음)
    if (' ' in f and not any(' ' in x for x in hs)) or len(f) > 24 or (L in ('ja', 'zh') and re.search(r'[A-Za-z]', f)):
        drop.add(f); continue
    rl = rule_lemmas(f)
    if all(x in rl for x in hs): drop.add(f)
open(p0, 'w', encoding='utf-8').write('\n'.join(sorted(drop)))
print(L, 'forms', n, 'drop', len(drop), 'keep', n - len(drop))
