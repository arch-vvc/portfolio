// Behaviour for the desktop home page. No fetch, no modules: works when opened from disk.
// Folders and dock icons only select or hover for now. The CV window really works.
(function () {
  var DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  var desktop = document.getElementById("desktop");
  if (!desktop) return;

  // ----- clock in the menu bar -----
  var clock = document.getElementById("clock");
  function tick() {
    var d = new Date();
    var h = d.getHours() % 12 || 12;
    var m = d.getMinutes();
    var ampm = d.getHours() < 12 ? "AM" : "PM";
    clock.textContent = DAYS[d.getDay()] + " " + d.getDate() + " " + MONTHS[d.getMonth()] +
      " " + h + ":" + (m < 10 ? "0" : "") + m + " " + ampm;
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

  // ----- selecting desktop icons -----
  var icons = document.querySelectorAll(".icon");
  function select(el) {
    for (var i = 0; i < icons.length; i++) icons[i].classList.remove("selected");
    if (el) el.classList.add("selected");
  }
  for (var i = 0; i < icons.length; i++) {
    (function (icon) {
      icon.addEventListener("click", function (e) { e.stopPropagation(); select(icon); });
      icon.addEventListener("focus", function () { select(icon); });
      if (icon.getAttribute("data-file") === "cv") {
        icon.addEventListener("dblclick", openWindow);
        icon.addEventListener("keydown", function (e) { if (e.key === "Enter") openWindow(); });
      }
    })(icons[i]);
  }
  desktop.addEventListener("click", function () { select(null); });

  // ----- the CV window -----
  var win = document.getElementById("cv-window");
  var titlebar = document.getElementById("titlebar");
  var appName = document.getElementById("app-name");
  var dockPreview = document.getElementById("dock-preview");
  var dockMin = document.getElementById("dock-min");
  var previewOnly = document.querySelectorAll(".preview-only");
  var minimised = false;

  function setApp(open) {
    appName.textContent = open ? "Preview" : "Finder";
    for (var i = 0; i < previewOnly.length; i++) previewOnly[i].style.display = open ? "" : "none";
    dockPreview.classList.toggle("not-running", !open);
  }

  function closeWindow() {
    win.classList.remove("is-full", "is-minimising");
    win.classList.add("is-gone");
    dockMin.hidden = true;
    minimised = false;
    setApp(false);
  }

  function openWindow() {
    win.classList.remove("is-gone", "is-minimising");
    win.style.removeProperty("--dx");
    win.style.removeProperty("--dy");
    dockMin.hidden = true;
    minimised = false;
    setApp(true);
    win.focus();
  }

  function minimiseWindow() {
    if (win.classList.contains("is-full")) win.classList.remove("is-full");
    dockMin.hidden = false;
    var w = win.getBoundingClientRect();
    var t = dockMin.getBoundingClientRect();
    win.style.setProperty("--dx", (t.left + t.width / 2 - (w.left + w.width / 2)) + "px");
    win.style.setProperty("--dy", (t.top + t.height / 2 - (w.top + w.height / 2)) + "px");
    win.classList.add("is-minimising");
    minimised = true;
  }

  function restoreWindow() {
    win.classList.remove("is-minimising");
    dockMin.hidden = true;
    minimised = false;
    win.focus();
  }

  function toggleFullscreen() {
    win.classList.toggle("is-full");
  }

  var actions = { close: closeWindow, minimise: minimiseWindow, fullscreen: toggleFullscreen };
  var lights = document.querySelectorAll("[data-action]");
  for (var l = 0; l < lights.length; l++) {
    (function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        actions[btn.getAttribute("data-action")]();
      });
    })(lights[l]);
  }
  dockMin.addEventListener("click", function (e) { e.stopPropagation(); restoreWindow(); });
  dockPreview.addEventListener("click", function (e) {
    e.stopPropagation();
    if (win.classList.contains("is-gone")) openWindow();
    else if (minimised) restoreWindow();
  });

  titlebar.addEventListener("dblclick", function (e) {
    if (e.target.closest && e.target.closest(".lights")) return;
    toggleFullscreen();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && win.classList.contains("is-full")) win.classList.remove("is-full");
  });

  // ----- dragging the window by its title bar -----
  var drag = null;
  titlebar.addEventListener("pointerdown", function (e) {
    if (win.classList.contains("is-full")) return;
    if (e.target.closest && e.target.closest(".lights")) return;
    var r = win.getBoundingClientRect();
    drag = { x: e.clientX - r.left, y: e.clientY - r.top };
    win.classList.add("dragging");
    titlebar.setPointerCapture(e.pointerId);
  });
  titlebar.addEventListener("pointermove", function (e) {
    if (!drag) return;
    var menubarH = document.querySelector(".menubar").getBoundingClientRect().height;
    var x = Math.min(Math.max(e.clientX - drag.x, -win.offsetWidth + 120), window.innerWidth - 120);
    var y = Math.min(Math.max(e.clientY - drag.y, menubarH), window.innerHeight - 60);
    win.style.left = x + "px";
    win.style.top = y + "px";
  });
  function endDrag(e) {
    if (!drag) return;
    drag = null;
    win.classList.remove("dragging");
    try { titlebar.releasePointerCapture(e.pointerId); } catch (err) { /* already released */ }
  }
  titlebar.addEventListener("pointerup", endDrag);
  titlebar.addEventListener("pointercancel", endDrag);

  setApp(true);
})();
