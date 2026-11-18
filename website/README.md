# SCENTRO – new store (concept v1)

`concept_v1/index.html` – homepage design concept (EN + AR/RTL, desktop + mobile). Open in a browser; add `#ar` to the URL for Arabic.
Rebuild: `python3 build.py` (reads `catalog_snapshot.json`, `template.html`). Screenshots: `node shot.js`.

## Data sources (read-only, public, no login used)
Live catalogue is read from the storefront's public API (`api.ballour.store/v1/products|categories|brands`, header `x-tenant-domain: scentrojo.com`): 96 products, 10 categories, 1 brand.
Nothing on the live site was changed.

## Known gaps / to verify before launch
- Ballour has **no descriptions, notes or reviews** for products. The scent-finder moods/notes in `build.py` are PLACEHOLDERS inferred from product photos.
  Real notes exist as images in each Selective product's gallery (Top/Heart/Base infographic) – can be OCR'd / re-typed.
- Package images are promo graphics with baked-in text – to be re-rendered as clean product shots.
- Customers/orders are personal data: export from Ballour admin, do not paste into chat.

## concept_v2 (three directions + notes finder + guest COD checkout)
`concept_v2/index.html` — open in a browser. Switcher bottom-left: A Maison / B Noir / C Atelier. URL hash examples: `#noir-ar-demo` (dark, Arabic, finder pre-filled), `#atelier-co` (checkout form).
- Finder works on **notes** (9 note families, up to 3), compares with the published Top/Heart/Base notes (`data/notes_niche.json`, transcribed from official MAD descriptions: 16 niche scents so far). Honest copy: "likely to suit you, not a guarantee". No percentages.
- Checkout is guest-only: name, Jordanian mobile (validated), governorate, address, optional note. Cash on delivery only. Delivery fee is a placeholder ("confirmed when we call you") until decided.
- Rebuild: `cd concept_v2 && python3 build.py`.
