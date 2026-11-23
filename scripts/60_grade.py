"""out/results/<lang>.tsv 자동 채점(참고) → 표. ① 큰 뜻 맞음 ② 맞는 뜻이 카드 안에 있음. 보통·함정 따로, 70:30 섞은 점수.
실행: python3 -I 60_grade.py <results_dir> <testsets_dir> [langs...]"""
import sys, os, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade_lib import big_ok, card_ok
rd, td = sys.argv[1], sys.argv[2]
langs = sys.argv[3:] or ['en', 'ja', 'zh-Hans', 'es', 'de']
summary = []
for L in langs:
    p = os.path.join(rd, f'{L}.tsv')
    if not os.path.exists(p): continue
    tests = {r['id']: r for r in csv.DictReader(open(os.path.join(td, f'{L}.csv'), encoding='utf-8'))}
    res = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    st = collections.Counter(); bad = []
    for r in res:
        t = tests[r['id']]
        acc = [x for x in t['acceptable_ko'].split('|') if x]; wrong = [x for x in t['wrong_but_plausible_ko'].split('|') if x]
        s = t['set']; st[s, 'n'] += 1; st[s, 'found'] += r['a_src'] == 'dict'
        for m, big, card in (('a', r['a_big'], r['a_card'].split('|')), ('b', r['b_big'], r['b_card'].split('|')), ('c', r['c_big'], [r['c_big']])):
            b1 = big_ok(big, acc, wrong); b2 = b1 or card_ok(card, acc)
            st[s, m + '1'] += b1; st[s, m + '2'] += b2
            st[(s, t['category']), m + '1'] += b1; st[(s, t['category']), 'n' if m == 'a' else '_'] += 1 if m == 'a' else 0
            if m == 'b' and not b1: bad.append((r['id'], s, t['category'], t['sentence'], r['send'], r['b_big'], r['b_src'], t['acceptable_ko'], r['cands'][:150]))
        st[s, 'bnone'] += r['b_src'] != 'dict+pick'
    with open(os.path.join(rd, f'{L}-b-wrong.tsv'), 'w', encoding='utf-8') as o:
        o.write('id\tset\tcategory\tsentence\tsend\tb_big\tb_src\tacceptable\tcands\n')
        for b in bad: o.write('\t'.join(b) + '\n')
    for s in ('realistic', 'trap'):
        n = st[s, 'n']
        summary.append((L, s, n, st[s, 'found'], *[st[s, k] for k in ('a1', 'a2', 'b1', 'b2', 'c1', 'c2')], st[s, 'bnone']))
    cats = sorted({k[0][1] for k in st if isinstance(k[0], tuple) and k[0][0] == 'trap'})
    print(L, 'trap by category (big meaning right a/b/c):', ', '.join(f"{c} {st[('trap', c), 'a1']}/{st[('trap', c), 'b1']}/{st[('trap', c), 'c1']} of {st[('trap', c), 'n']}" for c in cats))
print('\nlang\tset\tn\tin_dict\ta①\ta②\tb①\tb②\tc①\tc②\tb_fallback_to_c')
for row in summary:
    n = row[2]
    print('\t'.join([row[0], row[1], str(n), f"{row[3]/n:.1%}"] + [f"{x/n:.1%}" for x in row[4:10]] + [str(row[10])]))
print('\n70:30 mix (realistic 70% + trap 30%), big meaning ①:')
for L in langs:
    r = [x for x in summary if x[0] == L]
    if len(r) != 2: continue
    re_, tr_ = r
    mix = lambda i: 0.7 * re_[i] / re_[2] + 0.3 * tr_[i] / tr_[2]
    print(f"{L}\ta {mix(4):.1%}\tb {mix(6):.1%}\tc {mix(8):.1%}\t| ② a {mix(5):.1%} b {mix(7):.1%} c {mix(9):.1%}")
