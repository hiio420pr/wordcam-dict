# wordcam-krdict (CC BY-SA 2.0 KR)

Reverse indexes from foreign words (English, Japanese, Spanish, Chinese, French) to Korean headwords, used on-device by the Wordcam / 찰칵단어장 app.
Built from the Korean Basic Dictionary (한국어기초사전) by the National Institute of Korean Language. See ATTRIBUTION.md.
License: CC BY-SA 2.0 KR (LICENSE.txt). Text only: no audio, images or video from the source are included. App code is not part of this repository.

This is a companion to `wordcam-dict` (Wiktionary, CC BY-SA 4.0). It is kept as separate files under its own license.

## Files
- `data/krdict-<lang>-ko.tsv.gz`: the full reverse index as tab-separated text, with a header row. One row per (foreign key, Korean sense):
  - `key`: normalized foreign word. Lowercase for en/es/fr; parentheses removed; articles and "to " removed as a second key. Japanese `よみ【漢字・漢字】` gives each kanji form, plus the reading as a second key.
  - `ko`, `hom`: Korean headword and its homonym number.
  - `pos`: part of speech, as written in the source (명사, 동사 …).
  - `lvl`: vocabulary level. 0 = 초급 (beginner), 1 = 중급 (intermediate), 2 = 고급 (advanced), 3 = none.
  - `sn`: sense number of the Korean headword.
  - `pi`, `np`: position of this piece in the equivalent field, and the number of pieces in that field.
  - `kind`: 0 = as written; 1 = reading, or the form with the article removed; 2 = Japanese form with だ or する removed.
  - `unit`: 단어 / 구 / 관용구 / 속담.
  - `eq`: the original equivalent field, for review.
- `data/wordcam-krdict-<lang>-ko.sqlite.lzma`: the exact file the app would ship (xz/LZMA; unpack with `xz -d`).
  - Table `k(k key, v candidates)`. `v` holds up to 8 ranked candidates joined by `;`. Each candidate is `korean,pos,level,sense,flag`.
  - pos is n, v, a, d, i or o. level is 0–3, as above.
  - flag: `e` = the only word in the equivalent field, `f` = the first piece, `p` = another piece. A trailing `*` marks a reading or an article-stripped key.
  - Table `meta` holds the source, license and ranking name.
- `scripts/`: build scripts (Python 3, standard library only). Input: the official full JSON download (hashes in SOURCES.sha256).

Ranking (`score` in `krlib.py`):
1. single words first;
2. keys as written before readings or stripped forms;
3. then the lowest score = level (1 point per step: beginner < intermediate < advanced) + 2.5 × (sense number − 1, at most 4) + 0.5 × piece position + 0.5 if the field has several pieces.

## Build
```
python3 -I scripts/10_extract_krdict.py <dir with *.json> work/krdict.jsonl
python3 -I scripts/20_build_index.py work/krdict.jsonl out
python3 -I scripts/40_build_sqlite.py out en ja es zh fr
```
Entries are generated automatically from the source and are not reviewed. Corrections are welcome under the same license.
