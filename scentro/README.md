# SCENTRO carousel – editable source
- `python3 build_slide.py N [N...]` rebuilds slides (1..6) from transparent cutouts in `assets/cutouts/`.
- Scene (arch niche, travertine surface, shadows, reflections) and type are all in `build_slide.py` (config per slide in `SLIDES`).
- Cutouts: `cutout.py` (GrabCut), `cutout_white.py` (white-bg), `polycut.py` (hand-traced, low-contrast bottles). Originals in `assets/source/`.
- Fonts: Cormorant Garamond (OFL) + Inter.

## Original-bottle photo sources (commercial-reuse licence NOT verified)
MAD bottles (Rouge, Treasure, Marjorie, Dreamlight): fragrantica.com ids 118803, 119723, 119716, 118790 (bottle-only photos, edge-based cutout via cutout_edge.py). Effect + Forza: supplied photos.
Originals - Rouge: zgoperfumery.com · Naxos: shoprescuespa.com · Guidance: parfumexquis.us · Side Effect: 4doutfitters.com ·
Attrape-Rêves: fragrantica.com (id 51016) · Alexandria II: perfumeforever.com (matches Fragrantica id 17786 design)

## Collection 2 (new MAD carousel) - `output/collection2/`, cutouts in `assets/cutouts/collection2/`, sources in `assets/source/collection2/`
Built with the same `build_slide.py` template (entries 11+ in `SLIDES`). Bottle photos: Fragrantica ids - MAD: Sateen Oud 119717, Inviting 118792, Adria 118783, Bruno Exotic 118784, Draco 118789, Gumin 118791, Bruno Detox 119695;
originals: Oud Satin Mood 30352, Craquele 32671, Amyris Homme 15566, Delox 44357, Supreme Bouquet 18369. Commercial-reuse licence NOT verified.

## Collection 3 - women's MAD Selective 100 ml (`build_women.py`, `collection3/`)
Source = scentrojo.com product pages (site is a JS app; read with headless Playwright). Product ids: A113=48, A118=49, B103=51, B105=52, B107=53, D116=57, G102=59, K102=64, W213=73, Y104=76.
Use only the clean packshot (bottle beside its box); the site's campaign photos include designer bottles - do not use. Licence/permission: Scentro's own site imagery.
Originals (Fragrantica ids, each checked against the bottle in scentrojo's own product photo): A113 Alien Goddess 68354, A118 Armani My Way 62036, B103 Burberry Her 51694, B105 Burberry Her Elixir 75968, B107 Burberry Goddess 83483, D116 D&G Q EDP 78873, G102 Gucci Guilty Elixir Pour Femme 84546, K102 Kayali Vanilla Candy Rock Sugar 42 92258, W213 YSL Black Opium 25324, Y104 YSL Black Opium Over Red 88707.
Build all: `python3 build_women.py` (or pass codes). Per-perfume palette/notes/sizes live in W_ITEMS.
