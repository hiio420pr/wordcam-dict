# Wordcam dictionary data — attribution

This dataset (wordcam-dict-*-ko) is an adapted work ("Changes were made") by hiio, built on 2026-11-24 from:

| Source | Authors | License | Used for |
|---|---|---|---|
| English Wiktionary — https://en.wiktionary.org | Wiktionary contributors | CC BY-SA 4.0 | English headwords, senses, Korean translation tables, inflections; English glosses of Japanese, Chinese, Spanish, German and Korean entries |
| Korean Wiktionary (위키낱말사전) — https://ko.wiktionary.org | Wiktionary contributors | CC BY-SA 4.0 | Korean glosses of Japanese, Chinese, Spanish, German entries |
| German, Spanish, Japanese, Chinese Wiktionary — https://de.wiktionary.org, https://es.wiktionary.org, https://ja.wiktionary.org, https://zh.wiktionary.org | Wiktionary contributors | CC BY-SA 4.0 | Korean translation tables |

Extraction: Wiktextract (Tatu Ylonen, MIT License) via the machine-readable dumps at https://kaikki.org (dump dates 2026-10-30 to 2026-11-02; file hashes in SOURCES.sha256).

Changes made: selected entries; removed Hanja in parentheses, archaic/obsolete/vulgar entries and long phrases; merged duplicate Korean translations; ordered senses; added Korean meanings found by reverse lookup of English glosses of Korean entries and by pivoting through English glosses; built an inflection → lemma table; stored as SQLite and TSV.

License of this dataset: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0), https://creativecommons.org/licenses/by-sa/4.0/ — full text in LICENSE.txt. You may share and adapt it, also commercially, if you give attribution and share your adaptations under the same license.

No warranty. Dictionary entries were produced automatically and contain errors.
