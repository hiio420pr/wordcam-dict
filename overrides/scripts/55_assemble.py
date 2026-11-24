"""새 순위(rerank/)에 맞춰 검수 결과 모으기: 두 목록에 다 있는 낱말은 옛 Codex 결과, 새 낱말은 새 묶음 결과.
실행: python3 -I 55_assemble.py <review_dir> <codex_out_dir> <out_dir>
 - rerank/mapping.csv 의 batch 이름으로 <codex_out_dir>/<batch>.csv 를 읽어 id 로 줄을 찾는다
   (옛 묶음 en-001 … en-012, 새 묶음 en-101 …; 새 묶음 결과도 같은 폴더에 같은 이름으로 둔다고 가정)
 - 고정 칸(id … krdict_candidates, freq_rank 포함)은 rerank/<lang>.csv 에서, 검수 칸 4개만 Codex 결과에서 가져온다
 - 출력: <out_dir>/<lang>.csv (새 순위 3,000줄), <out_dir>/missing.tsv (결과가 아직 없는 줄)
 다음: python3 -I 40_check.py <review_dir>/rerank <out_dir>/*.csv  →  python3 -I 50_merge.py <merge_out> <out_dir>/*.csv
"""
import sys, os, csv, collections
R, CX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
REV = ['verdict', 'correct_meaning', 'alt_ok', 'note']
os.makedirs(OUT, exist_ok=True)
mp = list(csv.DictReader(open(os.path.join(R, 'rerank/mapping.csv'), encoding='utf-8')))
cache = {}


def batch_rows(b):
    if b not in cache:
        p = os.path.join(CX, f'{b}.csv')
        cache[b] = {r['id']: r for r in csv.DictReader(open(p, encoding='utf-8-sig', newline=''))} if os.path.exists(p) else None
    return cache[b]


missing = []
cnt = collections.Counter()
for L in sorted({m['lang'] for m in mp}):
    base = list(csv.DictReader(open(os.path.join(R, f'rerank/{L}.csv'), encoding='utf-8')))
    byid = {m['id']: m for m in mp if m['lang'] == L}
    out = []
    for r in base:
        m = byid[r['id']]
        got = batch_rows(m['batch'])
        x = got.get(r['id']) if got else None
        if x is not None and x.get('word') != r['word']:
            x = None   # id 는 같은데 낱말이 다르면 쓰지 않음
        if x is None or not (x.get('verdict') or '').strip():
            missing.append((L, r['id'], r['word'], m['source'], m['batch'], 'no file' if got is None else 'no verdict'))
            cnt[L, 'missing'] += 1
        else:
            for k in REV:
                r[k] = x.get(k, '')
            cnt[L, m['source']] += 1
        out.append(r)
    with open(os.path.join(OUT, f'{L}.csv'), 'w', encoding='utf-8', newline='') as o:
        w = csv.DictWriter(o, fieldnames=list(base[0].keys())); w.writeheader(); w.writerows(out)
    print(L, 'from old', cnt[L, 'old'], 'from new', cnt[L, 'new'], 'missing', cnt[L, 'missing'])
with open(os.path.join(OUT, 'missing.tsv'), 'w', encoding='utf-8') as o:
    o.write('lang\tid\tword\tsource\tbatch\twhy\n')
    for x in missing:
        o.write('\t'.join(x) + '\n')
