# wordcam-dict (CC BY-SA 4.0)

Small bilingual dictionaries (English, Japanese, Chinese, Spanish, German → Korean) used on-device by the Wordcam / 찰칵단어장 app.
Built from Wiktionary data; see ATTRIBUTION.md. License: CC BY-SA 4.0 (LICENSE.txt). App code is not part of this repository.

## Files
- `data/wordcam-dict-<lang>-ko.sqlite.lzma` — the exact file shipped in the app (xz/LZMA; unpack with `xz -d`).
  Tables: `s(h headword, n order, p part of speech, l English sense label, k Korean meanings '|', c source)`,
  `f(f inflected form, h lemma(s) '|')`, `m(a first word, h multi-word headword)`, `meta`.
  Source codes: `wikt` en.wiktionary translation table · `rev` reverse lookup of English glosses of Korean entries ·
  `nat` de/es/ja/zh.wiktionary translation table · `piv` English gloss of the entry → Korean · `kow` ko.wiktionary gloss.
- `data/<lang>-ko.senses.tsv.gz` — same senses as plain text: headword, pos, order, label, korean, source.
- `data/lemma_rules.json` — suffix rules used together with the `f` table to find lemmas.
- `scripts/` — build scripts (Python 3, standard library only). Input: kaikki.org dumps listed in SOURCES.sha256.

## Build
```
python3 -I scripts/10_extract_en.py en.jsonl.gz work/en_min.jsonl
python3 -I scripts/11_extract_ko.py ko.jsonl.gz work/ko_min.jsonl
python3 -I scripts/12_extract_x.py ja ja.jsonl.gz work/ja_min.jsonl   # also zh, es, de
python3 -I scripts/13_extract_native.py de dewikt.jsonl.gz work/dewikt_ko.jsonl   # also es, ja, zh
python3 -I scripts/20_build_en.py work out
python3 -I scripts/40_build_x.py ja work kowikt.jsonl.gz out          # also zh, es, de
python3 -I scripts/45_prune_forms.py out <lang>
python3 -I scripts/50_build_sqlite.py out <lang> out/drop-forms-<lang>.txt
```
Entries are generated automatically and contain errors. Corrections are welcome under the same license.

## krdict/
A separate reverse index built from the Korean Basic Dictionary (한국어기초사전, National Institute of Korean Language), licensed CC BY-SA 2.0 KR. See `krdict/README.md` and `krdict/ATTRIBUTION.md`. It keeps its own license and is not merged with the Wiktionary data above.
