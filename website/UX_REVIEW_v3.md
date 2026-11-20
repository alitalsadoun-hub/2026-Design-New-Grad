# UX/UI review — SCENTRO concept v3 (reviewer: Claude, acting as UX/UI designer)

Method: heuristic walkthrough of the buying journey (land → find → decide → cart → checkout → order), plus measurable checks (`concept_v3/audit.js`, `probe.js`, `flow.js`) on mobile 390px and desktop 1440px. Before/after numbers below are from the same script. This is an expert review, **not user research** — nothing here replaces testing with 5 real customers.

## Verdict
Visually strong and on-brand; the first version was **not yet easy to use**: mobile had no navigation, product cards led nowhere, and there was no clear next step after "Add to cart". Fixed in this pass. Score (my judgement): **before 5.5/10 → after 8/10** for a prototype; the remaining 2 points need real content (Selective notes, more photos per product), a real back-end, and user testing.

## Journey findings
| # | Step | Finding | Severity | Status |
|---|------|---------|----------|--------|
| 1 | Find | Mobile hamburger did nothing → no navigation at all on phones | 🔴 | Fixed (full-screen menu, closes on choose) |
| 2 | Find | Search icon did nothing | 🔴 | Fixed (search by name, note, family, brand) |
| 3 | Decide | 13 product links went to "#" → no product page, notes unreachable | 🔴 | Fixed (product page: price, COD/delivery info, Top/Heart/Base notes, similar scents) |
| 4 | Cart | After "Add to cart" only a toast, no path to checkout | 🟡 | Fixed (toast with "View cart (n)", badge pulse, mobile sticky add bar on product page) |
| 5 | Find | Mobile: finder results appear below the fold (159px) after choosing a note — no feedback | 🟡 | Fixed ("See your matches ↓" button) |
| 6 | Decide | Sold-out items (6 in the real catalogue) looked buyable; low stock invisible | 🟡 | Fixed (Sold out + "ask us when it is back" on WhatsApp; "Only N left" from real stock; cart capped at stock). Finder/similar never recommend sold-out items |
| 7 | All | Language reset to English on reload | 🟢 | Fixed (remembered; Arabic browsers default to Arabic) |
| 8 | Layout | Product grid overflowed the phone width after enlarging buttons (page 453px wide on a 390px phone) | 🔴 (found while testing my own fix) | Fixed; audit now compares against device width |
| 9 | Search | Overlay was see-through; toast cramped and overlapped the sticky bar; finder shortcut blocked taps | 🟡 | Fixed |

## Accessibility & ergonomics (measured)
| Check | Before | After |
|---|---|---|
| Touch targets < 44px (mobile / desktop) | 25 / 26 | **0 / 1** (desktop "Shop" link is 43×44) |
| Text under 12px | 36 elements | **0** |
| Contrast failures (WCAG AA) | 2 (WhatsApp green 3.1:1; small gold label on sand 4.05:1) | **0** (darker green and gold) |
| Links to nowhere | 13 | 1 (the logo → home, intended) |
| Cart is a dialog, Esc closes it, focus returns | no | **yes** |
| Visible keyboard focus / reduced-motion support | no | **yes** |
| Images lazy-loaded | 0/25 | 20/26 (hero + first screen stay eager) |
| JS errors | 0 | 0 |
Arabic/RTL checked on home and product page (mirrored layout, Amiri/IBM Plex Sans Arabic). Not audited: screen-reader pass with a real reader.

## What works well (keep)
- One clear primary action per screen; black/gold hierarchy; gold hairline from the logo reused as a divider.
- Notes finder with honest copy ("likely to suit you — not a guarantee"), shared notes shown by name, no fake percentages.
- Guest checkout with only name, mobile, governorate, address; Jordan mobile validation; COD stated three times (announcement bar, product page, cart).
- Cart shows exactly why the price changed (named promotions) and nudges toward free delivery with a progress bar.
- Delivery fee shown before checkout (3 JOD flat) — hidden costs are a top reason for abandonment.

