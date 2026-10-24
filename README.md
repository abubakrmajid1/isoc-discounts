# Swansea ISOC discount directory

**Website:** https://abubakrmajid1.github.io/isoc-discounts/

GitHub Pages publishes the `main` branch. The address and existing QR code stay unchanged when offers are updated.

## Current card benefits

The committee confirmed these offers on 24 October 2026. Show an ISOC discount card in store before ordering or paying.

| Partner | Card benefit | Additional condition |
| --- | --- | --- |
| Wokway | 15% off | |
| Cha Cha Stall | 10% off | One drink and a food item, or a meal deal |
| DFC Swansea | 20% off | Orders **over £25**; online code `ISOC123` |
| Hello Asia | 15% off | |
| Velvet Green | 25% off | |
| Jerk Hut | 7% off | Online code `SWANSEAISOC` |
| Foundry | 20% off | |
| Zazah Buffet | 10% off | |

Ace’s Desserts was removed following the committee’s report that it has closed.

Discount rates and conditions are supplied by the committee, not inferred from a public promotion. The website opens on **ISOC card**; unrelated student offers have a separate tab. Codes can be copied from the listing or offer details.

All eight current partners have logos. The Jerk Hut and Foundry logos were obtained from the official websites supplied by the committee: https://jerk-hut.co.uk/ and https://thefoundrycafekitchen.co.uk/. The downloaded images are stored locally so temporary image URLs do not expire on the directory. Their source records are in `logos/partner-correction-sources.json`. Jerk Hut’s order button points to its official menu. Directions appear only where a specific address is recorded.

## Change an offer

1. Open [directory-data.js](./directory-data.js) and click the pencil.
2. Edit the business’s details, keeping the quotes and commas.
3. Commit the change to `main` to publish it.

Add a business by copying one complete offer object with a new unique `id`. Upload its real logo to `logos/` and record its filename in `logo`. Leave uncertain fields blank rather than guessing. Set `onlineCode` and `onlineUrl` only when supplied or verified.

- `active`: committee-approved discount available to claim.
- `pending`: awaiting confirmation, not available to claim.
- `hidden`: excluded from the directory.

An active offer does **not** certify a business or all its products as halal. Keep dietary checks and written agreements in private committee records. Do not infer certification from a restaurant name or cuisine. Do not add pubs or alcohol-focused venues. Keep private contacts, member data, passwords and negotiations out of this public repository.

## General student offers

Boots, Superdrug, schuh and Specsavers remain in **Other student offers** with their own verification instructions and provider links. They are not ISOC partnerships. The retained terms were reviewed on 20 September 2026; recheck before promoting and when the provider changes its offer. Kaspa’s remains hidden pending verification.

## Website files

| File | Purpose |
| --- | --- |
| `index.html` | Page layout and wording |
| `directory.css` | Established ISOC design |
| `card-first.css` | Mobile card-first layout and code controls |
| `directory.js` | Filters, saved offers, details and code copying |
| `directory-data.js` | Discounts, conditions and business links |
| `logos/` | Original partner logos and source records |
| `isoc-emblem.png`, `isoc-logo.png`, `favicon.png` | Swansea ISOC branding |

The legacy `offers.js`, `app.js` and `styles.css` are not loaded. Fonts are requested from Google Fonts; no font files are distributed.

## Checks and recovery

`tools/test_card_benefits.py` checks all eight rates, Ace’s removal, the Cha Cha condition, DFC minimum spend, both copy buttons, eight logo loads, the supplied partner websites, saved items, searches, tabs, dialogs and six viewport widths. Browser screenshots and results are in the workflow artifact. It does not place orders or test merchant checkout acceptance.

For publishing progress, open **Actions → pages build and deployment**. Use file history to restore an earlier revision if necessary. Keep the repository name unchanged to preserve printed QR codes.
