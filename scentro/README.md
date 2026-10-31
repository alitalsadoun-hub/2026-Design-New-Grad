# SCENTRO carousel – editable source
- `python3 build_slide.py N [N...]` rebuilds slides (1..6) from transparent cutouts in `assets/cutouts/`.
- Scene (arch niche, travertine surface, shadows, reflections) and type are all in `build_slide.py` (config per slide in `SLIDES`).
- Cutouts: `cutout.py` (GrabCut), `cutout_white.py` (white-bg), `polycut.py` (hand-traced, low-contrast bottles). Originals in `assets/source/`.
- Fonts: Cormorant Garamond (OFL) + Inter.

## Original-bottle photo sources (commercial-reuse licence NOT verified)
MAD bottles (Rouge, Treasure, Marjorie, Dreamlight): fragrantica.com ids 118803, 119723, 119716, 118790 (bottle-only photos, edge-based cutout via cutout_edge.py). Effect + Forza: supplied photos.
Originals - Rouge: zgoperfumery.com · Naxos: shoprescuespa.com · Guidance: parfumexquis.us · Side Effect: 4doutfitters.com ·
Attrape-Rêves: fragrantica.com (id 51016) · Alexandria II: perfumeforever.com (matches Fragrantica id 17786 design)
