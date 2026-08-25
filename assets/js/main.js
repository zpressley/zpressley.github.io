/* ============================================================
   Rendering + interaction. You shouldn't need to touch this
   to add projects — edit assets/js/projects.js instead.
   ============================================================ */

(function () {
  "use strict";

  /* ---------- theme ---------- */

  var root = document.documentElement;

  function readTheme() {
    try {
      return localStorage.getItem("theme");
    } catch (e) {
      return null;
    }
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
    try {
      localStorage.setItem("theme", next);
    } catch (err) {
      /* private browsing — theme just won't persist */
    }
  });

  /* ---------- project grid ---------- */

  var grid = document.getElementById("project-grid");
  if (!grid || typeof PROJECTS === "undefined") return;

  var filters = document.getElementById("filters");
  var countEl = document.getElementById("project-count");
  var active = "All";

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function card(p) {
    var tags = (p.tags || [])
      .map(function (t) {
        return '<span class="tag">' + esc(t) + "</span>";
      })
      .join("");
    var target = p.external ? ' target="_blank" rel="noopener"' : "";
    return (
      '<a class="card" href="' + esc(p.href || "#") + '"' + target + ">" +
      '<div class="card__meta"><span>' + esc(p.kind || "Project") +
      (p.draft ? " · placeholder" : "") +
      '</span><span class="year">' + esc(p.year || "") + "</span></div>" +
      "<h3>" + esc(p.title) + "</h3>" +
      "<p>" + esc(p.blurb || "") + "</p>" +
      '<div class="tags">' + tags + "</div>" +
      '<div class="card__go">Read ' + (p.external ? "↗" : "→") + "</div>" +
      "</a>"
    );
  }

  function render() {
    var list = PROJECTS.filter(function (p) {
      return active === "All" || (p.tags || []).indexOf(active) !== -1 || p.kind === active;
    });
    grid.innerHTML = list.length
      ? list.map(card).join("")
      : '<p class="empty">Nothing tagged “' + esc(active) + '” yet.</p>';
    if (countEl) countEl.textContent = PROJECTS.length + (PROJECTS.length === 1 ? " project" : " projects");
  }

  function buildFilters() {
    if (!filters) return;
    var seen = {};
    var tags = [];
    PROJECTS.forEach(function (p) {
      (p.tags || []).forEach(function (t) {
        if (!seen[t]) {
          seen[t] = true;
          tags.push(t);
        }
      });
    });
    tags.sort();
    filters.innerHTML = ["All"]
      .concat(tags)
      .map(function (t) {
        return (
          '<button class="chip" type="button" data-filter="' + esc(t) + '" aria-pressed="' +
          (t === active) + '">' + esc(t) + "</button>"
        );
      })
      .join("");
    filters.addEventListener("click", function (e) {
      var chip = e.target.closest("[data-filter]");
      if (!chip) return;
      active = chip.getAttribute("data-filter");
      Array.prototype.forEach.call(filters.querySelectorAll(".chip"), function (c) {
        c.setAttribute("aria-pressed", String(c === chip));
      });
      render();
    });
  }

  buildFilters();
  render();

  var yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();
})();
