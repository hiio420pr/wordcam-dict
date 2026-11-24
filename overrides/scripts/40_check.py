"""채운 검수 CSV 검사: 틀린 줄을 찾아 알린다(고치지 않음).
실행: python3 -I 40_check.py <review_dir> <filled.csv> [more.csv ...]
 - 원본(<review_dir>/<lang>.csv)과 id 로 맞춰서, 검수자가 바꾸면 안 되는 칸이 바뀌었는지도 본다.
 - 끝 코드: 오류 있으면 1, 경고만 있으면 0
"""
import sys, os, csv, re, collections

COLS = ['id', 'lang', 'word', 'pos', 'freq_rank', 'example', 'app_meaning', 'app_chips', 'wikt_candidates', 'krdict_candidates',
        'verdict', 'correct_meaning', 'alt_ok', 'note']
FIXED = COLS[:10]
KO = re.compile(r'[가-힣 ~/]+')
LANGS = {'en', 'ja', 'es', 'de', 'zh'}


def ko_ok(s):
    return s == '(문법어)' or (bool(KO.fullmatch(s)) and re.search('[가-힣]', s) and len(s) <= 20)


def main(rd, files):
    orig = {}
    errs = warns = 0
    for f in files:
        rows = []
        with open(f, encoding='utf-8-sig', newline='') as fh:
            rd_ = csv.reader(fh)
            head = next(rd_, None)
            if head != COLS:
                print(f'{f}: ERROR header differs: {head}'); errs += 1; continue
            for ln, r in enumerate(rd_, 2):
                if len(r) != len(COLS):
                    print(f'{f}:{ln}: ERROR {len(r)} columns (expected {len(COLS)})'); errs += 1; continue
                rows.append((ln, dict(zip(COLS, r))))
        seen = set()
        cnt = collections.Counter()
        for ln, r in rows:
            where = f"{f}:{ln} {r['id']}"
            def err(m):
                nonlocal errs; errs += 1; print(f'{where}: ERROR {m}')
            def warn(m):
                nonlocal warns; warns += 1; print(f'{where}: warn {m}')
            L = r['lang']
            if L not in LANGS or not re.fullmatch(rf'{L}-\d{{4,5}}', r['id']):
                err('bad id/lang'); continue
            if r['id'] in seen:
                err('duplicate id')
            seen.add(r['id'])
            if L not in orig:
                p = os.path.join(rd, f'{L}.csv')
                orig[L] = {x['id']: x for x in csv.DictReader(open(p, encoding='utf-8'))} if os.path.exists(p) else {}
            o = orig[L].get(r['id'])
            if o is None:
                err('id not in source table')
            else:
                for c in FIXED:
                    if o[c] != r[c]:
                        err(f'fixed column changed: {c} {o[c]!r} -> {r[c]!r}')
            v = r['verdict'].strip()
            cnt[v or '(empty)'] += 1
            cm, alts, note = r['correct_meaning'].strip(), r['alt_ok'].strip(), r['note'].strip()
            if v not in ('ok', 'fix', 'unsure', ''):
                err(f'verdict {v!r} not in ok/fix/unsure')
            if v == '':
                if cm or alts:
                    err('meaning filled but verdict empty')
                continue
            if v == 'fix' and not cm:
                err('fix without correct_meaning')
            if v == 'fix' and cm and cm == r['app_meaning']:
                warn('fix but correct_meaning == app_meaning (should be ok?)')
            if v == 'ok' and cm and cm != r['app_meaning']:
                warn('ok but correct_meaning differs from app_meaning (should be fix?)')
            if v == 'ok' and not r['app_meaning']:
                err('ok but app_meaning is empty')
            if v == 'unsure' and not note:
                err('unsure without note')
            if cm and not ko_ok(cm):
                err(f'correct_meaning not short Hangul: {cm!r}')
            if alts:
                items = alts.split(';')
                if any(not x.strip() for x in items) or any(x != x.strip() for x in items):
                    err(f'alt_ok has empty items or spaces around ";": {alts!r}')
                items = [x.strip() for x in items if x.strip()]
                for x in items:
                    if not ko_ok(x):
                        err(f'alt_ok item not short Hangul: {x!r}')
                main_m = cm or (r['app_meaning'] if v == 'ok' else '')
                if main_m and main_m in items:
                    warn('alt_ok repeats the main meaning')
                if len(set(items)) != len(items):
                    warn('alt_ok has duplicates')
                if len(items) > 4:
                    warn('alt_ok has more than 4 items')
        print(f'{f}: rows {len(rows)} verdicts {dict(cnt)}')
    print(f'TOTAL errors {errs} warnings {warns}')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2:]))
