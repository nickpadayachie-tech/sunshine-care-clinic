# Deploying to Domains.co.za (or any shared .co.za host)

Last updated: 23 September 2026 · Production: `https://www.sunshinehealthcare.co.za/`

> This repository is **source control only** (GitHub). The live site is hosted
> separately. Never link the live site to a GitHub URL.

## What to upload (into the web root of the domain)

Upload the following files and folders, keeping the folder structure:

```
.htaccess
index.html
about.html
services.html
iv-drip-therapy.html
family-baby-wellness.html
wound-care.html
contact.html
styles.css
script.js
robots.txt
sitemap.xml
sunshine-health-care-logo.png
sunshine-health-care-favicon.png
backup/            (optional on server, but it is blocked from indexation)
```

Do **not** upload dev-only files unless needed: `make_letterhead.py`,
`SunshineHealthCare_Letterhead.docx`, `medical image.png`, `Website Prompt.txt`.
The original large `SunshineHealthcareLogo.png` is only used by the letterhead tool.

## How `.htaccess` behaves once uploaded

1. **HTTP → HTTPS**: any request on `http://` is 301-redirected to `https://www.sunshinehealthcare.co.za/...`.
2. **www version**: any request on a bare-domain or other host is 301-redirected to `www.sunshinehealthcare.co.za`.
3. **Clean URLs**: `/about/`, `/services/`, `/iv-drip-therapy/`, `/family-baby-wellness/`,
   `/wound-care/`, `/contact/` are served internally from the matching `*.html` file.
   Both `/about` and `/about/` work; `/about/` is the canonical form. The homepage
   (`/`) serves `index.html`.
4. **Caching headers**: images, CSS and JS get browser caching; HTML is short-cached.

## Checks after upload

- [ ] `https://www.sunshinehealthcare.co.za/about/` returns the About page (200, not a redirect loop).
- [ ] `http://sunshinehealthcare.co.za/about/` lands (redirected) on `https://www.sunshinehealthcare.co.za/about/`.
- [ ] `https://www.sunshinehealthcare.co.za/robots.txt` serves the live robots.txt.
- [ ] `https://www.sunshinehealthcare.co.za/sitemap.xml` serves the live sitemap.
- [ ] Google Fonts, the Google Maps embed and the Google Maps link all load (public internet, not a blocked local network).
- [ ] Device check: header collapses to the hamburger menu on a phone; WhatsApp bubble and
      "back to top" button work; the drip booking form still opens WhatsApp with the selection.

## If a redirect loop appears

This normally means the host already forces HTTPS and/or the www version before `.htaccess`
runs, and the two conditions fight each other. The rules check `%{HTTPS}` and `%{HTTP_HOST}`
before redirecting, so only redirect one step at a time — if the host does one already,
the remaining checks pass instantly. If you still see a loop, ask the host to disable their
intermediate redirect (or update this file to force only the step the host does not).

## DNS note

If the domain is not yet pointed at the host's nameservers/DNS, the site will not resolve.
Use the host's control panel to connect the domain to the hosting account first.