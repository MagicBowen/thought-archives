(function () {
  function setColorMode(mode) {
    var hljsLight = document.getElementById("hljs-light");
    var hljsDark = document.getElementById("hljs-dark");
    document.documentElement.setAttribute("data-bs-theme", mode);
    if (hljsLight && hljsDark) {
      if (mode === "dark") {
        hljsLight.disabled = true;
        hljsDark.disabled = false;
      } else {
        hljsDark.disabled = true;
        hljsLight.disabled = false;
      }
    }
  }

  function computeAutoMode() {
    var hour = new Date().getHours();
    return hour >= 19 || hour < 7 ? "dark" : "light";
  }

  function applyStoredMode() {
    var storedMode = localStorage.getItem("mkdocs-colormode");
    if (storedMode === "auto") {
      setColorMode(computeAutoMode());
    }
  }

  function syncAutoOnClick(event) {
    var mode = event.currentTarget.getAttribute("data-bs-theme-value");
    if (!mode) {
      return;
    }
    if (mode === "auto") {
      window.setTimeout(applyStoredMode, 0);
    }
  }

  applyStoredMode();

  document.querySelectorAll("[data-bs-theme-value]").forEach(function (toggle) {
    toggle.addEventListener("click", syncAutoOnClick);
  });

  window.setInterval(applyStoredMode, 60000);
})();
