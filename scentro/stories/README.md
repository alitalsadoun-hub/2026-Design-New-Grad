# SCENTRO Instagram Stories (1080x1920)
`python3 stories/build_stories.py [nyn|gs]` (run from `scentro/`) -> `stories/output/scentro_new_york_night_story.png`, `scentro_golden_soul_story.png`.
Sources (the user's three supplied photos) in `assets/source/`; cutouts in `assets/cutouts/`; ingredient cutouts via `extract_ingredients.py` (peach / vanilla / leaves, real pixels from the supplied flat-lay).
Safe zones respected: no important content above y=250 or below y=1620.
Notes used (verified on Fragrantica / Parfumo): New York Night - peach, vanilla (both sites), lily of the valley (Parfumo + brand flat-lay). Golden Soul - ylang-ylang, neroli / orange blossom, jasmine, cedarwood.
No inspiration claims are made on either Story (Bond No. 9 / Armani Prive not mentioned).

## Update: sharper sources
New York Night now uses the official MAD Parfumeur Singapore store images (2000x2000): packshot `assets/source/new_york_night_packshot_official_2000.jpg` (bottle + box) and flat-lay `..._flatlay_official_2000.jpg` (ingredients, extract_ingredients.py with scale 2.415). Cutouts: `nyn_bottle_hi.png`, `nyn_box_hi.png`, `ing_hi_*.png`.
Golden Soul: official madparfum.com page images top out at 615 px and Fragrantica (id 120894) has only a bottle-only 750x1000 photo, so the supplied 828 px box+bottle photo remains the best source for that Story.

## v2 (current): same layout as the 10-slide collections - MAD hero left, inspired original right, no box / props
- New York Night: MAD (official 2000 px packshot cutout) + Bond No. 9 New York Nights (Fragrantica id 46057). Pairing NOT verified by MAD's current page - flagged for owner confirmation.
- Golden Soul: MAD bottle (Fragrantica id 120894, bottle-only) + Armani Prive Rouge Malachite (Fragrantica id 34589). Pairing supplied by the owner ("listed by retailers"); no official source found.
- No "inspired by"/"dupe" wording on either image. First (box + props) versions are kept in `output/archive_box_version/`.
