// The four dock apps: Safari, Messages, Photos and Music. Each one describes a window.
// desktop.js builds it on the first click. No fetch, no modules: works from disk.
window.DESKTOP_APPS = (function () {
  var cfg = window.SITE_CONFIG || {};
  var GITHUB = "https://github.com/arch-vvc";
  var LINKEDIN = "https://www.linkedin.com/in/archit-rishabh";
  var EMAIL = "mailto:archit.rishabh25@gmail.com";
  var TO = "archit.rishabh25@gmail.com";
  var GMAIL = "https://mail.google.com/mail/?view=cm&fs=1";

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // Small line icons, drawn on a 24 by 24 grid.
  var ICON = {
    search: '<circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M16 16l5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    filter: '<path d="M5 8h14M8 12h8M11 16h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    compose: '<path d="M5 6h8M5 6v13h13v-8M17.500 4.500l2 2L11 15l-3 1 1-3z" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round"/>',
    plus: '<path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    emoji: '<circle cx="12" cy="12" r="8.500" fill="currentColor"/><circle cx="9" cy="10.500" r="1.200" fill="#1c1c1e"/><circle cx="15" cy="10.500" r="1.200" fill="#1c1c1e"/><path d="M8.500 14c1 1.800 5.500 1.800 7 0" fill="none" stroke="#1c1c1e" stroke-width="1.400" stroke-linecap="round"/>',
    wave: '<path d="M6 10v4M9 7v10M12 9v6M15 6v12M18 10v4" stroke="currentColor" stroke-width="1.700" stroke-linecap="round"/>',
    sidebar: '<rect x="3" y="5" width="18" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.800"/><path d="M9 5v14" stroke="currentColor" stroke-width="1.800"/>',
    back: '<path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    forward: '<path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    download: '<circle cx="12" cy="12" r="8.500" fill="none" stroke="currentColor" stroke-width="1.700"/><path d="M12 7.500v8M8.500 12.500l3.500 3.500 3.500-3.500" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round"/>',
    share: '<path d="M12 15V4M8.500 7.500L12 4l3.500 3.500M6 11v8h12v-8" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round"/>',
    tabs: '<rect x="8" y="3.500" width="12.500" height="12.500" rx="2.500" fill="none" stroke="currentColor" stroke-width="1.700"/><rect x="3.500" y="8" width="12.500" height="12.500" rx="2.500" fill="#2b2b2e" stroke="currentColor" stroke-width="1.700"/>',
    lock: '<rect x="6" y="11" width="12" height="8" rx="2" fill="currentColor"/><path d="M9 11V8.500a3 3 0 0 1 6 0V11" fill="none" stroke="currentColor" stroke-width="1.700"/>',
    home: '<path d="M4 11l8-7 8 7M6 10v9h12v-9M10 19v-5h4v5" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linejoin="round"/>',
    grid: '<g fill="none" stroke="currentColor" stroke-width="1.600"><rect x="4" y="4" width="6.500" height="6.500" rx="1.500"/><rect x="13.500" y="4" width="6.500" height="6.500" rx="1.500"/><rect x="4" y="13.500" width="6.500" height="6.500" rx="1.500"/><rect x="13.500" y="13.500" width="6.500" height="6.500" rx="1.500"/></g>',
    radio: '<circle cx="12" cy="12" r="2" fill="currentColor"/><path d="M7.500 7.500a6.400 6.400 0 0 0 0 9M16.500 7.500a6.400 6.400 0 0 1 0 9M4.800 4.800a10.200 10.200 0 0 0 0 14.400M19.200 4.800a10.200 10.200 0 0 1 0 14.400" fill="none" stroke="currentColor" stroke-width="1.500" stroke-linecap="round"/>',
    clock: '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.700"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linecap="round"/>',
    artist: '<path d="M14 4l6 6-9 9-4 1 1-4z" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linejoin="round"/>',
    album: '<rect x="5" y="4" width="14" height="16" rx="2.500" fill="none" stroke="currentColor" stroke-width="1.700"/><path d="M7.500 8h9" stroke="currentColor" stroke-width="1.700"/>',
    note: '<path d="M10 17V6l9-2v11" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linejoin="round"/><circle cx="7.500" cy="17" r="2.500" fill="currentColor"/><circle cx="16.500" cy="15" r="2.500" fill="currentColor"/>',
    star: '<path d="M12 4l2.400 5 5.600.7-4.100 3.800 1.100 5.500L12 16.300 7 19l1.100-5.500L4 9.700 9.600 9z" fill="none" stroke="currentColor" stroke-width="1.600" stroke-linejoin="round"/>',
    heart: '<path d="M12 19s-7-4.300-7-9.500A3.800 3.800 0 0 1 12 8a3.800 3.800 0 0 1 7 1.500C19 14.700 12 19 12 19z" fill="none" stroke="currentColor" stroke-width="1.700" stroke-linejoin="round"/>',
    photos: '<rect x="4" y="5" width="16" height="14" rx="2.500" fill="none" stroke="currentColor" stroke-width="1.700"/><circle cx="9" cy="10" r="1.600" fill="currentColor"/><path d="M5 17l5-4 3 2.500 3-2 3 3" fill="none" stroke="currentColor" stroke-width="1.500"/>',
    shuffle: '<path d="M4 7h3c5 0 5 10 10 10h3M4 17h3c2 0 3-1.500 4-3M14 8c1-1 2-1 3-1h3M18 4.500L20.500 7 18 9.500M18 14.500L20.500 17 18 19.500" fill="none" stroke="currentColor" stroke-width="1.600" stroke-linecap="round" stroke-linejoin="round"/>',
    prev: '<path d="M18 6v12L9 12zM7 6v12" fill="currentColor" stroke="currentColor" stroke-width="1.600" stroke-linejoin="round"/>',
    play: '<path d="M8 5.500v13l11-6.500z" fill="currentColor"/>',
    next: '<path d="M6 6v12l9-6zM17 6v12" fill="currentColor" stroke="currentColor" stroke-width="1.600" stroke-linejoin="round"/>',
    repeat: '<path d="M5 11V9a3 3 0 0 1 3-3h11M16 3l3 3-3 3M19 13v2a3 3 0 0 1-3 3H5M8 21l-3-3 3-3" fill="none" stroke="currentColor" stroke-width="1.600" stroke-linecap="round" stroke-linejoin="round"/>',
    send: '<path d="M4 12L20 4l-6 16-3-7z" fill="currentColor"/>',
    volume: '<path d="M5 10v4h3l4 3.500v-11L8 10zM15.500 9a4 4 0 0 1 0 6M18 6.500a7.500 7.500 0 0 1 0 11" fill="none" stroke="currentColor" stroke-width="1.600" stroke-linecap="round" stroke-linejoin="round"/>'
  };

  function svg(name, cls) {
    return '<svg' + (cls ? ' class="' + cls + '"' : "") + ' viewBox="0 0 24 24" aria-hidden="true">' + ICON[name] + "</svg>";
  }

  function lights() {
    return '<div class="lights app-lights">' +
      '<button class="light close" type="button" data-action="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
      '<button class="light minimise" type="button" data-action="minimise" aria-label="Minimise"><span aria-hidden="true">&minus;</span></button>' +
      '<button class="light zoom" type="button" data-action="fullscreen" aria-label="Full screen"><span aria-hidden="true">&#x2922;</span></button>' +
      "</div>";
  }

  // ---------- Messages ----------
  var THREADS = [
    {
      name: "Archit Rishabh", initials: "AR", time: "Today",
      lines: [
        { text: "Hi, I'm Archit. Final year AI and ML at PES University in Bangalore." },
        { text: "I build applied AI for messy business operations." },
        { text: "I'm looking for forward deployed engineer and founder's office roles, remote or in India." },
        { link: EMAIL, title: "Email me", host: "archit.rishabh25@gmail.com" },
        { link: LINKEDIN, title: "LinkedIn", host: "linkedin.com/in/archit-rishabh" }
      ]
    },
    {
      name: "Areas I want to work in", initials: "AW", time: "Today",
      lines: [
        { text: "Forward deployed engineering: taking an AI system from a demo to a customer's real workflow." },
        { text: "Applied AI for operations: procurement, finance back office, customer calls and sales." },
        { text: "Founder's office roles where I can own a problem from the first question to the shipped result." }
      ]
    },
    {
      name: "Work I've done before", initials: "WD", time: "Today",
      lines: [
        { text: "Tender tracker for Windstream: 33 portals read every day, an 8 figure contract now underway." },
        { text: "Call QA for voice agents, exception triage for accounts payable, and gtm_agent for outreach." },
        { text: "Founder's office at Windstream and OOH Advertising. Data and AI strategy at NexTurn." },
        { text: "Capstone: an immune system inspired supply chain pipeline. Paper submitted." }
      ]
    }
  ];

  function chatHtml(thread) {
    var out = '<p class="im-time">' + esc(thread.time) + "</p>";
    for (var i = 0; i < thread.lines.length; i++) {
      var l = thread.lines[i];
      if (l.link) {
        out += '<a class="bubble in link" href="' + esc(l.link) + '"' + (l.link.indexOf("mailto:") === 0 ? "" : ' target="_blank" rel="noopener"') +
          '><strong>' + esc(l.title) + "</strong><span>" + esc(l.host) + "</span></a>";
      } else {
        out += '<p class="bubble in">' + esc(l.text) + "</p>";
      }
    }
    return out;
  }

  function lastText(thread) {
    var l = thread.lines[thread.lines.length - 1];
    return l.text || l.title;
  }

  function messages() {
    var list = "";
    for (var i = 0; i < THREADS.length; i++) {
      list += '<li><button class="im-thread' + (i === 0 ? " selected" : "") + '" type="button" data-thread="' + i + '">' +
        '<span class="avatar">' + esc(THREADS[i].initials) + "</span>" +
        '<span class="im-meta"><span class="im-name">' + esc(THREADS[i].name) + '</span><span class="im-when">' + esc(THREADS[i].time) + "</span>" +
        '<span class="im-preview">' + esc(lastText(THREADS[i])) + "</span></span></button></li>";
    }
    return lights() + '<div class="drag-corner" data-drag></div>' +
      '<aside class="im-side"><div class="im-side-top" data-drag><span class="round-btn" aria-hidden="true">' + svg("filter") + "</span></div>" +
      '<div class="im-search" aria-hidden="true">' + svg("search") + "<span>Search</span></div>" +
      '<ul class="im-list">' + list + "</ul></aside>" +
      '<section class="im-main"><div class="im-head" data-drag><span class="round-btn" aria-hidden="true">' + svg("compose") + "</span>" +
      '<div class="im-who"><span class="avatar big" id="im-avatar">' + esc(THREADS[0].initials) + '</span><h2 class="im-title" id="im-title">' + esc(THREADS[0].name) + "</h2></div></div>" +
      '<div class="im-chat" id="im-chat" aria-live="polite">' + chatHtml(THREADS[0]) + "</div>" +
      '<div class="im-input" aria-hidden="true"><span class="round-btn">' + svg("plus") + '</span><span class="im-field">iMessage' + svg("wave") + '</span><span class="round-btn emoji">' + svg("emoji") + "</span></div></section>";
  }

  function messagesInit(el) {
    var buttons = el.querySelectorAll(".im-thread");
    var chat = el.querySelector("#im-chat");
    var title = el.querySelector("#im-title");
    var avatar = el.querySelector("#im-avatar");
    for (var i = 0; i < buttons.length; i++) {
      (function (btn) {
        btn.addEventListener("click", function () {
          var t = THREADS[Number(btn.getAttribute("data-thread"))];
          for (var k = 0; k < buttons.length; k++) buttons[k].classList.remove("selected");
          btn.classList.add("selected");
          chat.innerHTML = chatHtml(t);
          title.textContent = t.name;
          avatar.textContent = t.initials;
        });
      })(buttons[i]);
    }
  }

  // ---------- Music ----------
  var COVERS = ["assets/music/drake1.jpg", "assets/music/drake2.jpg", "assets/music/drake3.jpg", "assets/music/drake4.jpg"];
  var ALBUMS = ["assets/music/album1.jpg", "assets/music/album2.jpg", "assets/music/album3.jpg", "assets/music/album4.jpg"];

  // Cover art for a tile: a photo while there is one, a gradient otherwise.
  function art(list, i) {
    var src = list[i];
    return '<span class="art art' + (i % 5) + '"' + (src ? ' data-cover' : "") + ">" +
      (src ? '<img src="' + src + '" alt="Drake">' : svg("note")) + "</span>";
  }

  function tiles(list, count, cls) {
    var out = "";
    for (var i = 0; i < count; i++) {
      out += '<li class="tile ' + cls + '">' + art(list, i) + '<span class="t-title">Drake</span><span class="t-sub">Drake</span></li>';
    }
    return out;
  }

  function side(items, heads) {
    var out = "";
    for (var g = 0; g < items.length; g++) {
      out += '<div class="side-group">';
      if (heads[g]) out += '<p class="side-head">' + esc(heads[g]) + "</p>";
      for (var i = 0; i < items[g].length; i++) {
        var it = items[g][i];
        out += '<p class="side-item' + (it[2] ? " on" : "") + '">' + svg(it[1]) + "<span>" + esc(it[0]) + "</span></p>";
      }
      out += "</div>";
    }
    return out;
  }

  function music() {
    return lights() + '<div class="drag-corner" data-drag></div>' +
      '<aside class="mu-side" aria-hidden="true">' +
      side([
        [["Search", "search"], ["Home", "home", true], ["New", "grid"], ["Radio", "radio"]],
        [["Recently Added", "clock"], ["Artists", "artist"], ["Albums", "album"], ["Songs", "note"]],
        [["All Playlists", "grid"], ["Favourite Songs", "star"]]
      ], ["", "Library", "Playlists"]) + "</aside>" +
      '<section class="mu-main"><div class="mu-top" data-drag></div><div class="mu-scroll">' +
      "<h2>Home</h2>" +
      '<h3>Last Played</h3><div class="mu-last">' + art(COVERS, 0) + '<div><span class="t-title">Drake</span><span class="t-sub">Drake</span></div></div>' +
      '<h3>On Repeat</h3><ul class="tiles">' + tiles(COVERS, 4, "big") + "</ul>" +
      "<h3>Recently Played</h3><ul class=\"tiles\">" + tiles(ALBUMS, 4, "small") + "</ul>" +
      '</div><div class="mu-player" aria-hidden="true">' + svg("shuffle") + svg("prev") + svg("play", "play") + svg("next") + svg("repeat") +
      '<span class="mu-now"><span>Drake</span><span>Drake</span></span>' + svg("volume") + "</div></section>";
  }

  // ---------- Photos ----------
  function photos() {
    var cells = "";
    for (var i = 0; i < 15; i++) cells += '<li class="cell cell' + (i % 4) + '"></li>';
    return lights() + '<div class="drag-corner" data-drag></div>' +
      '<aside class="ph-side" aria-hidden="true">' +
      side([[["Library", "photos", true], ["Favourites", "heart"], ["Recents", "clock"]]], [""]) + "</aside>" +
      '<section class="ph-main"><div class="ph-top" data-drag><h2>Library</h2></div>' +
      '<ul class="ph-grid">' + cells + '</ul><p class="ph-note">Photos are on their way.</p></section>';
  }

  // ---------- Safari ----------
  function brand(letter, colour) {
    return '<span class="fav" style="background:' + colour + '" aria-hidden="true">' + esc(letter) + "</span>";
  }

  var TABS = [
    { name: "GitHub", host: "github.com/arch-vvc", href: GITHUB, fav: brand("G", "#24292f") },
    { name: "Krillion", host: "Krillion", fav: brand("K", "#f2711c"), page: "krillion" },
    { name: "LinkedIn", host: "linkedin.com/in/archit-rishabh", href: LINKEDIN, fav: brand("in", "#0a66c2") },
    { name: "Twitter", host: "x.com", href: cfg.twitter, fav: brand("X", "#000000"), page: "stub" },
    { name: "YouTube", host: "youtube.com", href: cfg.youtube, fav: brand("▶", "#e5322d"), page: "stub" }
  ];

  function pageHtml(tab) {
    if (tab.page === "krillion") {
      return cfg.krillionImage
        ? '<div class="sf-shot"><img src="' + esc(cfg.krillionImage) + '" alt="My One in a Krillion result in the Krillion game"></div>'
        : '<div class="sf-stub"><div class="sf-frame" aria-hidden="true">' + svg("photos") + "</div><p>My One in a Krillion goes here.</p></div>";
    }
    return '<div class="sf-stub"><div class="sf-frame small" aria-hidden="true">' + tab.fav + "</div><p>" + esc(tab.name) + " is coming soon.</p></div>";
  }

  function safari() {
    var tabs = "";
    for (var i = 0; i < TABS.length; i++) {
      var t = TABS[i];
      var inner = t.fav + "<span>" + esc(t.name) + "</span>";
      if (t.href) tabs += '<a class="sf-tab" href="' + esc(t.href) + '" target="_blank" rel="noopener">' + inner + "</a>";
      else tabs += '<button class="sf-tab' + (i === 1 ? " selected" : "") + '" type="button" data-tab="' + i + '">' + inner + "</button>";
    }
    return '<div class="sf-toolbar" data-drag>' + lights() +
      '<span class="round-btn sq" aria-hidden="true">' + svg("sidebar") + "</span>" +
      '<span class="sf-pill" aria-hidden="true">Personal</span>' +
      '<span class="round-btn pair" aria-hidden="true">' + svg("back") + "<i></i>" + svg("forward") + "</span>" +
      '<div class="sf-address" aria-hidden="true">' + svg("lock") + '<span id="sf-url">' + esc(TABS[1].host) + "</span></div>" +
      '<span class="round-btn" aria-hidden="true">' + svg("download") + "</span>" +
      '<span class="round-btn" aria-hidden="true">' + svg("share") + "</span>" +
      '<span class="round-btn" aria-hidden="true">' + svg("plus") + "</span>" +
      '<span class="round-btn" aria-hidden="true">' + svg("tabs") + "</span></div>" +
      '<div class="sf-tabs">' + tabs + "</div>" +
      '<div class="sf-page" id="sf-page">' + pageHtml(TABS[1]) + "</div>";
  }

  function safariInit(el) {
    var buttons = el.querySelectorAll("button.sf-tab");
    var page = el.querySelector("#sf-page");
    var url = el.querySelector("#sf-url");
    for (var i = 0; i < buttons.length; i++) {
      (function (btn) {
        btn.addEventListener("click", function () {
          var t = TABS[Number(btn.getAttribute("data-tab"))];
          for (var k = 0; k < buttons.length; k++) buttons[k].classList.remove("selected");
          btn.classList.add("selected");
          page.innerHTML = pageHtml(t);
          url.textContent = t.host;
        });
      })(buttons[i]);
    }
  }


  // ---------- Mail ----------
  // A drafted message. Send opens Gmail with the edited text filled in; the small link
  // underneath uses whatever mail app the visitor has. The site never sends anything itself.
  var DRAFT_SUBJECT = "Let's schedule a call";
  var DRAFT_BODY = "Hi Archit,\n\nCool website, let's schedule a call.\n\n";

  function gmailUrl(subject, body) {
    return GMAIL + "&to=" + encodeURIComponent(TO) + "&su=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }

  function mailtoUrl(subject, body) {
    return "mailto:" + TO + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }

  function mail() {
    return lights() +
      '<form class="ml-form" onsubmit="return false">' +
      '<div class="ml-top" data-drag><h2>New Message</h2>' +
      '<a class="ml-send" id="ml-send" href="' + esc(gmailUrl(DRAFT_SUBJECT, DRAFT_BODY)) + '" target="_blank" rel="noopener" aria-label="Send, opens Gmail with this message">' + svg("send") + "</a></div>" +
      '<div class="ml-row"><span class="ml-label">To:</span><span class="ml-to">' + esc(TO) + "</span></div>" +
      '<div class="ml-row"><label class="ml-label" for="ml-subject">Subject:</label><input class="ml-subject" id="ml-subject" type="text" value="' + esc(DRAFT_SUBJECT) + '" autocomplete="off"></div>' +
      '<textarea class="ml-body" id="ml-body" aria-label="Message">' + esc(DRAFT_BODY) + "</textarea>" +
      '<p class="ml-hint">Send opens Gmail with this message ready. <a id="ml-app" href="' + esc(mailtoUrl(DRAFT_SUBJECT, DRAFT_BODY)) + '">Use another mail app</a></p>' +
      "</form>";
  }

  function mailInit(el) {
    var subject = el.querySelector("#ml-subject");
    var body = el.querySelector("#ml-body");
    var send = el.querySelector("#ml-send");
    var app = el.querySelector("#ml-app");
    function sync() {
      send.href = gmailUrl(subject.value, body.value);
      app.href = mailtoUrl(subject.value, body.value);
    }
    subject.addEventListener("input", sync);
    body.addEventListener("input", sync);
    sync();
  }

  return {
    "Mail": { title: "New Message", size: [580, 440], pos: [360, 160], html: mail, init: mailInit },
    "Messages": { title: "Messages", size: [700, 520], pos: [330, 150], html: messages, init: messagesInit },
    "Music": { title: "Music", size: [900, 685], pos: [270, 84], html: music },
    "Safari": { title: "Safari", size: [920, 580], pos: [260, 118], html: safari, init: safariInit },
    "Photos": { title: "Photos", size: [780, 500], pos: [300, 140], html: photos }
  };
})();
