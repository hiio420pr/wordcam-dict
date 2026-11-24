# overrides/ — reviewed learner meanings for frequent words

Korean learner meanings for the 3,000 most frequent words in English, Japanese, Spanish, German and Chinese (15,000 rows), used by the Wordcam / 찰칵단어장 app as its first meaning when there is no sentence context, and as trusted candidates when there is.

## How it was made
- Word list: top 3,000 lemmas per language by [wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 frequency (data CC BY-SA 4.0), filtered to lemmas in the Wiktionary-based dictionary in this repository.
- Candidates shown to the reviewer: the app's meaning, the top Wiktionary→Korean senses (`data/`, CC BY-SA 4.0) and the top Korean Basic Dictionary candidates (`krdict/`, CC BY-SA 2.0 KR).
- Review: each row was judged by an AI model (OpenAI Codex) following `REVIEW-GUIDE.md`, then checked for format with `scripts/40_check.py`. **It was not reviewed by a human.** Expect mistakes; corrections are welcome.

## Files
- `data/overrides.tsv`: `lang, word, pos, meaning, alts, verdict, id`. `verdict` is `ok` (the app meaning was kept) or `fix` (replaced). `alts` are other acceptable meanings, `;`-separated.
- `data/unsure.tsv`: rows the reviewer marked unsure (not used by the app).
- `data/review-<lang>.csv.gz`: the full review tables with all candidate columns.
- `scripts/`: format checker, merge and assembly scripts (Python 3, standard library).

## License
CC BY-SA 4.0. This data adapts material from Wiktionary (CC BY-SA 4.0), the Korean Basic Dictionary by the National Institute of Korean Language (CC BY-SA 2.0 KR, which permits later versions) and wordfreq (CC BY-SA 4.0). See `../ATTRIBUTION.md` and `../krdict/ATTRIBUTION.md`.

- 2026-11-25: 41 of the 87 unsure rows were resolved with a dictionary candidate (verdict `unsure-fix`, see `data/unsure-decisions.tsv`); the other 46 are not used.
