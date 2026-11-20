// Behaviour for the desktop home page. No fetch, no modules: works when opened from disk.
// The CV window and the Finder windows share one small window manager.
(function () {
  var DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var REPO = "https://github.com/arch-vvc/";
  var TODAY = "20 Nov 2026";

  var cfg = window.SITE_CONFIG || {};
  var demos = cfg.demos || {};

  // What each folder holds. A folder always gets Summary.txt. A demo key adds Demo.mov
  // (live as soon as its Loom link is set in site.config.js) and a repo adds a GitHub row.
  var FOLDERS = {
    "tender-tracker": {
      title: "Tender Tracker", demo: "tender",
      summary: [
        "Reads 33 Indian state eProcurement portals every day, keeps the IT tenders that fit the bidder and emails the bid team a digest with an Excel sheet.",
        "Used by the company, resulting in an 8 figure contract now underway.",
        "About 3,900 new open tenders a day. 366 tests. Built at Windstream Technologies."
      ],
      rows: [{ kind: "page", name: "Case study.html", href: "projects/tender-tracker.html", date: "17 Nov 2026" }]
    },
    "call-qa": {
      title: "Call QA", demo: "callqa", repo: "voice-agent-call-qa", repoDate: "18 Nov 2026",
      summary: [
        "Simulated callers, including confused, Hinglish and adversarial ones, talk to an agent built from a client's SOP. A judge marks the exact turn where a call fails.",
        "Live run: the first prompt passed 0 of 5 callers, the fixed prompt passed 4 of 5.",
        "428 tests."
      ],
      rows: [{ kind: "page", name: "Project page.html", href: "projects/call-qa.html", date: "17 Nov 2026" }]
    },
    "exception-triage": {
      title: "Exception Triage", demo: "triage", repo: "invoice-exception-triage", repoDate: "17 Nov 2026",
      summary: [
        "Matches invoices, purchase orders and payments from Tally and Zoho Books exports, then lists every mismatch with the rupees at risk, the exact source rows and one plain English sentence.",
        "Caught 16 of 16 planted exceptions across 8 types. 505 tests."
      ],
      rows: [{ kind: "page", name: "Project page.html", href: "projects/exception-triage.html", date: "17 Nov 2026" }]
    },
    "gtm-agent": {
      title: "gtm_agent", demo: "gtm", repo: "gtm_agent", repoDate: "17 Nov 2026",
      summary: [
        "Give it a startup's URL. It returns the cluster, the demo to send, the deployment pain the company's customers likely have, three tailoring changes and a pitch note of 150 words or fewer that names only things found on the company's own site.",
        "FastAPI, Redis, PostgreSQL and Docker. 632 tests."
      ],
      rows: [{ kind: "page", name: "Project page.html", href: "projects/gtm-agent.html", date: "17 Nov 2026" }]
    },
    "capstone": {
      title: "Immunological Supply Chain", demo: "capstone", repo: "immunological_supply_chain_management", repoDate: "5 Oct 2026",
      summary: [
        "A 28 stage ML and RL pipeline that models supply chain resilience on immune principles: GCN anomaly detection, a PPO rerouting agent and a FAISS memory of past disruptions over 240K+ records.",
        "Blind backtest on real USAID shipment data flagged the Haiti 2010 disruption. Recommended vendors beat actual procurement on late rate in 71% of 76 cases.",
        "Paper submitted. Every headline number reproduces bit for bit from a fresh clone."
      ],
      rows: []
    },
    "windstream": {
      title: "Windstream",
      summary: [
        "Founder's Office Intern. Ran a site feasibility analysis across 100+ renewable energy installations (terrain, grid access, cost) to guide capital allocation for a ₹20 crore project.",
        "Built an energy yield model on 35,000+ hourly weather records. A hybrid turbine redesign lifts output 20 to 25% at windy sites and loses up to 13% elsewhere, so spend moved to panel and battery upgrades.",
        "Built the tender tracker. Supported the C suite on proposals and client presentations."
      ],
      rows: [{ kind: "folder", name: "Tender Tracker", open: "tender-tracker" }]
    },
    "nexturn": {
      title: "NexTurn",
      summary: [
        "Data and AI Strategy Intern. Built a RAG based document analysis and visualisation pipeline for a $150M firm, cutting client insight generation time by 93%.",
        "Parsed, chunked and embedded 10+ simultaneous unstructured documents into a vector index, and used structured LLM outputs to turn key metrics into automated visual reports."
      ],
      rows: []
    },
    "ooh": {
      title: "OOH Advertising",
      summary: [
        "Founder's Office Intern. Analysed crowd flow and visibility across 50+ Delhi Metro stations (about 30 lakh daily commuters) to build a site prioritisation framework for outdoor advertising placements.",
        "Created pitch decks supporting tender submissions across the South and East Delhi corridors."
      ],
      rows: []
    },
    "drishtikon": {
      title: "Drishtikon '26",
      summary: [
        "National Case Competition Finalist, IIMS Pune.",
        "Reached the national final from 750+ applicants on corporate restructuring and marketing cases."
      ],
      rows: []
    },
    "e-cell": {
      title: "E-Cell",
      summary: [
        "PESU Entrepreneurship Cell, Organising Committee.",
        "Built a 20 case business simulation from real corporate problems and ran it end to end for 100+ participants."
      ],
      rows: []
    },
    "cricket": {
      title: "Cricket",
      summary: [
        "Won the Cottonian Shield and the KSCA BT Ramaiah Shield, Best Wicketkeeper in both.",
        "Coached 15 juniors to a final. Played football and basketball for PES University."
      ],
      rows: []
    }
  };

  var SIDEBAR = [
    { items: [["Recents", "recents"], ["Shared", "shared"]] },
    { head: "Favorites", items: [["Downloads", "downloads"], ["Applications", "apps"], ["Desktop", "desktop"], ["Documents", "docs"]] },
    { head: "Locations", items: [["iCloud Drive", "icloud"], ["archit", "home"]] }
  ];

  var desktop = document.getElementById("desktop");
  if (!desktop) return;

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // ----- clock in the menu bar -----
  var clock = document.getElementById("clock");
  function tick() {
    var d = new Date();
    var h = d.getHours() % 12 || 12;
    var m = d.getMinutes();
    clock.textContent = DAYS[d.getDay()] + " " + d.getDate() + " " + MONTHS[d.getMonth()] +
      " " + h + ":" + (m < 10 ? "0" : "") + m + " " + (d.getHours() < 12 ? "AM" : "PM");
  }
  tick();
  setInterval(tick, 15000);

  // ----- reminders count -----
  var boxes = document.querySelectorAll(".reminders input");
  var count = document.getElementById("reminder-count");
  function updateCount() {
    var left = 0;
    for (var i = 0; i < boxes.length; i++) if (!boxes[i].checked) left++;
    count.textContent = String(left);
  }
  for (var b = 0; b < boxes.length; b++) boxes[b].addEventListener("change", updateCount);

  // ----- window manager -----
  var dock = document.querySelector(".dock");
  var trash = dock.lastElementChild;
  var appName = document.getElementById("app-name");
  var previewOnly = document.querySelectorAll(".preview-only");
  var order = [];        // open windows, back to front
  var all = [];          // every registered window

  function isOpen(w) { return !w.el.classList.contains("is-gone") && !w.minimised; }

  function refresh() {
    for (var i = 0; i < order.length; i++) order[i].el.style.zIndex = String(20 + i);
    var front = null;
    for (var j = order.length - 1; j >= 0; j--) if (isOpen(order[j])) { front = order[j]; break; }
    var app = front ? front.app : "Finder";
    appName.textContent = app;
    for (var k = 0; k < previewOnly.length; k++) previewOnly[k].style.display = app === "Preview" ? "" : "none";
  }

  function focusWin(w) {
    var at = order.indexOf(w);
    if (at !== -1) order.splice(at, 1);
    order.push(w);
    refresh();
  }

  function removeDockSlot(w) {
    if (w.slot && w.slot.parentNode) w.slot.parentNode.removeChild(w.slot);
    w.slot = null;
  }

  function openWin(w) {
    if (w.minimised) { restoreWin(w); return; }
    var wasGone = w.el.classList.contains("is-gone");
    if (wasGone) {
      w.el.classList.add("is-opening");
      w.el.classList.remove("is-gone");
      void w.el.offsetWidth;
      w.el.classList.remove("is-opening");
    }
    focusWin(w);
    w.el.focus({ preventScroll: true });
  }

  function closeWin(w) {
    w.el.classList.remove("is-full", "is-minimising");
    w.el.classList.add("is-gone");
    removeDockSlot(w);
    w.minimised = false;
    var at = order.indexOf(w);
    if (at !== -1) order.splice(at, 1);
    refresh();
  }

  function minimiseWin(w) {
    w.el.classList.remove("is-full");
    if (!w.slot) {
      w.slot = document.createElement("button");
      w.slot.type = "button";
      w.slot.className = "dock-item dock-min" + (w.dark ? " dark" : "");
      w.slot.setAttribute("aria-label", "Restore " + w.title);
      w.slot.innerHTML = '<span class="thumb" aria-hidden="true"></span>';
      w.slot.addEventListener("click", function (e) { e.stopPropagation(); restoreWin(w); });
      dock.insertBefore(w.slot, trash);
    }
    var r = w.el.getBoundingClientRect();
    var t = w.slot.getBoundingClientRect();
    w.el.style.setProperty("--dx", (t.left + t.width / 2 - (r.left + r.width / 2)) + "px");
    w.el.style.setProperty("--dy", (t.top + t.height / 2 - (r.top + r.height / 2)) + "px");
    w.el.classList.add("is-minimising");
    w.minimised = true;
    refresh();
  }

  function restoreWin(w) {
    w.el.classList.remove("is-minimising");
    removeDockSlot(w);
    w.minimised = false;
    focusWin(w);
    w.el.focus({ preventScroll: true });
  }

  function toggleFull(w) { w.el.classList.toggle("is-full"); }

  var drag = null;
  function register(el, title, dark) {
    var w = { el: el, title: title, dark: !!dark, app: el.getAttribute("data-app") || "Finder", slot: null, minimised: false };
    all.push(w);
    el.addEventListener("pointerdown", function () { focusWin(w); }, true);

    var buttons = el.querySelectorAll("[data-action]");
    for (var i = 0; i < buttons.length; i++) {
      (function (btn) {
        btn.addEventListener("click", function (e) {
          e.stopPropagation();
          var a = btn.getAttribute("data-action");
          if (a === "close") closeWin(w);
          else if (a === "minimise") minimiseWin(w);
          else toggleFull(w);
        });
      })(buttons[i]);
    }

    var handles = el.querySelectorAll("[data-drag]");
    for (var h = 0; h < handles.length; h++) {
      (function (handle) {
        handle.addEventListener("dblclick", function (e) {
          if (e.target.closest && e.target.closest(".lights")) return;
          toggleFull(w);
        });
        handle.addEventListener("pointerdown", function (e) {
          if (el.classList.contains("is-full")) return;
          if (e.target.closest && e.target.closest(".lights")) return;
          var r = el.getBoundingClientRect();
          drag = { w: w, handle: handle, x: e.clientX - r.left, y: e.clientY - r.top };
          el.classList.add("dragging");
          handle.setPointerCapture(e.pointerId);
        });
        handle.addEventListener("pointermove", function (e) {
          if (!drag || drag.handle !== handle) return;
          var bar = document.querySelector(".menubar").getBoundingClientRect().height;
          var x = Math.min(Math.max(e.clientX - drag.x, -el.offsetWidth + 120), window.innerWidth - 120);
          var y = Math.min(Math.max(e.clientY - drag.y, bar), window.innerHeight - 60);
          el.style.left = x + "px";
          el.style.top = y + "px";
        });
        function end(e) {
          if (!drag || drag.handle !== handle) return;
          drag = null;
          el.classList.remove("dragging");
          try { handle.releasePointerCapture(e.pointerId); } catch (err) { /* already released */ }
        }
        handle.addEventListener("pointerup", end);
        handle.addEventListener("pointercancel", end);
      })(handles[h]);
    }
    return w;
  }

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    for (var i = order.length - 1; i >= 0; i--) {
      if (order[i].el.classList.contains("is-full")) { order[i].el.classList.remove("is-full"); return; }
    }
  });

  // ----- the CV window (already in the page) -----
  var cvWin = register(document.getElementById("cv-window"), "Archit_Rishabh_CV.pdf", false);
  order.push(cvWin);

  // ----- Finder windows, built on first click -----
  var finders = {};

  function sizeOf(chars) { return Math.max(1, Math.round(chars / 1024)) + " KB"; }

  function rowsFor(key) {
    var f = FOLDERS[key];
    var text = f.summary.join(" ");
    var rows = [{ kind: "txt", name: "Summary.txt", date: TODAY, size: sizeOf(text.length), text: f.summary, selected: true }];
    if (f.demo) {
      var url = demos[f.demo];
      rows.push(url
        ? { kind: "mov", name: "Demo.mov", date: TODAY, size: "Video", href: url }
        : { kind: "mov", name: "Demo.mov", date: "Coming soon", size: "Soon", text: ["The demo video for this project is being recorded."] });
    }
    if (f.repo) rows.push({ kind: "link", name: "GitHub repo", date: f.repoDate, size: "Link", href: REPO + f.repo });
    return rows.concat(f.rows || []);
  }

  function sidebarHtml() {
    var out = "";
    for (var g = 0; g < SIDEBAR.length; g++) {
      out += '<div class="side-group">';
      if (SIDEBAR[g].head) out += '<p class="side-head">' + esc(SIDEBAR[g].head) + "</p>";
      for (var i = 0; i < SIDEBAR[g].items.length; i++) {
        var it = SIDEBAR[g].items[i];
        out += '<p class="side-item"><svg viewBox="0 0 24 24"><use href="#g-side-' + it[1] + '"/></svg><span>' + esc(it[0]) + "</span></p>";
      }
      out += "</div>";
    }
    return out;
  }

  function rowHtml(r, i) {
    var icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#g-file-' +
      (r.kind === "txt" ? "txt" : r.kind === "mov" ? "mov" : r.kind === "link" ? "link" : r.kind === "page" ? "web" : "folder") + '"/></svg>';
    var inner = '<span class="fname">' + icon + "<span>" + esc(r.name) + '</span></span><span class="fdate">' +
      esc(r.date || "") + '</span><span class="fsize">' + esc(r.size || (r.kind === "page" ? "Web page" : "Folder")) + "</span>";
    if (r.href) return '<li><a class="frow" href="' + esc(r.href) + '" target="_blank" rel="noopener">' + inner + "</a></li>";
    return '<li><button class="frow' + (r.selected ? " selected" : "") + '" type="button" data-row="' + i + '">' + inner + "</button></li>";
  }

  function paneHtml(name, lines) {
    var out = '<h3>' + esc(name) + "</h3>";
    for (var i = 0; i < lines.length; i++) out += "<p>" + esc(lines[i]) + "</p>";
    return out;
  }

  function buildFinder(key) {
    var f = FOLDERS[key];
    var rows = rowsFor(key);
    var el = document.createElement("section");
    el.className = "window finder is-gone";
    el.setAttribute("data-app", "Finder");
    el.setAttribute("tabindex", "-1");
    el.setAttribute("aria-label", f.title);

    var rowsHtml = "";
    for (var i = 0; i < rows.length; i++) rowsHtml += rowHtml(rows[i], i);

    el.innerHTML =
      '<div class="lights finder-lights">' +
        '<button class="light close" type="button" data-action="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
        '<button class="light minimise" type="button" data-action="minimise" aria-label="Minimise"><span aria-hidden="true">&minus;</span></button>' +
        '<button class="light zoom" type="button" data-action="fullscreen" aria-label="Full screen"><span aria-hidden="true">&#x2922;</span></button>' +
      "</div>" +
      '<div class="drag-corner" data-drag></div>' +
      '<aside class="finder-side" aria-hidden="true">' + sidebarHtml() + "</aside>" +
      '<div class="finder-main">' +
        '<div class="titlebar finder-bar" data-drag>' +
          '<span class="tool pill nav" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#g-back"/></svg><i></i><svg viewBox="0 0 24 24"><use href="#g-forward"/></svg></span>' +
          "<h2>" + esc(f.title) + "</h2>" +
          '<span class="tools-right" aria-hidden="true">' +
            '<span class="tool"><svg viewBox="0 0 24 24"><use href="#g-view-list"/></svg><svg class="small" viewBox="0 0 24 24"><use href="#g-chevron"/></svg></span>' +
            '<span class="tool"><svg viewBox="0 0 24 24"><use href="#g-view-grid"/></svg><svg class="small" viewBox="0 0 24 24"><use href="#g-chevron"/></svg></span>' +
            '<span class="tool"><svg viewBox="0 0 24 24"><use href="#g-more"/></svg></span>' +
            '<span class="tool round"><svg viewBox="0 0 24 24"><use href="#g-search"/></svg></span>' +
          "</span>" +
        "</div>" +
        '<div class="finder-cols" aria-hidden="true"><span class="c-name">Name</span><span class="c-date">Date Modified</span><span class="c-size">Size</span></div>' +
        '<ul class="finder-rows">' + rowsHtml + "</ul>" +
        '<div class="finder-pane" aria-live="polite">' + paneHtml(rows[0].name, rows[0].text) + "</div>" +
      "</div>";

    desktop.querySelector(".stage").appendChild(el);
    var w = register(el, f.title, true);

    var pane = el.querySelector(".finder-pane");
    var buttons = el.querySelectorAll("button.frow");
    for (var b2 = 0; b2 < buttons.length; b2++) {
      (function (btn) {
        var row = rows[Number(btn.getAttribute("data-row"))];
        btn.addEventListener("click", function () {
          if (row.kind === "folder") { openFolder(row.open); return; }
          for (var k = 0; k < buttons.length; k++) buttons[k].classList.remove("selected");
          btn.classList.add("selected");
          if (row.text) pane.innerHTML = paneHtml(row.name, row.text);
        });
      })(buttons[b2]);
    }
    return w;
  }

  function openFolder(key) {
    var w = finders[key];
    if (!w) {
      w = finders[key] = buildFinder(key);
      var shown = 0;
      for (var k in finders) if (finders[k] !== w && !finders[k].el.classList.contains("is-gone")) shown++;
      var n = shown % 6;
      w.el.style.left = "calc(var(--u) * " + (445 + n * 26) + ")";
      w.el.style.top = "calc(var(--u) * " + (262 + n * 26) + ")";
    }
    openWin(w);
  }

  // ----- desktop icons -----
  var icons = document.querySelectorAll(".icon");
  function select(el) {
    for (var i = 0; i < icons.length; i++) icons[i].classList.remove("selected");
    if (el) el.classList.add("selected");
  }
  for (var i = 0; i < icons.length; i++) {
    (function (icon) {
      icon.addEventListener("click", function (e) {
        e.stopPropagation();
        select(icon);
        var key = icon.getAttribute("data-folder");
        if (key && FOLDERS[key]) openFolder(key);
      });
      if (icon.getAttribute("data-file") === "cv") {
        icon.addEventListener("click", function () { openWin(cvWin); });
      }
    })(icons[i]);
  }
  desktop.addEventListener("click", function () { select(null); });

  refresh();
})();
