"""거꾸로 찾기 TSV → 앱용 작은 SQLite + LZMA(xz, preset 9 — 1.2 번들과 같은 방식). 크기·찾기 시간 재기.
실행: python3 -I 40_build_sqlite.py <out_dir> [langs...]
표: k(k TEXT PRIMARY KEY, v TEXT)  v = 순위대로 최대 8개 '한국어,품사,수준,뜻번호,표시' 를 ';' 로 이음
  품사 n/v/a/d/i/o · 수준 0초 1중 2고 3없음 · 표시 e=대역어 칸에 이 말 하나뿐, f=맨 앞 조각, p=그 밖, 끝에 *=읽기·관사 뗀 꼴(낮은 순위)
    meta(k, v): source·license·version
"""
import sys, os, sqlite3, lzma, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from krlib import load, ranked, rank_key

out = sys.argv[1]
langs = sys.argv[2:] or ['en', 'ja', 'es', 'zh', 'fr']
VAR = 'score'
os.makedirs(os.path.join(out, 'bundle'), exist_ok=True)
print('lang\tkeys\tsqlite_MB\txz_MB\tlookup_us_mean\tp95')
for L in langs:
    idx = load(os.path.join(out, f'krdict-{L}-ko.tsv'))
    p = os.path.join(out, 'bundle', f'wordcam-krdict-{L}-ko.sqlite')
    if os.path.exists(p):
        os.remove(p)
    db = sqlite3.connect(p)
    db.execute('CREATE TABLE k(k TEXT PRIMARY KEY, v TEXT NOT NULL) WITHOUT ROWID')
    db.execute('CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT) WITHOUT ROWID')
    rows = []
    for key, rs in idx.items():
        for r in rs:
            r['rank'] = rank_key(r, VAR)
        items = []
        for ko, r in ranked(rs)[:8]:
            flag = 'e' if r['np'] == 1 else ('f' if r['pi'] == 0 else 'p')
            if r['kind'] > 0:
                flag += '*'
            items.append(f"{ko.replace(',', ' ').replace(';', ' ')},{r['pc']},{r['lvl']},{r['sn']},{flag}")
        rows.append((key, ';'.join(items)))
    db.executemany('INSERT INTO k VALUES(?,?)', rows)
    db.executemany('INSERT INTO meta VALUES(?,?)', [
        ('source', '한국어기초사전 (National Institute of Korean Language, krdict.korean.go.kr), download 2026-11-19'),
        ('license', 'CC BY-SA 2.0 KR'), ('rank', VAR), ('lang', L)])
    db.commit(); db.execute('VACUUM'); db.close()
    data = open(p, 'rb').read()
    xz = lzma.compress(data, preset=9)
    open(p + '.lzma', 'wb').write(xz)
    # 찾기 시간(열린 파일, 열쇠 하나 = 쿼리 하나)
    db = sqlite3.connect(p)
    keys = random.Random(7).sample([r[0] for r in rows], 2000) + ['zzzz-not-there'] * 200
    ts = []
    for k in keys:
        t0 = time.perf_counter(); db.execute('SELECT v FROM k WHERE k=?', (k,)).fetchone(); ts.append((time.perf_counter() - t0) * 1e6)
    ts.sort()
    print(f"{L}\t{len(rows)}\t{len(data)/1e6:.2f}\t{len(xz)/1e6:.2f}\t{sum(ts)/len(ts):.1f}\t{ts[int(len(ts)*.95)]:.1f}")
