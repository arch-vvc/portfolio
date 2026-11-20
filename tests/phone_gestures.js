// Real browser check of the phone gestures. Run by tests/test_phone_browser.py, or by hand:
//   node tests/phone_gestures.js
// Needs Node and Playwright. Exits 0 and prints "PHONE GESTURES OK" when everything holds.
const { chromium } = require('playwright');
const path = require('path');

const failures = [];
function check(name, ok, detail) { if (!ok) failures.push(name + (detail !== undefined ? ' (' + JSON.stringify(detail) + ')' : '')); }

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
  });
  const page = await ctx.newPage();
  page.setDefaultTimeout(5000);
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const client = await ctx.newCDPSession(page);

  async function swipe(x1, y1, x2, y2, steps = 14) {
    await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: x1, y: y1 }] });
    for (let i = 1; i <= steps; i++) {
      await client.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x1 + (x2 - x1) * i / steps, y: y1 + (y2 - y1) * i / steps }] });
      await page.waitForTimeout(10);
    }
    await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await page.waitForTimeout(550);
  }
  const centre = sel => page.$eval(sel, e => { const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; });
  async function tap(sel) { const [x, y] = await centre(sel); await page.touchscreen.tap(x, y); await page.waitForTimeout(750); }
  const track = () => page.$eval('#p-track', e => e.style.transform);
  const sheets = () => page.$$eval('.p-sheet', s => s.length);

  await page.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  await page.waitForTimeout(400);

  // the phone shows, the laptop does not, and the drawn screen is inset from the real one
  const shown = await page.evaluate(() => [getComputedStyle(document.getElementById('phone')).display, getComputedStyle(document.getElementById('desktop')).display]);
  check('phone visible and laptop hidden', shown[0] === 'block' && shown[1] === 'none', shown);
  const inset = await page.$eval('#phone-screen', e => { const r = e.getBoundingClientRect(); return [r.left, innerWidth - r.right, innerHeight - r.bottom]; });
  check('screen inset at least 12px on the sides and bottom', inset.every(v => v >= 12), inset);

  // home first; the hint says what the owner asked for
  check('starts on home', (await track()) === 'translateX(-50%)', await track());
  check('hint text', (await page.$eval('#p-hint', e => e.textContent)) === 'swipe right to see projects');
  check('home page shows the name', (await page.$eval('[data-page="1"]', e => e.innerText)).includes('Archit Rishabh'));
  check('off screen page is inert', await page.$eval('[data-page="0"]', e => e.hasAttribute('inert')));

  // swiping left on home goes nowhere (rubber band), swiping right reveals projects
  await swipe(300, 420, 160, 420, 8);
  check('left swipe on home stays on home', (await track()) === 'translateX(-50%)');
  await swipe(90, 420, 300, 420);
  check('swipe right reveals projects', (await track()) === 'translateX(0%)', await track());
  check('hint follows the page', (await page.$eval('#p-hint', e => e.textContent)).includes('go back home'));
  check('home is inert, projects is not', await page.$eval('[data-page="1"]', e => e.hasAttribute('inert')) && !(await page.$eval('[data-page="0"]', e => e.hasAttribute('inert'))));
  await swipe(300, 420, 270, 420, 6);
  check('short swipe snaps back', (await track()) === 'translateX(0%)');

  // tap opens a sheet, a swipe up from the bottom strip closes it; a tiny swipe does not
  await tap('[data-pfolder=tender-tracker] .p-tile');
  check('folder opens', (await sheets()) === 1);
  check('folder shows its title', (await page.$eval('.p-sheet h2', e => e.textContent)) === 'Tender Tracker');
  check('no Coming soon row on a folder without a video', !(await page.$eval('.p-sheet', e => e.innerText)).includes('Coming soon'));
  let [bx, by] = await centre('.p-sheet .p-home-bar');
  await swipe(bx, by, bx, by - 30, 6);
  check('tiny swipe up keeps the sheet', (await sheets()) === 1);
  [bx, by] = await centre('.p-sheet .p-home-bar');
  await swipe(bx, by - 14, bx, by - 280, 12);
  await page.waitForTimeout(300);
  check('swipe up from above the bar icon closes the sheet', (await sheets()) === 0);

  // nested folder: the Windstream row opens Tender Tracker on top of it
  await swipe(300, 420, 80, 420);
  await tap('[data-pfolder=windstream] .p-tile');
  await tap('.p-sheet [data-open="tender-tracker"]');
  check('alias opens a second sheet', (await sheets()) === 2);
  await page.keyboard.press('Escape'); await page.waitForTimeout(600);
  await page.keyboard.press('Escape'); await page.waitForTimeout(600);
  check('Escape closes both sheets', (await sheets()) === 0);

  // Messages: list, thread, edge swipe back
  await tap('[data-pdock][aria-label=Messages]');
  check('messages opens', (await sheets()) === 1);
  await tap('.p-sheet .p-thread');
  check('thread view', (await page.$eval('.p-sheet h2', e => e.textContent)) === 'Archit Rishabh');
  const left = await page.$eval('.p-sheet', e => e.getBoundingClientRect().left);
  await swipe(left + 12, 420, left + 220, 420, 12);
  check('edge swipe goes back to the list', (await page.$eval('.p-sheet h2', e => e.textContent)) === 'Messages');
  await page.click('.p-sheet .p-close'); await page.waitForTimeout(600);

  // Safari does not open on a stub; Mail send link follows the edits; Claude does not open a sheet
  await tap('[data-pdock][aria-label=Safari]');
  const safariText = await page.$eval('.p-sheet', e => e.innerText);
  check('safari has no stub text', !/goes here|coming soon/i.test(safariText), safariText.slice(0, 120));
  await page.click('.p-sheet .p-close'); await page.waitForTimeout(600);
  await tap('[data-pdock][aria-label=Mail]');
  await page.fill('#p-subject', 'Call next week?');
  const send = await page.$eval('#p-send', a => a.href);
  check('mail send link carries the subject', send.startsWith('https://mail.google.com/mail/?view=cm') && send.includes('Call%20next%20week%3F') && send.includes('archit.rishabh25%40gmail.com'), send);
  await page.click('.p-sheet .p-close'); await page.waitForTimeout(600);
  await tap('[data-pdock][aria-label=Claude]');
  check('claude tap opens nothing', (await sheets()) === 0);

  // the CV sheet carries the CV
  await tap('[data-pfile=cv] .p-tile');
  check('cv sheet has the CV text', (await page.$eval('.p-cv', e => e.innerText)).includes('Windstream Technologies'));
  await page.click('.p-sheet .p-close'); await page.waitForTimeout(600);

  // a second finger and a cancelled touch must not leave the pages stuck mid drag
  await page.reload(); await page.waitForTimeout(400);
  await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 200, y: 420, id: 1 }] });
  for (let i = 1; i <= 5; i++) await client.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 200 + i * 12, y: 420, id: 1 }] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 200 + 60, y: 420, id: 1 }, { x: 120, y: 500, id: 2 }] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchCancel', touchPoints: [] });
  await page.waitForTimeout(600);
  check('cancel after a second finger snaps back to a page', (await track()) === 'translateX(-50%)', await track());
  check('track is not stuck in drag mode', !(await page.$eval('#p-track', e => e.classList.contains('dragging'))));
  await swipe(90, 420, 300, 420);
  check('pager still works after the cancel', (await track()) === 'translateX(0%)', await track());
  await swipe(300, 420, 80, 420);

  // Escape in the Mail text field is for the field, and focus returns to the opener after a nested close
  await tap('[data-pdock][aria-label=Mail]');
  await page.focus('#p-mailbody');
  await page.keyboard.press('Escape'); await page.waitForTimeout(500);
  check('Escape inside the mail body does not discard the draft', (await sheets()) === 1);
  await page.click('.p-sheet .p-close'); await page.waitForTimeout(600);
  await tap('[data-pfolder=windstream] .p-tile');
  await tap('.p-sheet [data-open="tender-tracker"]');
  check('parent sheet is inert while the child is open', await page.$eval('.p-sheet:not(:last-child)', e => e.hasAttribute('inert')));
  await page.keyboard.press('Escape'); await page.waitForTimeout(600);
  check('focus returns to the row that opened the child', await page.evaluate(() => document.activeElement && document.activeElement.getAttribute('data-open') === 'tender-tracker'));
  await page.keyboard.press('Escape'); await page.waitForTimeout(600);

  // Photos says what it is, plainly
  await tap('[data-pdock][aria-label=Photos]');
  check('photos shows its message without scrolling', (await page.$eval('.p-sheet .p-empty', e => { const r = e.getBoundingClientRect(); return r.bottom <= innerHeight && r.height > 0; })));
  await page.click('.p-sheet .p-close'); await page.waitForTimeout(600);

  check('no script errors', errors.length === 0, errors);
  await ctx.close();

  // other phone sizes: everything on Home fits, nothing overflows sideways, Mail does not clip
  for (const [name, w, h, land] of [['320x568', 320, 568, false], ['360x640', 360, 640, false], ['430x932', 430, 932, false], ['844x390 landscape', 844, 390, true]]) {
    const c2 = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const p2 = await c2.newPage(); p2.setDefaultTimeout(5000);
    await p2.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
    await p2.waitForTimeout(400);
    const fit = await p2.evaluate(() => {
      const pager = document.getElementById('p-pager').getBoundingClientRect();
      const inside = el => { const r = el.getBoundingClientRect(); return r.top >= pager.top - 1 && r.bottom <= pager.bottom + 1 && r.left >= 0 && r.right <= innerWidth; };
      return {
        icons: [...document.querySelectorAll('[data-page="1"] .p-icon')].map(inside),
        widget: inside(document.querySelector('[data-page="1"] .p-widget')),
        plain: (() => { const r = document.querySelector('.p-plain').getBoundingClientRect(); const d = document.querySelector('.p-dock').getBoundingClientRect(); return r.width > 0 && r.left >= 0 && r.right <= innerWidth && r.bottom <= d.top + 1; })(),
        overflowX: document.documentElement.scrollWidth > innerWidth,
      };
    });
    check(name + ': all four Home icons are visible without scrolling', fit.icons.length === 4 && fit.icons.every(Boolean), fit);
    check(name + ': widget fully visible', fit.widget, fit);
    check(name + ': plain version link visible', fit.plain, fit);
    check(name + ': no sideways overflow', !fit.overflowX, fit);
    const [mx, my] = await p2.$eval('[data-pdock][aria-label=Mail]', e => { const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; });
    await p2.touchscreen.tap(mx, my); await p2.waitForTimeout(750);
    const mail = await p2.evaluate(() => {
      const body = document.querySelector('.p-sheet .p-body');
      const to = [...document.querySelectorAll('.p-sheet .p-field-row span')].pop();
      return { overflow: body.scrollWidth > body.clientWidth, toClipped: to.scrollWidth > to.clientWidth };
    });
    check(name + ': mail does not overflow or clip the address', !mail.overflow && !mail.toClipped, mail);
    await c2.close();
  }

  await browser.close();

  if (failures.length) { console.log('PHONE GESTURES FAILED:\n - ' + failures.join('\n - ')); process.exit(1); }
  console.log('PHONE GESTURES OK');
})().catch(e => { console.log('PHONE GESTURES CRASHED: ' + e.message); process.exit(2); });
