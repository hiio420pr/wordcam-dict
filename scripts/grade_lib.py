"""자동 채점(참고용, README 2절): 한국어 뜻이 acceptable_ko 와 같은지. 띄어쓰기·문장부호 무시, 끝말(하다/되다/다/히/게/한/의) 차이 허용.
틀림 표시가 나온 줄은 사람이 다시 본다."""
import re
SUF = ['하다', '되다', '스럽다', '이다', '하게', '하는', '한', '히', '게', '의', '적인', '적', '다', '기', '음', '은', '는', '인']
def norm(s):
    s = re.sub(r'\([^)]*\)', '', s or '')
    return re.sub(r'[\s\.\,!?~·\-\'"“”‘’]', '', s)
def stem(s):
    s = norm(s)
    if s.endswith('운') and len(s) >= 2:   # 날카로운 → 날카롭 (ㅂ 불규칙)
        last = s[-2]; code = ord(last) - 0xAC00
        if 0 <= code < 11172 and code % 28 == 0: return s[:-2] + chr(ord(last) + 17)
    for x in SUF:
        if s.endswith(x) and len(s) - len(x) >= 1:
            return s[:-len(x)]
    return s
def unpast(c):
    """과거·현재 활용 근사 되돌리기: 했다→하다, 접었다→접다, 헹군다→헹구다"""
    for a, b in (('했다', '하다'), ('었다', '다'), ('았다', '다'), ('였다', '다'), ('군다', '구다'), ('한다', '하다'), ('된다', '되다')):
        if c.endswith(a) and len(c) > len(a): return c[:-len(a)] + b
    return c
def match(cand, acc_list, strict=False):
    """cand: 한국어 한 낱말·구. acc_list: 허용 목록"""
    if norm(cand) != unpast(norm(cand)) and match(unpast(norm(cand)), acc_list, strict): return True
    c = norm(cand)
    if not c: return False
    for a in acc_list:
        a2 = norm(a)
        if not a2: continue
        if '~' in a:  # '방금 ~하다' 꼴: 앞뒤 조각이 다 들어 있으면 맞음
            parts = [norm(p) for p in a.split('~') if norm(p)]
            if parts and all(p in c for p in parts): return True
            continue
        if c == a2 or stem(c) == stem(a2): return True
        if strict: continue
        # 활용 차이(가르쳤다↔가르치다)는 앞 2글자 이상 같고 길이 차 2 이하일 때만
        sc, sa = stem(c), stem(a2)
        if len(sc) >= 2 and len(sa) >= 2 and sc[:2] == sa[:2] and abs(len(sc) - len(sa)) <= 1 and (sc.startswith(sa) or sa.startswith(sc)):
            return True
    return False
def split_meanings(text):
    """모델 답 '끝나다, 지속되다' → ['끝나다','지속되다']"""
    return [x.strip() for x in re.split(r'[,/;|·]', text or '') if x.strip()]
def big_ok(big_text, acc, wrong):
    ms = split_meanings(big_text)
    if not ms: return False
    if any(match(m, wrong, strict=True) for m in ms if wrong): return False
    return all(match(m, acc) for m in ms)
def card_ok(all_texts, acc):
    return any(match(m, acc) for t in all_texts for m in split_meanings(t))
