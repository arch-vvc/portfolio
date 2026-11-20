# Phone layout: progress

Branch: claude/phone-layout (based on claude/layout-trash-zoom, not yet on main)
Rule: never push to main. Council decides if it is done.

## Decisions (20 Nov 2026)
- Phone UI lives in a frame inset from the real screen edges so it does not fight iOS gestures.
- Home page (black wallpaper): Reminders widget, the three internship folders and the CV file.
  Hint at the bottom: "swipe right to see projects". Dock unchanged (7 icons).
- Projects page sits to the LEFT of home, as on an iPhone, so swiping right reveals it.
- Folders open as full screen sheets that grow out of the tapped icon. Swipe up from the home bar closes.
- Content is reused from the laptop site: folder data (desktop.js), app data (apps.js), CV markup.

## Tasks
1. [x] T1 Checks first. Goal: tests/test_phone.py fails for the right reasons. Done when: new tests exist and fail. Files: tests/test_phone.py
2. [x] T2 Share data. Goal: phone code can read folder, thread, tab and music data. Done when: window.DESKTOP_DATA and window.DESKTOP_SHARED exist. Files: desktop.js, apps.js
3. [x] T3 Markup and styles. Goal: frame, status bar, two pages, widget, dock, hint, dots. Done when: static checks pass and 390 by 844 screenshot looks right. Files: index.html, desktop.css
4. [x] T4 Gestures. Goal: page swipe with rubber band, tap to open with zoom from icon, swipe up from home bar to close, edge swipe back in Messages. Done when: touch tests pass in a mobile browser. Files: phone.js
5. [x] T5 Sheets. Goal: folder, CV, Mail, Messages, Safari, Music, Photos, Trash. Done when: each opens and closes. Files: phone.js, desktop.css
6. [ ] T6 Council. Goal: Engineer and Sceptic judge "is the phone site done", chairman verdict. Done when: verdict and top 3 actions recorded below.
7. [ ] T7 Fix the top actions, push branch, give preview link. Never main.

## Status log
- 20 Nov 2026: T1 to T5 done. 118 static checks pass. Touch tests in an emulated iPhone pass (swipe, rubber band, tap to open, swipe up to close, all dock apps).
- Found and fixed while building: the narrow screen media rule sat above the base .phone rule, so the phone never showed.

## Fix round 1 (20 Nov 2026)
Done: noscript redirect to plain.html, visible Plain version link on Home, name and role on Home, Demo rows hidden until there is a video, Safari shows only tabs with content, Claude tap shakes, project pages link back to the portfolio and the plain version, off screen page inert, touch-action on sheets so the Messages edge swipe works, taller swipe up zone, bigger dots, dock separator, hint arrow spacing, Escape and arrow keys fixed (offsetParent bug), real browser gesture test added (tests/phone_gestures.js). 128 checks pass.

## Council verdict (round 1, 20 Nov 2026)
Engineer: NOT DONE. Sceptic: NOT DONE. Chairman: NOT DONE.
Top 3 actions:
1. Make it feel finished: hide Demo rows with no video, no Safari stub on first open, Claude tap gives feedback, name and role visible on Home.
2. Make it safe: visible Plain version link on the phone, noscript fallback to plain.html, project pages link back to the portfolio, off screen page inert.
3. Fix the gestures: edge swipe back in Messages is cancelled by the browser (needs touch-action on the sheet), wider swipe up zone, plus a real browser gesture test. Then run the council again.
Parked (owner decisions): CV is one tap behind an icon (kept as the owner's layout), Cricket line about coaching juniors is from the original site but not on the CV.

## Council round 2 (20 Nov 2026)
Engineer: NOT DONE (one real bug: a second finger left the pages stuck mid drag; small focus and layout items).
Sceptic: NOT DONE (no blockers; Photos blank tiles, Drake labels, Trash text, no CV PDF, Mail clipped at 320).
Chairman: NOT DONE at the time of review. All engineering findings fixed in fix round 2 (second finger and cancel, nested sheet inert and focus, Escape in text fields, Photos message, role labels on Home, Mail wrapping, Plain version link moved to the footer, Home fits at 320 by 568 and in landscape). 128 checks pass, including the real browser test at 320, 360, 390, 430 and landscape.
Not re-reviewed by the council. Maximum fix rounds reached, so the rest is for the owner.

## Owner decisions (not mine to make)
1. Music says "Drake" on every title, artist and cover (asked for). Keep it in front of recruiters?
2. Trash says "Nothing to say here, everything I make is sexy." (asked for). Keep it in front of recruiters?
3. The CV sheet is titled Archit_Rishabh_CV.pdf but there is no PDF to download. Add one (without the phone number) or rename it.
4. The CV is one tap behind an icon on Home, not on the page itself. Say if you want the CV text on Home.
5. Cricket says "Coached 15 juniors to a final", which is on the original site but not on the CV.
6. Not tested on a real iPhone: Safari's own edge swipe, the Gmail send link, and new tab behaviour.

## Owner changes after the merge (20 Nov 2026), branch claude/phone-v2
- Dock is four icons cut from the owner's iPhone screenshot: Mail, Music, Messages, Safari. No Trash, Photos, Claude or Phone icon on the phone.
- Mail opens the drafted email directly (replaced the Phone app on 20 Nov 2026 at the owner's request). No phone number appears anywhere.
- Home (internships) is first; Projects is one swipe LEFT. Hints: "swipe left to see projects" and "swipe right to go back home".
- Folder icons are stylised first letters (W, N, O, I, T, C, E, G, D, E, C). The CV keeps its document thumbnail.
- Recently Played shows Take Care, Habibti, Views, Nothing Was The Same (laptop and phone).
- Plain version link removed from the phone. No JavaScript still redirects to plain.html.
- 129 checks pass, including the real browser test at 320, 360, 390, 430 and landscape.

## After the phone merge (20 Nov 2026), branch claude/cv-pdf
- Added assets/Archit_Rishabh_CV.pdf (one page, no phone number), built by scripts/make_cv_pdf.js from the CV text in index.html. Download buttons: laptop Preview toolbar, phone CV sheet, plain page (cvPath set).
- Cache busting: scripts and stylesheet carry ?v=20261120b so a phone cannot keep old copies. Bump the value when you change them.
- Trash stays as is (owner decision).
- Music: waiting for the owner to say what to change.
- Owner said the phone did not change after the merge. The live site was verified serving the new version; preview links are frozen snapshots and never update.
