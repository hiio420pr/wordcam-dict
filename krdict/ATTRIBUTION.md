# Wordcam krdict data: attribution

This dataset (wordcam-krdict-*-ko) is an adapted work ("Changes were made") by hiio, built on 2026-11-24 from:

| Source | Author | License | Used for |
|---|---|---|---|
| 한국어기초사전 (Korean Basic Dictionary): https://krdict.korean.go.kr | 국립국어원 (National Institute of Korean Language) | CC BY-SA 2.0 KR | Korean headwords, part of speech, vocabulary level, sense numbers, and the English, Japanese, Spanish, Chinese and French equivalents (대역어) |

Source file: the official full download in JSON (LMF) form, created 2026-11-19 (11 files, hashes in SOURCES.sha256). The dictionary text only: no pronunciation audio, images or video were used.

Changes made:
- used only the headword, part of speech, vocabulary level, lexical unit, sense number and equivalent fields;
- dropped affixes, endings, particles and grammar patterns;
- split multi-word equivalent fields into pieces;
- normalized the keys (lowercase; parentheses, articles and "to " removed; Japanese readings and kanji split);
- reversed the direction to foreign word → Korean;
- ranked the candidates;
- stored the result as SQLite and TSV.

License of this dataset: Creative Commons 저작자표시-동일조건변경허락 2.0 대한민국 (CC BY-SA 2.0 KR), https://creativecommons.org/licenses/by-sa/2.0/kr/. The full text is in LICENSE.txt. You may share and adapt this dataset, also commercially, if you give attribution to 국립국어원 한국어기초사전 and share your adaptations under the same (or a compatible later) license.

No warranty. The data was produced automatically and contains errors. The National Institute of Korean Language has not reviewed or endorsed this adaptation.
