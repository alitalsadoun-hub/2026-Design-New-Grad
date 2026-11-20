# "Find by notes" — test report

## What was tested
Every combination of 1–3 scent families (129) × anyone / for her / for him = **387 runs**, driven through the page's real code,
then re-computed by an independent oracle (`concept_v3/finder_test.py`) and compared run by run. Plus a click-through UI test
(`finder_ui.js`: desktop EN + mobile AR) and the older suites (promotions engine 32, order flow, history/back 19, accessibility audit).

Checks per result: eligible (right gender, in stock, not a body mist); really linked to a picked family; every note shown is a
real note of that perfume and belongs to a picked family; the best 3 are shown in the right order; the tier label ("Closest /
Close / Shares some") and the strength sentence are correct; no note shown twice; a perfect match is always first.

## Result
387/387 runs pass, every run returns 3 results, 0 page errors. For 3 picked families a full match exists for 77 of 84 combinations
(anyone); the other 7 are labelled "Close to your notes" instead of pretending (e.g. citrus + fruity + oud: no perfume has all three).

## Problems found by the first run, and fixed
1. 21 of 182 note strings belonged to **no** family (coffee, iris, litchi, passion fruit, ambroxan, osmanthus, juniper, suede, milk…) so they never counted.
   -> audited dictionary `data/note_families.json` (every note mapped by hand; the build now **fails** if a new note has no family).
2. Wrong classes: honeysuckle (was "sweet", is a flower), orange flower (was citrus), balsamic (was aromatic, is amber), chewing gum, candied lemon.
3. Keyword matching by substring (e.g. "rose" inside "rosewood") -> exact dictionary + word-boundary fallback.
4. The same note shown twice in 175 of 1,161 result cards ("Vanilla" + "vanilla" + "sweet") -> real notes only, each once; accord words only if nothing more specific matches.
5. Matching was yes/no. Now by **strength**: heart/base/key notes count fully, a top note or an accord only 0.6–0.8; results with only a weak link are labelled "light hint".
6. Ranking: ties are broken by whether the family's headline note is a real note (a real *Oud* note for "Oud & smoky"), then by how dominant the family is in the perfume.
7. One bug in my own first fix: a "generic words" filter hid real notes named like accords (Amber, Vanilla, Oud). Replaced by source-based logic (note vs accord).

## "What do most people actually smell?" — what could and could not be done
- Selective: the MAD catalogue gives the **main accords of the original** as voted by fragrance-community users, plus the 3 key notes. Used (weight 0.8 / 1.0).
- Niche: MAD's own *Fragrance Family* for all 21 (official), plus Parfumo community accords for the 9 where Parfumo's note list matches MAD's by >= 80%
  (for the others Parfumo's entry differs from MAD's official list, so its accords were NOT used). Fragrantica is blocked for me.
- Written reviews of MAD niche perfumes online are almost non-existent; found: Treasure ≈ Xerjoff Naxos (more honey, less tobacco, fresher lemon opening), Pera = sweet
  dessert-like oriental turning spicy, Detox = cherry/sweet with rose, Gumin = fresh citrus-aquatic-woody (one reviewer: fades quickly). All consistent with the data; nothing invented for the rest.

## Re-run
`cd website/concept_v3 && python3 build.py && node finder_audit.js && python3 finder_test.py && node finder_ui.js`
