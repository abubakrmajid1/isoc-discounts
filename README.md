# Swansea ISOC discount directory

**Website:** https://abubakrmajid1.github.io/isoc-discounts/

The website is published by GitHub Pages from the `main` branch. No installation, terminal commands or paid hosting are needed.

## Change an offer

1. Open [directory-data.js](./directory-data.js) and click the pencil (Edit).
2. Change the relevant business details, keeping the quotes and commas.
3. Click **Commit changes**, choose `main`, and save. Pages republishes the website; the QR-code address stays the same.

To add a business, copy one complete offer object and give it a unique `id`. Upload its logo into `logos/` using **Add file → Upload files**, and put that relative filename in `logo`.

Status values:
- `active`: available to claim.
- `pending`: displayed as awaiting confirmation, not as a live offer.
- `hidden`: not displayed.

For a food business, `halalChecked: true` is also required before an offer becomes claimable. Set this only after the specific branch has been checked. Retain confirmation evidence in the private committee records. Public web listings and a cuisine type are not equivalent to certification.

## Files used by the live site

| File | Purpose |
| --- | --- |
| `index.html` | Page structure and wording |
| `directory.css` | Styling and phone layouts |
| `directory.js` | Search, filters, saved places and offer details |
| `directory-data.js` | Business details, discount conditions and source links |
| `isoc-emblem.png`, `isoc-logo.png`, `favicon.png` | Supplied Swansea ISOC branding |
| `logos/` | Business logos; source URLs are recorded in `sources.json` |

The earlier `offers.js`, `app.js` and `styles.css` are not used by the redesigned site. The original unconfirmed business list is retained in `offers.js` for reference rather than silently deleted.

## Offer records

Wokway and Ace’s 15% offers originate from the supplied ISOC draft. They remain pending until the committee confirms their terms and branch halal information. Kaspa’s is hidden pending verification. No pubs, example businesses or invented discounts are displayed.

The general offers link to their providers: [Boots](https://www.boots.com/student-discount), [Superdrug via Student Beans](https://www.studentbeans.com/student-discount/uk/superdrug), [schuh](https://www.schuh.co.uk/help/student-discount/) and [Specsavers](https://www.specsavers.co.uk/offers/student-glasses-discount). These were reviewed on 20 September 2026. They are not ISOC-negotiated partnerships. Recheck them before promoting and whenever terms change.

Brand logos identify the listed businesses; they do not imply sponsorship. Logo source URLs are retained with the assets. Fonts are loaded remotely from Google Fonts (Newsreader and Onest); no font files are distributed.

## Access and privacy

This repository and GitHub Pages site are public. Do not put volunteer details, member information, passwords, private negotiation notes or personal contacts in any file. The page does not implement committee-only access. Only authorized repository collaborators can publish changes.

## Checks and recovery

The check workflow tests desktop, tablet and phone layouts, asset loading, filters, saved offers, keyboard-operated dialogs and offer deep links. It produces screenshots and a report as downloadable Actions artifacts.

To find deployment progress, open **Actions → pages build and deployment**. To undo an accidental edit, open the file’s History and restore the previous contents. Keep the repository name unchanged once cards carrying its QR code have been printed.
