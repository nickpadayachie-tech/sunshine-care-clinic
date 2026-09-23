# Google Search Console — Verification & Maintenance

Last updated: 23 September 2026

## 1. Sign in

Go to `https://search.google.com/search-console`, sign in with the Google account that
owns (or will own) the site, and click **Add property**.

## 2. Property type & verification

- Choose **Domain** and enter `sunshinehealthcare.co.za` (this covers www and non-www,
  http and https in one property). Verification is done at DNS level with a TXT record.
- Or choose **URL prefix** with `https://www.sunshinehealthcare.co.za/` and verify via
  an HTML file, meta tag, or Google Analytics.

If using the DNS TXT method, add the record in the Domains.co.za DNS panel, wait up to a
few hours for propagation, then press **Verify**.

## 3. Submit the sitemap

1. In the left menu go to **Sitemaps**.
2. Submit: `https://www.sunshinehealthcare.co.za/sitemap.xml`
3. Confirm it reports no errors and lists all 7 URLs.

## 4. Request indexing

After deployment, request re-crawl of the most important pages:

- `https://www.sunshinehealthcare.co.za/`
- `https://www.sunshinehealthcare.co.za/iv-drip-therapy/`
- `https://www.sunshinehealthcare.co.za/contact/`

Use **URL Inspection** (top search bar) → paste URL → **Request indexing**.

## 5. What to watch for (first 1–2 weeks)

- **Coverage**: any excluded/erroring URLs (fixed by the 301s in `.htaccess` /
  consistent canonicals and internal links).
- **Sitemap**: index status and any "URL not tested" rows.
- **Indexing of each clean URL** (`/about/` etc., not `about.html`).
- Duplicate page errors caused by `http`/non-www variants — these should all 301 to
  `https://www.sunshinehealthcare.co.za/...` and then stop being indexed.

## 6. Useful GSC panels

- **Performance** — keyword clicks/impressions; check the keyword map in
  `SEO-KEYWORD-MAP.md` against what actually ranks.
- **Pages** — which URLs get impressions (should be the clean URLs).
- **Enhancements → breadcrumbs / merchant listings (if available)** — Google may surface
  the BreadcrumbList and MedicalClinic structured data here. Broken structured data
  appears here as errors.

## 7. Housekeeping

- Update `sitemap.xml` `lastmod` values whenever a page changes and re-submit it.
- Validate any JSON-LD edits with Google's Rich Results Test or Schema validator
  before publishing.
- Keep passwords/verification tokens out of the repository.