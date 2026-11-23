"""<lang>-ko.senses.tsv + forms.tsv → out/dict/wordcam-dict-<lang>-ko.sqlite (+ 크기 보고)
표: s(h 표제어, p 품사, n 순서, l 영어 이름표, k 한국어 '|' 묶음, c 출처) / f(f 꼴, h 표제어들 '|') / m(a 첫 낱말 소문자, h 여러 낱말 표제어) / meta
실행: python3 -I 50_build_sqlite.py <out_dir> <lang> [drop_forms.txt]"""
import sys, os, sqlite3, gzip, lzma, collections
out, L = sys.argv[1], sys.argv[2]
drop = set()
if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
    drop = set(x.rstrip('\n') for x in open(sys.argv[3], encoding='utf-8'))
os.makedirs(os.path.join(out, 'dict'), exist_ok=True)
db = os.path.join(out, os.environ.get('DICTDIR', 'dict'), f'wordcam-dict-{L}-ko.sqlite')
os.makedirs(os.path.dirname(db), exist_ok=True)
if os.path.exists(db): os.remove(db)
c = sqlite3.connect(db)
c.executescript("""
PRAGMA page_size=4096;
CREATE TABLE s(h TEXT NOT NULL, n INTEGER NOT NULL, p TEXT NOT NULL, l TEXT NOT NULL, k TEXT NOT NULL, c TEXT NOT NULL, PRIMARY KEY(h,n)) WITHOUT ROWID;
CREATE TABLE f(f TEXT PRIMARY KEY, h TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE m(a TEXT NOT NULL, h TEXT NOT NULL, PRIMARY KEY(a,h)) WITHOUT ROWID;
CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT) WITHOUT ROWID;
""")
rows = []; hw = set(); cnt = collections.Counter()
for l in open(os.path.join(out, f'{L}-ko.senses.tsv'), encoding='utf-8'):
    w, p, n, lab, ko, src = l.rstrip('\n').split('\t')
    rows.append((w, cnt[w], p, lab, ko, src)); cnt[w] += 1; hw.add(w)
c.executemany('INSERT OR IGNORE INTO s VALUES (?,?,?,?,?,?)', rows)
fr = []
for l in open(os.path.join(out, f'{L}-ko.forms.tsv'), encoding='utf-8'):
    f, h = l.rstrip('\n').split('\t')
    if f in drop: continue
    fr.append((f, h))
c.executemany('INSERT OR IGNORE INTO f VALUES (?,?)', fr)
mw = [(w.split()[0].lower(), w) for w in hw if ' ' in w]
# 한국어가 없는 여러 낱말 표제어도 '묶기 목록'으로만 넣는다(구동사·숙어·부사구 등). 뜻은 앱이 문맥 뜻으로 채움
import json as _j
work = os.environ.get('WORK', 'work')
wp = os.path.join(work, f'{L}_min.jsonl')
PHRASE_POS = {'verb', 'phrase', 'prep_phrase', 'adv', 'intj', 'adj', 'prep', 'conj', 'proverb'} if L == 'en' else None
have = set(h for _, h in mw)
if os.path.exists(wp) and L not in ('ja', 'zh'):
    for line in open(wp, encoding='utf-8'):
        if '"w": "' not in line: continue
        d = _j.loads(line)
        w = d['w']
        if ' ' not in w or len(w.split()) > 5 or w in have: continue
        if PHRASE_POS is not None and d['p'] not in PHRASE_POS: continue
        if not any(not x['fo'] for x in d['se']): continue
        mw.append((w.split()[0].lower(), w)); have.add(w)
c.executemany('INSERT OR IGNORE INTO m VALUES (?,?)', mw)
meta = {'lang': L, 'target': 'ko', 'license': 'CC BY-SA 4.0', 'built': '2026-11-24',
        'source': 'Wiktionary (en/ko/de/es/ja/zh) via Wiktextract/kaikki.org dumps of 2026-10-30..11-02; adapted by hiio'}
c.executemany('INSERT INTO meta VALUES (?,?)', meta.items())
c.commit(); c.execute('VACUUM'); c.close()
raw = os.path.getsize(db); data = open(db, 'rb').read()
gz = len(gzip.compress(data, 9)); xz = len(lzma.compress(data, preset=9))
srcs = collections.Counter(r[5].split('+')[0] for r in rows)
print(f"{L}\theadwords={len(hw)}\tsenses={len(rows)}\tforms={len(fr)}\tmultiword={len(mw)}\tsqlite={raw/1e6:.2f}MB\tgzip={gz/1e6:.2f}MB\txz={xz/1e6:.2f}MB\tsrc={dict(srcs)}")