## Still open (honest list)
1. **Notes coverage: 36 of 76 perfumes** (niche 16/24, selective 20/52; men's Selective almost entirely pending). Sources: Scentro's own product images (4), official MAD Parfumeur descriptions (32; cross-checked on 8 products against the images — 7 matched, 1 was a typo on MAD's own site). Everything without verified notes shows "notes coming soon" and is left out of the finder. The finder/product pages are only as good as this data.
2. One photo per product; perfume buyers want 2–4 (box, bottle on white, mood shot).
3. No order-tracking, About, Contact or policy pages yet (footer items are placeholders).
4. Prototype stores data in the browser. Real build needs server DB, login for the dashboard, server-side re-pricing, order e-mail.
5. Not tested with real users or on real low-end Android devices; run a 5-person task test (find a scent for a gift → order) before launch and watch where they hesitate.
6. Instagram page could not be viewed (login wall); brand colours/fonts were taken from the website wordmark only.

7. Brand alignment after seeing the Instagram page: feed is ivory/white with black serif and a champagne-gold (#D3B66D) accent. Store updated accordingly (light hero, gold sampled from the page); black kept only for the notes finder and footer.

8. Data update: Selective now uses the MAD Selective catalogue (26 collection): inspired-by house + original, the original's key notes and main accords for 48 of 52 products; sold-out items (stock 0) are no longer listed. Original names read from bottle photos are shown only where legible; 11 show the house only until confirmed (see QUESTIONS_for_owner.xlsx).

9. Niche notes now verified against the official MAD Niche catalogue (FlipHTML5): 6 spot-checks matched; Devil's Trick, Dreamlight, Pera, Trono added. Pending: Forza, Golden Soul. Selective inspired-by completed for W174 (Versace Eros), C126 (Carolina Herrera 212 Sexy), V109 (Victoria's Secret Crème Cloud) per owner. Tom Ford Q105/Q110 drafted in data/new_products_draft.json (need price, stock, photo).

10. Owner decisions applied: real offer "buy 2 Selective, get the 3rd free" (any 3 for 50 JOD at 25 JOD each) as a dashboard rule with customer headline fields; old Ballour packages hidden pending owner decision; before-discount prices kept; Golden Soul kept; stock kept as on Ballour (known inaccurate, temporary); Tom Ford Q105/Q110 listed at 25 JOD with placeholder photo/stock; originals confirmed from high-res catalogue pages except B105, P108, W179, J110; W174 = Versace Eros, C126 = 212 Sexy, V109 = Crème Cloud. Cart nudge for buy-X-get-Y; offers section; offer tags on cards and product pages. Engine: 32 tests passing.

11. Owner decisions: old packages deleted (offer is enough for now; packages can be added later). Forza (inspired by Xerjoff Alexandria II) and Golden Soul (inspired by Armani Privé Rouge Malachite) now have notes from Parfumo (MAD's own listings); Golden Soul also shows key notes of the original. Tom Ford Q105/Q110 images rebuilt as MAD 100 ml bottle + the original from the Selective catalogue (website/tools/make_tomford_images.py). Private preview published as an artifact link for the owner.

12. Data complete: all 77 listed products now have notes (niche from MAD Niche catalogue/Parfumo; Selective = original's key notes + accords from MAD Selective catalogue; body mists from the official MAD site). The 4 remaining originals confirmed by owner: B105 Burberry Her Elixir, P108 Million Gold for Her, W179 Invictus Parfum, J110 Scandal Absolu pour Homme. Inspired-by shows the original's NAME only (no logos), per owner. Remaining open: stock count (owner, later), real Tom Ford photos (optional).

13. Owner-reported bug: no way back from a product page (swipe-back). Fixed: product pages remember the list scroll position and browser back restores it; cart/search/menu are history entries so swipe-back closes them instead of leaving the page; visible Back button on product pages (also works where the browser's swipe is not available). `node hist.js` = 19 checks (desktop + mobile). Note: tested in Chromium, not on a physical iPhone. "Only N left" labels switched off (SHOW_STOCK_HINTS=false) until the stock count is verified, because the numbers on Ballour are known to be inaccurate; hiding items at 0 and capping quantity at stock remain per owner's instruction.

14. Finder tested end-to-end (387 runs + UI) and rebuilt: audited note->family dictionary, strength-based matching, headline-note tie-break, niche accords (MAD family + reliable Parfumo), duplicate chips removed. See website/FINDER_TEST_REPORT.md.
