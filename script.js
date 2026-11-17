// Reads SITE_CONFIG (site.config.js) and shows only what has a value.
// No fetch, no modules: works when opened from disk.
(function () {
  var cfg = window.SITE_CONFIG || {};

  function makeLink(url, label, className) {
    var a = document.createElement("a");
    a.href = url;
    a.className = className;
    a.textContent = label;
    a.rel = "noopener";
    return a;
  }

  // <span data-demo="callqa"></span> becomes a demo button only if a URL is set.
  function renderDemo(slot) {
    var url = (cfg.demos || {})[slot.getAttribute("data-demo")];
    if (!url) return;
    slot.appendChild(makeLink(url, "Watch demo", "button"));
  }

  function renderDemos() {
    var slots = document.querySelectorAll("[data-demo]");
    for (var i = 0; i < slots.length; i++) renderDemo(slots[i]);
  }

  // <span data-cv></span> becomes the CV button only if a path is set.
  function renderCv() {
    var url = cfg.cvPath;
    var slots = document.querySelectorAll("[data-cv]");
    for (var i = 0; i < slots.length; i++) {
      if (!url) continue;
      slots[i].appendChild(makeLink(url, "CV (PDF)", "button"));
    }
  }

  // <p data-text="callqaResult" hidden></p> is filled and unhidden only if text is set.
  function renderText() {
    var slots = document.querySelectorAll("[data-text]");
    for (var i = 0; i < slots.length; i++) {
      var text = cfg[slots[i].getAttribute("data-text")];
      if (!text) continue;
      slots[i].textContent = text;
      slots[i].hidden = false;
    }
  }

  // <ul data-photos hidden></ul> gets one figure per photo, or stays hidden.
  function renderPhotos() {
    var list = cfg.windstreamPhotos || [];
    var slots = document.querySelectorAll("[data-photos]");
    for (var i = 0; i < slots.length; i++) {
      if (!list.length) continue;
      for (var j = 0; j < list.length; j++) {
        if (!list[j].src) continue;
        var li = document.createElement("li");
        var img = document.createElement("img");
        img.src = list[j].src;
        img.alt = list[j].alt || list[j].caption || "Site photo";
        li.appendChild(img);
        if (list[j].caption) {
          var cap = document.createElement("p");
          cap.textContent = list[j].caption;
          li.appendChild(cap);
        }
        slots[i].appendChild(li);
      }
      slots[i].hidden = !slots[i].children.length;
    }
  }

  // <span data-degree>AI and ML engineering</span> is replaced only if a title is set.
  function renderDegree() {
    var slots = document.querySelectorAll("[data-degree]");
    for (var i = 0; i < slots.length; i++) {
      if (cfg.degreeTitle) slots[i].textContent = cfg.degreeTitle;
    }
  }

  renderDemos();
  renderCv();
  renderText();
  renderPhotos();
  renderDegree();
})();
