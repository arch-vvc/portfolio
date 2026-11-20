// Builds assets/Archit_Rishabh_CV.pdf from the CV text in index.html, so the PDF and the site
// always say the same thing. The CV in index.html has no phone number, so neither does the PDF.
// Run:  node scripts/make_cv_pdf.js      (needs Node and Playwright)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const m = html.match(/<article class="page">([\s\S]*?)<\/article>/);
if (!m) { console.error('CV article not found in index.html'); process.exit(1); }

const doc = `<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>Archit Rishabh CV</title>
<style>
  @page { size: A4; margin: 11mm 13mm; }
  * { box-sizing: border-box; }
  body { margin: 0; color: #111; font-family: Carlito, Calibri, "Liberation Sans", Arial, Helvetica, sans-serif; font-size: 9.7pt; line-height: 1.33; }
  a { color: #0b57d0; text-decoration: none; }
  .cv-name { margin: 0; text-align: center; font-size: 15pt; font-weight: 700; }
  .cv-contact { margin: 3pt 0 0; text-align: center; font-size: 9.6pt; }
  h4 { margin: 8pt 0 3pt; text-align: center; font-size: 10.6pt; font-weight: 700; }
  .entry { margin: 0 0 2pt; break-inside: avoid; }
  .row { display: flex; justify-content: space-between; gap: 12pt; }
  ul { margin: 1pt 0 2pt; padding-left: 17pt; }
  li { margin: 0; }
  b, strong { font-weight: 700; }
</style></head><body>${m[1]}</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(doc, { waitUntil: 'load' });
  const out = path.join(root, 'assets', 'Archit_Rishabh_CV.pdf');
  await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('wrote', out);
})();
