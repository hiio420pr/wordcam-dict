"""거꾸로 찾기 목록: 외국어 대역어 → 한국어 표제어 (en, ja, es, zh, fr).
실행: python3 -I 20_build_index.py <krdict.jsonl> <out_dir>
출력: <out_dir>/krdict-<lang>-ko.tsv  (머리줄 있음)
 key        정규화한 외국어 낱말(찾는 열쇠)
 ko         한국어 표제어
 hom        동형어 번호
 pos        품사(한국어기초사전 표기)
 lvl        0=초급 1=중급 2=고급 3=없음
 sn         뜻 번호(1부터)
 pi         대역어 칸 안에서 몇 번째 조각인지(0부터)
 np         대역어 칸의 조각 수
 kind       0=그대로 1=읽기(일본어 가나)·관사 뗀 꼴 2=だ/する 뗀 꼴
 unit       단어/구/관용구/속담
 eq         대역어 칸 원문(검토용)
"""
import sys, os, re, json, html

LV = {'초급': 0, '중급': 1, '고급': 2}
SKIP_POS = {'접사', '어미', '조사'}
SKIP_UNIT = {'문법‧표현'}
SEP = {
    'en': r'[;,]',
    'es': r'[;,]',
    'fr': r'[;,]',
    'zh': r'[;,，、；/]',
    'ja': r'[。;；、,，]',
}
PAREN = re.compile(r'\([^)]*\)|（[^）]*）|\[[^\]]*\]')
ART = {
    'en': ('to ', 'a ', 'an ', 'the '),
    'es': ('el ', 'la ', 'los ', 'las ', 'un ', 'una '),
    'fr': ('le ', 'la ', 'les ', "l'", 'un ', 'une ', 'se ', "s'"),
}
JA = re.compile(r'^(.*?)【(.*?)】(.*)$')


def clean(s):
    s = html.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def pieces(lang, raw):
    """대역어 칸 → [(조각 원문, [(열쇠, kind)])]"""
    raw = clean(raw)
    if not raw or raw.startswith('(') and PAREN.sub('', raw).strip(' .') == '':
        return []
    out = []
    for p in re.split(SEP[lang], raw):
        p = p.strip(' .。!?…·')
        if not p:
            continue
        keys = []
        if lang == 'ja':
            m = JA.match(p)
            if m:
                read, kan, tail = m.group(1).strip(), m.group(2), m.group(3).strip()
                for k in kan.split('・'):
                    k = PAREN.sub('', k).strip()
                    if k:
                        keys.append((k + tail, 0))
                if read:
                    keys.append((PAREN.sub('', read).strip() + tail, 1))
            else:
                k = PAREN.sub('', p).strip()
                if k:
                    keys.append((k, 0))
            more = []
            for k, kd in keys:
                if k.endswith('だ') and len(k) > 1:
                    more.append((k[:-1], 2))
                if k.endswith('する') and len(k) > 2:
                    more.append((k[:-2], 2))
            keys += more
        else:
            k = PAREN.sub('', p).strip()
            if lang != 'zh':
                k = k.lower()
                k2 = k
                for a in ART.get(lang, ()):
                    if k2.startswith(a) and len(k2) > len(a) + 1:
                        k2 = k2[len(a):].strip()
                        break
                if k:
                    keys.append((k, 0))
                if k2 != k and k2:
                    keys.append((k2, 1))
                # 영어 'be locked' → 'locked'(형용사·수동 대역)
                if lang == 'en' and k2.startswith('be ') and len(k2) > 4:
                    keys.append((k2[3:], 1))
            elif k:
                keys.append((k, 0))
        keys = [(re.sub(r'\s+', ' ', k).strip(), kd) for k, kd in keys]
        keys = [(k, kd) for k, kd in keys if k and len(k) <= 60]
        if keys:
            out.append((p, keys))
    return out


def main(src, outd):
    os.makedirs(outd, exist_ok=True)
    langs = ['en', 'ja', 'es', 'zh', 'fr']
    fh = {L: open(os.path.join(outd, f'krdict-{L}-ko.tsv'), 'w', encoding='utf-8') for L in langs}
    for f in fh.values():
        f.write('key\tko\thom\tpos\tlvl\tsn\tpi\tnp\tkind\tunit\teq\n')
    cnt = {L: 0 for L in langs}
    for line in open(src, encoding='utf-8'):
        e = json.loads(line)
        if e.get('pos') in SKIP_POS or e.get('unit') in SKIP_UNIT:
            continue
        ko = e['w'].strip()
        if not ko or ko.startswith('-') or ko.endswith('-'):
            continue
        lvl = LV.get(e.get('lvl'), 3)
        for si, s in enumerate(e['senses']):
            sn = s.get('n') or si + 1
            for L in langs:
                if L not in s['eq']:
                    continue
                raw = s['eq'][L][0]
                ps = pieces(L, raw)
                seen = set()
                for pi, (p, keys) in enumerate(ps):
                    for k, kd in keys:
                        if k in seen:
                            continue
                        seen.add(k)
                        fh[L].write('\t'.join(map(str, [k, ko, e.get('hom') or '', e.get('pos') or '', lvl, sn, pi, len(ps), kd,
                                                        e.get('unit') or '', clean(raw).replace('\t', ' ')])) + '\n')
                        cnt[L] += 1
    for f in fh.values():
        f.close()
    print(cnt)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
