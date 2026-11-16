// Theme switch: follows the device setting until the visitor chooses, then remembers the choice.
(function () {
  var root = document.documentElement;
  var btn = document.getElementById("theme-toggle");
  function isDark() { var t = root.dataset.theme; return t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches; }
  function sync() { if (btn) btn.setAttribute("aria-checked", isDark()); }
  if (btn) btn.addEventListener("click", function () {
    var next = isDark() ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
    sync();
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", sync);
  sync();

  // Remember the language the visitor picked.
  document.querySelectorAll("[data-set-lang]").forEach(function (a) {
    a.addEventListener("click", function () { try { localStorage.setItem("lang", a.dataset.setLang); } catch (e) {} });
  });

  // Recipe filters on the home page.
  var chips = document.querySelectorAll("[data-filter]");
  var cards = document.querySelectorAll(".card[data-kcal]");
  var count = document.getElementById("count");
  var tests = {
    all: function () { return true; },
    u600: function (d) { return +d.kcal <= 600; },
    p40: function (d) { return +d.protein >= 40; },
    f15: function (d) { return +d.fiber >= 15; },
    chicken: function (d) { return d.main === "chicken"; },
    beef: function (d) { return d.main === "beef"; },
    fish: function (d) { return d.main === "fish"; },
    plant: function (d) { return d.main === "plant-based"; },
    prep: function (d) { return (" " + d.tags + " ").indexOf(" meal-prep ") > -1; },
    freezer: function (d) { return (" " + d.tags + " ").indexOf(" freezer-friendly ") > -1; }
  };
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var shown = 0;
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip); });
      cards.forEach(function (card) {
        var ok = tests[chip.dataset.filter](card.dataset);
        card.hidden = !ok;
        if (ok) shown++;
      });
      if (count) count.textContent = (shown === cards.length ? count.dataset.all : count.dataset.some.replace("{a}", shown));
      var none = document.getElementById("none");
      if (none) none.hidden = shown > 0;
    });
  });
})();
