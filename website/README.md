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

## concept_v3 (Scentro identity · promotions engine · dashboard prototype)
`concept_v3/index.html` — single file. Store: `#`, Arabic: `#ar`, dashboard: `#admin` (tabs: promotions / orders / brands). Demo hashes: `#ar-demo`, `#promo` (cart with promos), `#co` (checkout).
- Identity taken from the live SCENTRO wordmark: black · ivory · gold, classic serif. Burgundy (MAD campaign colour) is NOT part of the store identity. Logo processed to transparent PNGs (`img/logo_dark.png`, `img/logo_light.png`); original glyphs unchanged.
- Delivery: flat 3 JOD everywhere (`DELIVERY_FEE`), waived by a free-delivery promotion.
- `engine.js` = promotions engine (percent, fixed amount, free delivery, buy X get Y %, bundle price, tiered spend, free gift; coupon codes, schedule, max uses, stackable vs best-of). `node test_engine.js` (25 cases). `node flow.js` = end-to-end store→order→dashboard check (Playwright).
- Orders are saved first (source of truth); WhatsApp message is an optional button for the customer, and a per-order "WhatsApp customer" button in the dashboard. E-mail to the shop on each order = server feature (not in prototype).
- Prototype data lives in the browser (localStorage). Real build: server DB + login; the server must re-price every order (never trust browser totals).
- Sample promotions in `SEED_RULES` are placeholders, not real offers.
- Notes: `data/notes_niche.json` (16 niche, from official MAD descriptions) + `data/notes_selective.json` (4 of ~52 so far, read from Scentro's own product-gallery infographics; mapping by product code from other sites proved unreliable – Y102 exists for both men and women).

- v3 update: light hero + Instagram-sampled gold (#D3B66D); all 81 catalogue products (24 niche, 52 selective, 5 body mist) in the store with real stock (sold-out / only-N-left); notes for 36 perfumes (`data/notes_*.json`, provenance per item); product page, search, mobile menu; audit scripts `audit.js`, `probe*.js`, `flow.js`, `test_engine.js`.
