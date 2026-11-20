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

## Council verdict
(pending)
