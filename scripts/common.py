"""공통: 한국어 낱말 다듬기, 영어 뜻풀이 쪼개기"""
import re
HANGUL = re.compile(r'[가-힣]')
OLD = re.compile(r'[ᄀ-ᇿ㄰-㆏ꥠ-꥿ힰ-퟿]')  # 옛한글·자모
BAD_TAGS = {'obsolete', 'archaic', 'dated', 'vulgar', 'offensive', 'derogatory', 'rare', 'dialectal', 'North-Korea', 'Middle-Korean', 'slur'}

def clean_ko(w):
    """'자유적(自由的)이다' → '자유적이다'. 한글이 아니거나 옛한글이면 None"""
    if not isinstance(w, str): return None
    w = re.sub(r'\([^)]*\)', '', w)
    w = re.sub(r'[\[\]{}〈〉《》「」]', '', w).strip()
    w = re.sub(r'\s+', ' ', w)
    if not w or OLD.search(w) or not HANGUL.search(w): return None
    if re.search(r'[A-Za-z0-9一-鿿~/]', w): return None
    if len(w) > 12: return None
    return w

def split_gloss(g):
    """영어 뜻풀이 → 짧은 영어 낱말·구 후보들. 'to be anxious; to worry (about)' → ['anxious','worry']"""
    g = re.sub(r'\([^)]*\)', '', g or '')
    g = re.sub(r'\[[^\]]*\]', '', g)
    out = []
    for part in re.split(r'[;,]', g):
        p = part.strip().strip('.').strip()
        p = re.sub(r'^(to be |to |a |an |the |be )', '', p, flags=re.I).strip()
        p = re.sub(r'\s+', ' ', p)
        if p and len(p) <= 40 and len(p.split()) <= 5:
            out.append(p.lower())
    return out

def short_label(s, n=60):
    s = re.sub(r'\s+', ' ', (s or '').strip())
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'

POS_KO = {'noun': 'noun', 'verb': 'verb', 'adj': 'adj', 'adv': 'adv', 'name': 'name', 'phrase': 'phrase', 'intj': 'intj',
          'num': 'num', 'pron': 'pron', 'det': 'det', 'prep': 'prep', 'conj': 'conj', 'particle': 'particle'}
