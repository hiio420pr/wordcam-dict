"""채운 검수 CSV → 앱에 넣을 덮어쓰기 표 (lang, word, pos → meaning, alts).
실행: python3 -I 50_merge.py <out_dir> <filled.csv> [more.csv ...]
 - 먼저 40_check.py 를 통과한 파일만 넣을 것(여기서도 오류 줄은 건너뜀).
 - ok  → meaning = app_meaning(검수자가 맞다고 확인), fix → meaning = correct_meaning, unsure·빈 줄 → 넣지 않음(unsure.tsv 로)
 - 같은 (lang, word, pos)가 여러 번이면 나중 파일이 이김.
출력:
 overrides.tsv            lang word pos meaning alts(;) verdict id
 wordcam-overrides.sqlite  o(l, w, p, m, a, v) PRIMARY KEY(l, w, p) — 앱이 사전보다 먼저 볼 표
 unsure.tsv               사람이 다시 볼 줄
"""
import sys, os, csv, re, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
KO = re.compile(r'[가-힣 ~/]+')


def ok(s):
    return s == '(문법어)' or bool(KO.fullmatch(s) and re.search('[가-힣]', s) and len(s) <= 20)


def main(out, files):
    os.makedirs(out, exist_ok=True)
    table, unsure, skipped = {}, [], 0
    for f in files:
        for r in csv.DictReader(open(f, encoding='utf-8-sig', newline='')):
            v = (r.get('verdict') or '').strip()
            cm = (r.get('correct_meaning') or '').strip()
            alts = [x.strip() for x in (r.get('alt_ok') or '').split(';') if x.strip()]
            if v == 'unsure':
                unsure.append(r); continue
            if v == 'ok':
                m = r['app_meaning'].strip()
            elif v == 'fix':
                m = cm
            else:
                continue
            if not m or not ok(m) or not all(ok(a) for a in alts):
                skipped += 1; continue
            alts = [a for a in dict.fromkeys(alts) if a != m][:4]
            table[(r['lang'], r['word'], r['pos'])] = (m, alts, v, r['id'])
    rows = sorted(table.items())
    with open(os.path.join(out, 'overrides.tsv'), 'w', encoding='utf-8') as o:
        o.write('lang\tword\tpos\tmeaning\talts\tverdict\tid\n')
        for (L, w, p), (m, a, v, i) in rows:
            o.write('\t'.join([L, w, p, m, ';'.join(a), v, i]) + '\n')
    p = os.path.join(out, 'wordcam-overrides.sqlite')
    if os.path.exists(p):
        os.remove(p)
    db = sqlite3.connect(p)
    db.execute('CREATE TABLE o(l TEXT NOT NULL, w TEXT NOT NULL, p TEXT NOT NULL, m TEXT NOT NULL, a TEXT NOT NULL, v TEXT NOT NULL, PRIMARY KEY(l, w, p)) WITHOUT ROWID')
    db.executemany('INSERT INTO o VALUES(?,?,?,?,?,?)', [(L, w, pp, m, ';'.join(a), v) for (L, w, pp), (m, a, v, i) in rows])
    db.commit(); db.execute('VACUUM'); db.close()
    if unsure:
        with open(os.path.join(out, 'unsure.tsv'), 'w', encoding='utf-8') as o:
            o.write('id\tword\tpos\tapp_meaning\tcorrect_meaning\tnote\n')
            for r in unsure:
                o.write('\t'.join((r.get(k) or '').replace('\t', ' ') for k in ('id', 'word', 'pos', 'app_meaning', 'correct_meaning', 'note')) + '\n')
    fixes = sum(1 for _, x in rows if x[2] == 'fix')
    print(f'overrides {len(rows)} (fix {fixes}, ok {len(rows) - fixes}) · unsure {len(unsure)} · skipped malformed {skipped}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
