document.addEventListener("DOMContentLoaded", function () {
  const body = document.querySelector("body"),
    sidebar = body.querySelector(".sidebar"),
    toggle = body.querySelector(".toggle"),
    searchBtn = body.querySelector(".search-box"),
    modeSwitch = body.querySelector(".toggle-switch"),
    modeText = body.querySelector(".mode-text");
  document.body.classList.remove("initial-hide");
  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
  });

  modeSwitch.addEventListener("click", () => {
    body.classList.toggle("dark");
    const isDarkMode = body.classList.contains("dark");
    localStorage.setItem("darkMode", isDarkMode);
  });

  // Recuperar el estado del modo almacenado
  const storedDarkMode = localStorage.getItem("darkMode");
  if (storedDarkMode) {
    body.classList.toggle("dark", storedDarkMode === "true");
  }
});
