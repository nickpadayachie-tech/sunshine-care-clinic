document.documentElement.classList.add("js-enabled");

(function () {
  "use strict";

  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  var hoursList = document.getElementById("hoursList");
  if (hoursList) {
    var weekDays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    var today = weekDays[new Date().getDay()];
    var todayRow = hoursList.querySelector('.hours-day[data-day="' + today + '"]');
    if (todayRow) {
      todayRow.classList.add("is-today");
    }
  }

  var navToggle = document.getElementById("navToggle");
  var primaryNav = document.getElementById("primaryNav");

  function closeNav() {
    if (primaryNav) {
      primaryNav.classList.remove("is-open");
    }
    if (navToggle) {
      navToggle.setAttribute("aria-expanded", "false");
    }
  }

  if (navToggle && primaryNav) {
    navToggle.addEventListener("click", function () {
      var isOpen = primaryNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    primaryNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeNav);
    });
  }

  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var revealObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  var toTop = document.getElementById("toTop");
  if (toTop) {
    var toTopShown = false;
    function updateToTop() {
      var show = window.scrollY > 400;
      if (show !== toTopShown) {
        toTopShown = show;
        toTop.style.display = show ? "grid" : "none";
      }
    }
    updateToTop();
    window.addEventListener("scroll", updateToTop, { passive: true });

    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  var tipTriggers = document.querySelectorAll(".pnp, .sanc, .qual");
  if (tipTriggers.length && window.matchMedia("(hover: none), (pointer: coarse)").matches) {
    tipTriggers.forEach(function (trigger) {
      trigger.addEventListener("click", function (event) {
        event.preventDefault();
        var wasOpen = trigger.classList.contains("is-open");
        tipTriggers.forEach(function (t) {
          t.classList.remove("is-open");
        });
        if (!wasOpen) {
          trigger.classList.add("is-open");
        }
      });
    });

    document.addEventListener("click", function (event) {
      var target = event.target;
      if (!target.closest || !target.closest(".pnp, .sanc, .qual")) {
        tipTriggers.forEach(function (t) {
          t.classList.remove("is-open");
        });
      }
    });
  }

  var bookingForm = document.getElementById("bookingForm");
  if (bookingForm) {
    var linesWrap = document.getElementById("bookingLines");
    var addDripBtn = document.getElementById("addDripLine");
    var bookingTotal = document.getElementById("bookingTotal");

    function linePrice(line) {
      var sel = line.querySelector(".line-drip");
      var opt = sel.options[sel.selectedIndex];
      return opt && opt.dataset && opt.dataset.price ? parseInt(opt.dataset.price, 10) : 0;
    }

    function lineQty(line) {
      return parseInt(line.querySelector(".line-qty").value, 10);
    }

    function updateTotal() {
      var total = 0;
      document.querySelectorAll(".booking-line").forEach(function (line) {
        total += linePrice(line) * lineQty(line);
      });
      bookingTotal.textContent = "Total: R" + total.toLocaleString("en-ZA");
    }

    function addLine() {
      var source = linesWrap.querySelector(".booking-line");
      var clone = source.cloneNode(true);
      var n = linesWrap.querySelectorAll(".booking-line").length + 1;

      clone.querySelectorAll("select").forEach(function (sel) {
        var baseId = sel.id;
        sel.id = baseId + "-" + n;
        var lbl = clone.querySelector('label[for="' + baseId + '"]');
        if (lbl) {
          lbl.setAttribute("for", sel.id);
        }
        sel.selectedIndex = sel.classList.contains("line-qty") ? 0 : 0;
      });

      linesWrap.appendChild(clone);
      updateTotal();
    }

    addDripBtn.addEventListener("click", addLine);

    linesWrap.addEventListener("click", function (event) {
      var btn = event.target.closest(".line-remove");
      if (!btn) {
        return;
      }
      var line = btn.closest(".booking-line");
      if (linesWrap.querySelectorAll(".booking-line").length > 1) {
        line.parentNode.removeChild(line);
        updateTotal();
      }
    });

    document.querySelectorAll(".booking-line select").forEach(function (sel) {
      sel.addEventListener("change", updateTotal);
    });

    bookingForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var name = bookingForm.querySelector("#bookingName").value.trim();
      var phone = bookingForm.querySelector("#bookingPhone").value.trim();
      var day = bookingForm.querySelector("#bookingDate").value;
      var notes = bookingForm.querySelector("#bookingNotes").value.trim();

      var lines = document.querySelectorAll(".booking-line");
      var items = [];
      var grandTotal = 0;
      var missing = [];

      lines.forEach(function (line) {
        var price = linePrice(line);
        var qty = lineQty(line);
        if (price) {
          items.push(line.querySelector(".line-drip").value + " x" + qty + " — R" + price * qty);
          grandTotal += price * qty;
        }
      });

      if (!items.length) missing.push("a drip");
      if (!name) missing.push("your name");
      if (!phone) missing.push("your phone number");

      if (missing.length) {
        alert("Please choose " + missing.join(", ") + ".");
        return;
      }

      var message = [
        "Hello Sunshine Health Care!",
        "I would like to book drip sessions.",
        "",
        "Selection:",
        items.map(function (item) { return "- " + item; }).join("\n"),
        "Total: R" + grandTotal,
        "",
        "Preferred day: " + (day || "Flexible"),
        "Name: " + name,
        "Phone: " + phone
      ].join("\n");

      if (notes) {
        message += "\nNotes: " + notes;
      }

      var via = "https://wa.me/27792131692?text=" + encodeURIComponent(message);
      window.open(via, "_blank", "noopener");
    });
  }
})();