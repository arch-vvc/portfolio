// Phone layout: an iPhone drawn inside the real screen, inset from every edge so the
// gestures the phone keeps for itself never reach it. No fetch, no modules: works from disk.
// Folder, thread, tab and music content is shared with the laptop code (desktop.js, apps.js).
(function () {
  var phone = document.getElementById("phone");
  if (!phone) return;

  var data = window.DESKTOP_DATA || { folders: {}, rowsFor: function () { return []; } };
  var shared = window.DESKTOP_SHARED || { threads: [], tabs: [], covers: [], albums: [], esc: String };
  var cfg = window.SITE_CONFIG || {};
  var esc = shared.esc;

  var pager = document.getElementById("p-pager");
  var track = document.getElementById("p-track");
  var hint = document.getElementById("p-hint");
  var dots = document.querySelectorAll("[data-pdot]");
  var sheets = document.getElementById("p-sheets");
  var inertParts = [pager, hint, document.getElementById("p-dots"), document.querySelector(".p-dock")];

  var ICON = {
    close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    back: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    send: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12L20 4l-6 16-3-7z" fill="currentColor"/></svg>',
    search: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 16l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    lock: '<svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true"><rect x="6" y="11" width="12" height="8" rx="2" fill="currentColor"/><path d="M9 11V8.500a3 3 0 0 1 6 0V11" fill="none" stroke="currentColor" stroke-width="1.800"/></svg>',
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.500v13l11-6.500z" fill="currentColor"/></svg>'
  };

  function file(name) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#g-file-' + name + '"/></svg>';
  }

  // ----- status bar clock and reminders -----
  var clock = document.getElementById("p-clock");
  function tick() {
    var d = new Date();
    var m = d.getMinutes();
    clock.textContent = (d.getHours() % 12 || 12) + ":" + (m < 10 ? "0" : "") + m;
  }
  tick();
  setInterval(tick, 15000);

  var boxes = document.querySelectorAll(".p-reminders input");
  var count = document.getElementById("p-count");
  for (var bi = 0; bi < boxes.length; bi++) {
    boxes[bi].addEventListener("change", function () {
      var left = 0;
      for (var i = 0; i < boxes.length; i++) if (!boxes[i].checked) left++;
      count.textContent = String(left);
    });
  }

  // ----- the two pages: Projects on the left, Home in the middle of the story -----
  var page = 1;
  var HINTS = ["swipe left to go back home", "swipe right to see projects"];

  function setPage(i, instant) {
    page = Math.max(0, Math.min(1, i));
    track.classList.remove("dragging");
    if (instant) track.classList.add("dragging");      // first paint: no slide in from the other page
    track.style.transform = "translateX(" + (-page * 50) + "%)";
    if (instant) {
      void track.offsetWidth;
      window.requestAnimationFrame(function () { track.classList.remove("dragging"); });
    }
    hint.textContent = HINTS[page];
    hint.setAttribute("data-dir", page === 0 ? "back" : "forward");
    for (var d = 0; d < dots.length; d++) {
      if (Number(dots[d].getAttribute("data-pdot")) === page) dots[d].setAttribute("aria-current", "true");
      else dots[d].removeAttribute("aria-current");
    }
  }

  // Past the first or last page the content follows the finger at a fraction of the distance,
  // like the rubber band on a real home screen.
  function rubber(dx) {
    if ((page === 0 && dx > 0) || (page === 1 && dx < 0)) return dx * 0.28;
    return dx;
  }

  var swipe = null;
  var quietUntil = 0;

  pager.addEventListener("pointerdown", function (e) {
    if (stack.length) return;
    if (e.pointerType === "mouse" && e.button !== 0) return;
    swipe = { id: e.pointerId, x: e.clientX, y: e.clientY, locked: false, dx: 0, lastX: e.clientX, lastT: e.timeStamp, v: 0 };
  });

  pager.addEventListener("pointermove", function (e) {
    if (!swipe || e.pointerId !== swipe.id) return;
    var dx = e.clientX - swipe.x;
    var dy = e.clientY - swipe.y;
    if (!swipe.locked) {
      if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
      if (Math.abs(dx) > Math.abs(dy) * 1.2) {
        swipe.locked = true;
        try { pager.setPointerCapture(e.pointerId); } catch (err) { /* touch already owns the pointer */ }
        track.classList.add("dragging");
      } else { swipe = null; return; }
    }
    var dt = e.timeStamp - swipe.lastT;
    if (dt > 0) swipe.v = (e.clientX - swipe.lastX) / dt;
    swipe.lastX = e.clientX;
    swipe.lastT = e.timeStamp;
    swipe.dx = dx;
    track.style.transform = "translateX(calc(" + (-page * 50) + "% + " + rubber(dx) + "px))";
  });

  function endSwipe(e) {
    if (!swipe || e.pointerId !== swipe.id) return;
    var s = swipe;
    swipe = null;
    if (!s.locked) return;
    quietUntil = Date.now() + 350;
    var w = pager.clientWidth;
    var go = 0;
    if (Math.abs(s.dx) > w * 0.2 || Math.abs(s.v) > 0.45) go = (s.dx > 0 || s.v > 0.45) ? -1 : 1;
    if (e.type === "pointercancel") go = 0;
    setPage(page + go);
  }
  pager.addEventListener("pointerup", endSwipe);
  pager.addEventListener("pointercancel", endSwipe);

  // A swipe must not also count as a tap on the icon under the finger.
  pager.addEventListener("click", function (e) {
    if (Date.now() < quietUntil) { e.stopPropagation(); e.preventDefault(); }
  }, true);

  for (var di = 0; di < dots.length; di++) {
    dots[di].addEventListener("click", function () { setPage(Number(this.getAttribute("data-pdot"))); });
  }

  document.addEventListener("keydown", function (e) {
    if (!phone.offsetParent) return;
    if (e.key === "Escape" && stack.length) { closeSheet(stack[stack.length - 1]); return; }
    if (stack.length) return;
    if (e.key === "ArrowLeft") setPage(0);
    if (e.key === "ArrowRight") setPage(1);
  });

  // ----- sheets: every folder and app opens from the icon that was tapped -----
  var stack = [];

  function setInert(on) {
    for (var i = 0; i < inertParts.length; i++) {
      if (on) inertParts[i].setAttribute("inert", "");
      else inertParts[i].removeAttribute("inert");
    }
  }

  function aim(el, origin) {
    var s = sheets.getBoundingClientRect();
    var o = origin ? origin.getBoundingClientRect() : s;
    el.style.setProperty("--ox", (o.left + o.width / 2 - (s.left + s.width / 2)) + "px");
    el.style.setProperty("--oy", (o.top + o.height / 2 - (s.top + s.height / 2)) + "px");
    el.style.setProperty("--os", String(Math.max(0.12, Math.min(0.5, o.width / s.width))));
  }

  function openSheet(opts) {
    var el = document.createElement("section");
    el.className = "p-sheet is-opening no-anim";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", opts.title);
    el.innerHTML =
      '<div class="p-sheet-head"><button class="p-close" type="button" aria-label="Close">' + ICON.close + "</button>" +
      "<h2>" + esc(opts.title) + "</h2>" + (opts.action || "") + "</div>" +
      '<div class="p-body"></div><div class="p-home-bar" aria-hidden="true"></div>';
    el.querySelector(".p-body").appendChild(opts.body);
    if (opts.action) el.classList.add("has-action");
    sheets.appendChild(el);
    var rec = { el: el, origin: opts.origin, back: null, body: el.querySelector(".p-body"), title: el.querySelector("h2") };
    aim(el, opts.origin);
    void el.offsetWidth;
    el.classList.remove("no-anim");
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { el.classList.remove("is-opening"); });
    });
    stack.push(rec);
    setInert(true);
    el.querySelector(".p-close").addEventListener("click", function () { closeSheet(rec); });
    wireHomeBar(rec);
    wireEdgeBack(rec);
    el.querySelector(".p-close").focus({ preventScroll: true });
    return rec;
  }

  function closeSheet(rec) {
    var at = stack.indexOf(rec);
    if (at === -1) return;
    stack.splice(at, 1);
    rec.el.style.transform = "";
    rec.el.style.opacity = "";
    rec.el.classList.remove("dragging");
    aim(rec.el, rec.origin && document.body.contains(rec.origin) ? rec.origin : null);
    rec.el.classList.add("is-closing");
    if (!stack.length) {
      setInert(false);
      if (rec.origin && rec.origin.closest) {
        var focusable = rec.origin.closest("button");
        if (focusable) focusable.focus({ preventScroll: true });
      }
    }
    window.setTimeout(function () { if (rec.el.parentNode) rec.el.parentNode.removeChild(rec.el); }, 480);
  }

  // Swipe up from the bar at the bottom to go home. The sheet follows the finger and shrinks.
  function wireHomeBar(rec) {
    var bar = rec.el.querySelector(".p-home-bar");
    var st = null;
    bar.addEventListener("pointerdown", function (e) {
      st = { id: e.pointerId, y: e.clientY, dy: 0, lastY: e.clientY, lastT: e.timeStamp, v: 0 };
      try { bar.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
      rec.el.classList.add("dragging");
    });
    bar.addEventListener("pointermove", function (e) {
      if (!st || e.pointerId !== st.id) return;
      var dy = Math.min(0, e.clientY - st.y);
      var dt = e.timeStamp - st.lastT;
      if (dt > 0) st.v = (e.clientY - st.lastY) / dt;
      st.lastY = e.clientY;
      st.lastT = e.timeStamp;
      st.dy = dy;
      var progress = Math.min(1, -dy / 360);
      rec.el.style.transform = "translateY(" + dy + "px) scale(" + (1 - progress * 0.2) + ")";
      rec.el.style.opacity = String(1 - progress * 0.35);
    });
    function end(e) {
      if (!st || e.pointerId !== st.id) return;
      var s = st;
      st = null;
      rec.el.classList.remove("dragging");
      if (e.type !== "pointercancel" && (-s.dy > 90 || s.v < -0.5)) { closeSheet(rec); return; }
      rec.el.style.transform = "";
      rec.el.style.opacity = "";
    }
    bar.addEventListener("pointerup", end);
    bar.addEventListener("pointercancel", end);
  }

  // Swipe right from the left edge of the sheet to go back, where a sheet has somewhere to go back to.
  function wireEdgeBack(rec) {
    var st = null;
    rec.el.addEventListener("pointerdown", function (e) {
      if (!rec.back) return;
      var r = rec.el.getBoundingClientRect();
      if (e.clientX - r.left > 28) return;
      st = { id: e.pointerId, x: e.clientX };
    });
    rec.el.addEventListener("pointermove", function (e) {
      if (!st || e.pointerId !== st.id) return;
      if (e.clientX - st.x > 70) { st = null; rec.back(); }
    });
    rec.el.addEventListener("pointerup", function () { st = null; });
    rec.el.addEventListener("pointercancel", function () { st = null; });
  }

  function node(html, cls) {
    var d = document.createElement("div");
    if (cls) d.className = cls;
    d.innerHTML = html;
    return d;
  }

  // ----- folders (shared data with the laptop) -----
  function rowHtml(r) {
    var name = esc(r.name);
    if (r.kind === "folder") {
      return '<button class="p-row" type="button" data-open="' + esc(r.open) + '">' + file("folder") + '<span class="p-row-name">' + name + '</span><span class="p-row-meta">Folder</span></button>';
    }
    if (r.href) {
      var icon = r.kind === "mov" ? "mov" : r.kind === "link" ? "link" : "web";
      var meta = r.kind === "mov" ? "Video" : (r.date || "");
      return '<a class="p-row" href="' + esc(r.href) + '" target="_blank" rel="noopener">' + file(icon) + '<span class="p-row-name">' + name + '</span><span class="p-row-meta">' + esc(meta) + "</span></a>";
    }
    return '<div class="p-row off">' + file("mov") + '<span class="p-row-name">' + name + '</span><span class="p-row-meta">Coming soon</span></div>';
  }

  function folderSheet(key, origin) {
    var f = data.folders[key];
    if (!f) return;
    var body;
    if (f.bare) {
      body = node('<p>' + esc(f.summary[0]) + "</p>", "p-empty");
    } else {
      var html = '<div class="p-sum">';
      for (var i = 0; i < f.summary.length; i++) html += "<p>" + esc(f.summary[i]) + "</p>";
      html += "</div>";
      var rows = data.rowsFor(key);
      var list = "";
      for (var r = 0; r < rows.length; r++) if (rows[r].kind !== "txt") list += rowHtml(rows[r]);
      if (list) html += '<div class="p-rows">' + list + "</div>";
      body = node(html);
    }
    var rec = openSheet({ title: f.title, body: body, origin: origin });
    var alias = rec.body.querySelectorAll("[data-open]");
    for (var a = 0; a < alias.length; a++) {
      (function (btn) {
        btn.addEventListener("click", function () { folderSheet(btn.getAttribute("data-open"), btn); });
      })(alias[a]);
    }
    return rec;
  }

  // ----- the CV: the same text as the laptop window -----
  function cvSheet(origin) {
    var source = document.querySelector("#pdf .page");
    var wrap = document.createElement("div");
    wrap.className = "p-cv";
    if (source) wrap.appendChild(source.cloneNode(true));
    openSheet({ title: "Archit_Rishabh_CV.pdf", body: wrap, origin: origin });
  }

  // ----- Mail: a drafted message; Send opens Gmail with the edited text -----
  function mailSheet(origin) {
    var body = node(
      '<div class="p-field-row"><span class="p-flabel">To:</span><span>' + esc(shared.to) + "</span></div>" +
      '<div class="p-field-row"><label for="p-subject">Subject:</label><input id="p-subject" type="text" value="' + esc(shared.subject) + '" autocomplete="off"></div>' +
      '<textarea class="p-mail-body" id="p-mailbody" aria-label="Message">' + esc(shared.body) + "</textarea>" +
      '<p class="p-hint-small">Send opens Gmail with this message ready. <a id="p-mailapp" href="' + esc(shared.mailtoUrl(shared.subject, shared.body)) + '">Use another mail app</a></p>');
    var action = '<a class="p-send" id="p-send" href="' + esc(shared.gmailUrl(shared.subject, shared.body)) + '" target="_blank" rel="noopener" aria-label="Send, opens Gmail with this message">' + ICON.send + "</a>";
    var rec = openSheet({ title: "New Message", body: body, origin: origin, action: action });
    var subject = rec.el.querySelector("#p-subject");
    var text = rec.el.querySelector("#p-mailbody");
    var send = rec.el.querySelector("#p-send");
    var app = rec.el.querySelector("#p-mailapp");
    function sync() {
      send.href = shared.gmailUrl(subject.value, text.value);
      app.href = shared.mailtoUrl(subject.value, text.value);
    }
    subject.addEventListener("input", sync);
    text.addEventListener("input", sync);
  }

  // ----- Messages: a list, then a conversation, like the real thing -----
  function messagesSheet(origin) {
    var rec = openSheet({ title: "Messages", body: document.createElement("div"), origin: origin });

    function showList() {
      rec.back = null;
      rec.title.textContent = "Messages";
      var html = '<h3 class="p-large">Messages</h3><div class="p-pill">' + ICON.search + "<span>Search</span></div>";
      for (var i = 0; i < shared.threads.length; i++) {
        var t = shared.threads[i];
        var last = t.lines[t.lines.length - 1];
        for (var q = t.lines.length - 1; q >= 0; q--) if (t.lines[q].text) { last = t.lines[q]; break; }
        html += '<button class="p-thread" type="button" data-thread="' + i + '"><span class="p-avatar">' + esc(t.initials) + "</span>" +
          '<span class="p-thread-meta"><span class="p-thread-name">' + esc(t.name) + '</span><span class="p-thread-when">' + esc(t.time) + "</span>" +
          '<span class="p-thread-preview">' + esc(last.text || last.title) + "</span></span></button>";
      }
      rec.body.innerHTML = html;
      var buttons = rec.body.querySelectorAll(".p-thread");
      for (var b = 0; b < buttons.length; b++) {
        (function (btn) { btn.addEventListener("click", function () { showThread(Number(btn.getAttribute("data-thread"))); }); })(buttons[b]);
      }
    }

    function showThread(i) {
      var t = shared.threads[i];
      rec.back = showList;
      rec.title.textContent = t.name;
      var html = '<button class="p-tab" type="button" id="p-back">' + ICON.back + "<span>Messages</span></button>" +
        '<div class="p-who"><span class="p-avatar">' + esc(t.initials) + "</span><span>" + esc(t.name) + "</span></div>" +
        '<div class="p-chat"><p class="p-time">' + esc(t.time) + "</p>";
      for (var k = 0; k < t.lines.length; k++) {
        var l = t.lines[k];
        if (l.link) {
          html += '<a class="p-bubble" href="' + esc(l.link) + '"' + (l.link.indexOf("mailto:") === 0 ? "" : ' target="_blank" rel="noopener"') +
            "><strong>" + esc(l.title) + "</strong><span>" + esc(l.host) + "</span></a>";
        } else {
          html += '<p class="p-bubble">' + esc(l.text) + "</p>";
        }
      }
      html += '</div><div class="p-msg-input" aria-hidden="true"><span class="p-field">iMessage</span></div>';
      rec.body.innerHTML = html;
      rec.body.scrollTop = 0;
      rec.body.querySelector("#p-back").addEventListener("click", showList);
    }

    showList();
  }

  // ----- Safari: GitHub and LinkedIn open for real, the rest wait for their links -----
  function safariSheet(origin) {
    var tabs = shared.tabs;
    var chips = "";
    for (var i = 0; i < tabs.length; i++) {
      var t = tabs[i];
      var inner = t.fav + "<span>" + esc(t.name) + "</span>";
      if (t.href) chips += '<a class="p-tab" href="' + esc(t.href) + '" target="_blank" rel="noopener">' + inner + "</a>";
      else chips += '<button class="p-tab' + (i === 1 ? " selected" : "") + '" type="button" data-tab="' + i + '">' + inner + "</button>";
    }
    var body = node('<div class="p-address">' + ICON.lock + '<span id="p-url"></span></div><div class="p-tabs">' + chips + '</div><div id="p-tabpage"></div>');
    var rec = openSheet({ title: "Safari", body: body, origin: origin });
    var url = rec.el.querySelector("#p-url");
    var pageEl = rec.el.querySelector("#p-tabpage");

    function show(i) {
      var t = tabs[i];
      url.textContent = t.host;
      if (t.page === "krillion") {
        pageEl.innerHTML = cfg.krillionImage
          ? '<div class="p-shot"><img src="' + esc(cfg.krillionImage) + '" alt="My One in a Krillion result in the Krillion game"></div>'
          : '<div class="p-stub"><div class="p-frame">My One in a Krillion goes here.</div></div>';
      } else {
        pageEl.innerHTML = '<div class="p-stub"><div class="p-frame small">' + t.fav + "</div><p>" + esc(t.name) + " is coming soon.</p></div>";
      }
    }
    var buttons = rec.el.querySelectorAll("button.p-tab");
    for (var b = 0; b < buttons.length; b++) {
      (function (btn) {
        btn.addEventListener("click", function () {
          for (var k = 0; k < buttons.length; k++) buttons[k].classList.remove("selected");
          btn.classList.add("selected");
          show(Number(btn.getAttribute("data-tab")));
        });
      })(buttons[b]);
    }
    show(1);
  }

  // ----- Music and Photos -----
  function cards(list, cls) {
    var out = "";
    for (var i = 0; i < list.length; i++) {
      out += '<div class="p-card ' + cls + '"><img src="' + esc(list[i]) + '" alt="Drake"><span class="p-card-title">Drake</span><span class="p-card-sub">Drake</span></div>';
    }
    return out;
  }

  function musicSheet(origin) {
    var body = node('<h3 class="p-large">Home</h3><h3 class="p-h3">On Repeat</h3><div class="p-cards">' + cards(shared.covers, "") +
      '</div><h3 class="p-h3">Recently Played</h3><div class="p-cards">' + cards(shared.albums, "small") +
      '</div><div class="p-mini"><img src="' + esc(shared.covers[0]) + '" alt="Drake"><span>Drake<br>Drake</span>' + ICON.play + "</div>");
    openSheet({ title: "Music", body: body, origin: origin });
  }

  function photosSheet(origin) {
    var cells = "";
    for (var i = 0; i < 18; i++) cells += "<i></i>";
    openSheet({ title: "Photos", body: node('<h3 class="p-large">Library</h3><div class="p-photo-grid">' + cells + '</div><p class="p-note">Photos are on their way.</p>'), origin: origin });
  }

  // ----- wiring: icons on the pages, then the dock -----
  var APPS = {
    "Mail": mailSheet, "Messages": messagesSheet, "Safari": safariSheet,
    "Music": musicSheet, "Photos": photosSheet,
    "Trash": function (origin) { folderSheet("trash", origin); },
    "Claude": function () { /* nothing here yet, like the laptop */ }
  };

  var icons = document.querySelectorAll(".p-icon");
  for (var ii = 0; ii < icons.length; ii++) {
    (function (icon) {
      icon.addEventListener("click", function () {
        if (stack.length) return;
        var origin = icon.querySelector(".p-tile") || icon;
        var key = icon.getAttribute("data-pfolder");
        if (key) folderSheet(key, origin);
        else if (icon.getAttribute("data-pfile") === "cv") cvSheet(origin);
      });
    })(icons[ii]);
  }

  var dockItems = document.querySelectorAll("[data-pdock]");
  for (var dk = 0; dk < dockItems.length; dk++) {
    (function (btn) {
      btn.addEventListener("click", function () {
        if (stack.length) return;
        var open = APPS[btn.getAttribute("aria-label")];
        if (open) open(btn);
      });
    })(dockItems[dk]);
  }

  setPage(1, true);
})();
