# Sunshine Health Care — SEO Audit & Site Structure

Last updated: 23 September 2026 · Domain: https://www.sunshinehealthcare.co.za/

## What was done

The original single-page site (one `index.html`) was converted into a seven-page site with
one clear topic per page, clean URLs, unique metadata, canonicals and structured data.

### Site map

| Page                                     | File                    | Clean URL                              |
| ---------------------------------------- | ----------------------- | -------------------------------------- |
| Home                                     | `index.html`            | `https://www.sunshinehealthcare.co.za/` |
| About                                    | `about.html`            | `https://www.sunshinehealthcare.co.za/about/` |
| Services                                 | `services.html`         | `https://www.sunshinehealthcare.co.za/services/` |
| IV / Drip Therapy                        | `iv-drip-therapy.html`  | `https://www.sunshinehealthcare.co.za/iv-drip-therapy/` |
| Family & Baby Wellness                   | `family-baby-wellness.html` | `https://www.sunshinehealthcare.co.za/family-baby-wellness/` |
| Wound Care                               | `wound-care.html`       | `https://www.sunshinehealthcare.co.za/wound-care/` |
| Contact                                  | `contact.html`          | `https://www.sunshinehealthcare.co.za/contact/` |

## On-page SEO checklist (applied per page)

- Unique `<title>` (primary keyword + brand).
- Unique meta description primed with the primary keyword + NAP for local intent.
- One `H1` per page describing the page topic.
- Self-referencing canonical link per page.
- `lang="en-ZA"`.
- Open Graph and Twitter Card tags (title, description, image, URL) using the
  production domain so shared links render correctly.
- `geo.region` / `geo.placename` meta for local signals.
- Favicon (`sunshine-health-care-favicon.png`) and optimised logo
  (`sunshine-health-care-logo.png`) referenced on every page.
- Logical internal linking: every page links to the booking section, contact,
  and related service pages. Old single-page anchors (`#home`, `#about`,
  `#services`, `#drips`, `#contact`) were retained for any existing inbound links.

## Structured data (JSON-LD)

Every page carries two blocks merged with `@graph`:

- **MedicalClinic** with a shared `@id` (`https://www.sunshinehealthcare.co.za/#clinic`)
  so all pages describe the same clinic entity (name, NAP, phone, email, opening
  hours, `priceRange`). No fake reviews or ratings are included.
- **BreadcrumbList** matching the visual breadcrumb.

The homepage additionally embeds a **Person** node (`@id` `.../#practitioner`) for the
practitioner: Sr Sylvia P Mngadi, Private Nurse Practitioner.

Opening hours in structured data (Mon–Sat 10:30–18:30, Sun closed) match the hours
shown on the Contact page. `priceRange` "R350 - R1000" matches the drip menu on the
IV page.

## Administrative / indexation files

- `robots.txt` — allows crawling, blocks the `backup/` folder, points to the sitemap.
- `sitemap.xml` — the seven clean URLs with `lastmod`, `changefreq` and `priority`.
- `.htaccess` — clean-URL rewrites, `http → https` and non-`www → www` 301s, caching headers.
  Behavior documented in `DEPLOYMENT-DOMAINS-CO-ZA.md`.

## What was intentionally NOT done

- No fake Google reviews, star ratings, or unsupported claims.
- No qualifications beyond the four already shown on the original site
  (AUDHS in HSM (NWU); WC (FPD); AWC (Eloquent); GNS (GFNC)).
- No content about services the clinic does not advertise.
- No `localhost`/GitHub URLs anywhere in user-facing output.

## Known follow-ups

1. Deploy to Domains.co.za hosting and serve `https://www.sunshinehealthcare.co.za/`
   (see `DEPLOYMENT-DOMAINS-CO-ZA.md`).
2. Verify in Google Search Console that the live sitemap and canonical URLs report no
   errors (see `GOOGLE-SEARCH-CONSOLE.md`).
3. If the clinic later has a real Google Business listing, check the `url` field used
   there matches the site.
4. Re-run Google schema testing on the live domain after deployment.
5. Keep `lastmod` values in `sitemap.xml` accurate whenever pages change.