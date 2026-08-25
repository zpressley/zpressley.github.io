/* ============================================================
   Theme toggle + project filtering.

   The project cards live as plain HTML in index.html so that search
   engines and link previews can read them. This script only reads what
   is already on the page — it never renders the cards.
   ============================================================ */

(function () {
  "use strict";

  /* ---------- theme ---------- */

  var root = document.documentElement;

  function readTheme() {
    try { return localStorage.getItem("theme"); } catch (e) { return null; }
  }

  function applyTheme(t) {
    if (t === "light") root.setAttribute("data-theme", "light");
    else root.removeAttribute("data-theme");
    var btn = document.querySelector(".theme-toggle");
    if (btn) {
      btn.textContent = t === "light" ? "☾" : "☀";
      btn.setAttribute("aria-label", "Switch to " + (t === "light" ? "dark" : "light") + " theme");
    }
  }

  applyTheme(readTheme() || "dark");

  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".theme-toggle");
    if (!btn) return;
    var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    applyTheme(next);
    try { localStorage.setItem("theme", next); } catch (err) { /* private mode */ }
  });

  /* ---------- year ---------- */

  var yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- project filters ---------- */

  var grid = document.getElementById("project-grid");
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
  var filters = document.getElementById("filters");
  var countEl = document.getElementById("project-count");

  if (countEl) {
    countEl.textContent = cards.length + (cards.length === 1 ? " project" : " projects");
  }
  if (!filters || cards.length < 2) return;

  function tagsOf(card) {
    return Array.prototype.map.call(card.querySelectorAll(".tag"), function (t) {
      return t.textContent.trim();
    });
  }

  var seen = {};
  var tags = [];
  cards.forEach(function (c) {
    tagsOf(c).forEach(function (t) {
      if (!seen[t]) { seen[t] = true; tags.push(t); }
    });
  });
  tags.sort();

  filters.innerHTML = ["All"].concat(tags).map(function (t, i) {
    var esc = t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
    return '<button class="chip" type="button" data-filter="' + esc + '" aria-pressed="' +
           (i === 0) + '">' + esc + "</button>";
  }).join("");

  filters.addEventListener("click", function (e) {
    var chip = e.target.closest("[data-filter]");
    if (!chip) return;
    var active = chip.getAttribute("data-filter");

    Array.prototype.forEach.call(filters.querySelectorAll(".chip"), function (c) {
      c.setAttribute("aria-pressed", String(c === chip));
    });

    var shown = 0;
    cards.forEach(function (card) {
      var match = active === "All" || tagsOf(card).indexOf(active) !== -1;
      card.style.display = match ? "" : "none";
      if (match) shown++;
    });

    if (countEl) {
      countEl.textContent = shown + (shown === 1 ? " project" : " projects");
    }
  });
})();
