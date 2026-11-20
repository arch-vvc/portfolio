# Archit Rishabh, portfolio site

## What this is

A static portfolio site written like a CV. Plain HTML, CSS and a little JavaScript. No framework, no build step, no packages, no CDN, no external fonts or scripts, no analytics.

- `index.html` is the home page: a Mac desktop with the CV open in a window, a Reminders widget, one folder per CV item and a dock. It is built for laptop screens. `desktop.css`, `desktop.js` and `assets/icons/` belong to it.
- `plain.html` is the plain text version. Small screens are sent there until the phone layout exists.
- `projects/` holds one page per project, including the tender tracker case study.
- `site.config.js` holds everything still to be filled in (demo videos, a CV file, photos).
- `styles.css` is the only stylesheet. `script.js` reads the config.
- `404.html` is shown by GitHub Pages for unknown pages.

Open `index.html` by double clicking it, or run `python3 -m http.server 8080` in this folder and visit http://localhost:8080.

## Desktop home page

The CV window is real HTML, so the text can be selected and read by search engines. Its close, minimise and full screen buttons work, the title bar drags, and a double click on the CV file on the desktop reopens it. Folders only select for now, and the dock icons only react to hovering.

To change the wallpaper, put a new image in `assets/` and change the one `url(assets/wallpaper.jpg)` line in `desktop.css`.

## Edit site.config.js

Every value starts empty. An empty value means nothing is shown: no button, no placeholder text.

Add a Loom link, which turns on the "Watch demo" button for that project:

```js
demos: {
  callqa: "https://www.loom.com/share/your-video-id",
  triage: "",
  gtm: "",
  tender: ""
},
```

Add a photo under Windstream. Put the file in `assets/` first:

```js
windstreamPhotos: [
  { src: "assets/site-1.jpg", caption: "Site survey", alt: "Engineers surveying a solar site" }
],
```

Other keys: `callqaResult` (live result text on the Call QA page), `capstoneResult` (text under Research), `cvPath` (for example `assets/archit-rishabh-cv.pdf`, which turns on the CV button) and `degreeTitle` (the exact degree title).

## Run the checks

```
python3 -m unittest discover -s tests -q
```

Python 3 standard library only, nothing to install. The checks cover links, images, alt text, titles, descriptions, external resources, phone numbers, page content, stylesheet contrast and sharing tags.

## Publish

Publish with GitHub Pages from the repo root:

1. Push the branch you want to publish to `main`.
2. In the repo on GitHub, open Settings, then Pages.
3. Under Build and deployment, choose "Deploy from a branch", pick `main` and the `/ (root)` folder, then save.
4. The site appears at the address GitHub shows on that page. The `.nojekyll` file stops GitHub from processing the files.
