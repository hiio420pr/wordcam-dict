# Review guide: Wordcam top-3k meanings

Your job: for each row, decide whether `app_meaning` is the best **short Korean meaning for a learner** who photographs this word in everyday text, and fill in the four reviewer columns. Edit nothing else.

## Columns you fill

| column | what to write |
|---|---|
| `verdict` | `ok`, `fix` or `unsure` (lowercase, nothing else) |
| `correct_meaning` | `fix`: required, the best meaning. `ok`: leave empty (it means "app_meaning is right"). `unsure`: optional best guess |
| `alt_ok` | other meanings a learner should also accept, separated by `;` (no spaces around `;`). At most 4. Leave empty if none |
| `note` | short English or Korean reason. Required for `unsure`, and for `fix` when the reason is not obvious |

Never change `id, lang, word, pos, freq_rank, example, app_meaning, app_chips, wikt_candidates, krdict_candidates`. Never add or delete rows.

## What "the best meaning" is

1. **The most common sense first.** Think of the sense a learner meets most often in everyday text (signs, menus, news, chats, textbooks). Not the first sense in a dictionary, not the etymology, not a technical sense. `bank` → 은행, not 둑; `dog` → 개, not 수캐.
2. **Short, plain Korean a learner knows.** One word or a short phrase, usually ≤ 8 Hangul characters. Prefer the everyday word over a rare, literary or Sino-Korean one: 소나기 over 소낙비, 잡초 over 김, 기념품 over 토산물. No Hanja, no Latin letters, no brackets, no explanations.
3. **Part of speech must match `pos`.**
   - noun → noun form (회의, not 회의하다).
   - verb → dictionary form ending in -다 (먹다, 공부하다).
   - adjective → descriptive verb in -다 (크다, 조용하다). If Korean naturally uses a noun + 이다 / 적 form, write that (필수적이다).
   - adverb → adverb (빨리, 완전히).
   - If `pos` itself looks wrong for this word, keep the meaning for the given pos and say so in `note`.
4. **Polysemy.** Pick the single most common sense for `correct_meaning`. Put other *common* senses in `alt_ok` (e.g. `play` verb: 놀다; alt_ok 경기하다;연주하다). Do not list rare senses. If two senses are about equally common and neither dominates, choose one, list the other in `alt_ok` and keep the verdict `ok`/`fix` (not `unsure`).
5. **Function words, particles, counters.**
   - Articles, particles and pure grammar words that have no Korean word (the, a, ja が/を/は, de "zu" as infinitive marker): write the closest Korean grammar element in short form with `~`, e.g. `~이/가`, `~을/를`, `~의`, `~하기 위해`. If there is no sensible equivalent, write `(문법어)` in `correct_meaning`, verdict `fix`, and explain in `note`.
   - Counters / measure words (枚, 本, 冊, 张, 条, 件, 只, 块, 门): write the Korean counter (장, 자루, 권, 벌, 마리, 개…) and add the typical object in `note` (e.g. "for flat things"). Use `alt_ok` for other counters.
   - Pronouns and prepositions: the usual Korean equivalent (나, 너, ~에서, ~와 함께).
6. **Judge `app_meaning` only.** `app_chips`, `wikt_candidates` and `krdict_candidates` are hints. `krdict_candidates` come from a learner dictionary; the letter in brackets is the Korean word's level (초 beginner, 중 intermediate, 고 advanced, then the sense number if it is not 1). A beginner-level candidate is often the better learner word, but not always.
7. **`ok` vs `fix`.**
   - `ok` when `app_meaning` is a correct, natural, common meaning for this pos, even if you would have phrased it slightly differently. Synonyms that a learner would accept are `ok`.
   - `fix` when it is wrong, a rare or wrong sense, the wrong pos, odd or archaic Korean, a misspelling (트랙타 → 트랙터), or empty.
8. **`unsure`** only when you cannot decide without more information: the word is genuinely ambiguous without context and no sense dominates, it is regional or slang you are not confident about, or you do not know the word well. Always say why in `note`. Do not use `unsure` just because the candidates disagree.
9. **The `example` column** shows one dictionary example when one exists. Use it to understand the word, but do not choose a rare sense just because the example uses it.
10. **Never invent facts.** If you are guessing, say so in `note`.

## Format rules (the checker enforces these)

- UTF-8 CSV, same header, same row order, same number of rows.
- `verdict` ∈ {ok, fix, unsure}.
- `correct_meaning` and every `alt_ok` item: Hangul, spaces, `~`, `/` only. No Latin letters, digits, Hanja or brackets (except the literal `(문법어)`). At most 20 characters each.
- `alt_ok` must not repeat `correct_meaning` (or `app_meaning` when verdict is `ok`).
