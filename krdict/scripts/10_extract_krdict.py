"""한국어기초사전(LMF JSON) → 작은 JSONL (표제어·뜻 번호·뜻풀이·대역어).
원자료는 믿지 않는 데이터로 다룬다: python3 -I 로만 읽고, 이 스크립트는 원자료 폴더 밖에 둔다.
실행: python3 -I 10_extract_krdict.py <raw_dir> <out.jsonl>
한 줄 = 한 표제어:
 {"id","w","hom","unit","pos","lvl","origin","sem","senses":[{"n","def","eq":{"en":[lemma,definition],...}}]}
"""
import sys, os, json, glob

LANG = {'영어': 'en', '일본어': 'ja', '스페인어': 'es', '중국어': 'zh', '프랑스어': 'fr'}


def L(x):
    """한 개면 dict, 여러 개면 list 인 필드를 늘 list 로"""
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def feats(node):
    out = {}
    if isinstance(node, list):
        for x in node:
            for k, v in feats(x).items():
                out.setdefault(k, v)
        return out
    for f in L((node or {}).get('feat')):
        if isinstance(f, dict) and 'att' in f:
            out.setdefault(f['att'], f.get('val'))
    return out


def main(raw, outp):
    n_e = n_s = 0
    with open(outp, 'w', encoding='utf-8') as o:
        for p in sorted(glob.glob(os.path.join(raw, '*.json'))):
            d = json.load(open(p, encoding='utf-8'))
            for e in L(d['LexicalResource']['Lexicon'].get('LexicalEntry')):
                ef = feats(e)
                w = feats(e.get('Lemma')).get('writtenForm')
                if not w:
                    continue
                senses = []
                for s in L(e.get('Sense')):
                    sf = feats(s)
                    eq = {}
                    for q in L(s.get('Equivalent')):
                        qf = feats(q)
                        lg = LANG.get(qf.get('language'))
                        if lg and qf.get('lemma'):
                            eq[lg] = [qf.get('lemma', '').strip(), (qf.get('definition') or '').strip()]
                    senses.append({'n': int(s.get('val') or 0) if str(s.get('val') or '').isdigit() else 0,
                                   'def': (sf.get('definition') or '').strip(), 'eq': eq})
                n_e += 1; n_s += len(senses)
                o.write(json.dumps({'id': e.get('val'), 'w': w, 'hom': ef.get('homonym_number'),
                                    'unit': ef.get('lexicalUnit'), 'pos': ef.get('partOfSpeech'),
                                    'lvl': ef.get('vocabularyLevel'), 'origin': ef.get('origin'),
                                    'sem': ef.get('semanticCategory'), 'senses': senses},
                                   ensure_ascii=False) + '\n')
            del d
            print(os.path.basename(p), n_e, n_s, file=sys.stderr)
    print('entries', n_e, 'senses', n_s)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
