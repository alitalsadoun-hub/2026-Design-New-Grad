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
