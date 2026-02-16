// Theme picker: dropdown menu with multiple themes
// Themes are applied via data-theme attribute on <html>.
// The FOUC prevention script in base.html sets data-theme before paint.
document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("theme-toggle");
    var menu = document.getElementById("theme-menu");
    var options = document.querySelectorAll(".theme-option");

    var themeColors = {
        light: "#22c55e",
        dark: "#0a0a0a",
        retro: "#1a1a0e",
        myspace: "#000033",
    };

    function getResolvedTheme(choice) {
        if (choice && choice !== "system") return choice;
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function getStoredChoice() {
        return localStorage.getItem("theme") || "system";
    }

    function applyTheme(choice) {
        var resolved = getResolvedTheme(choice);
        document.documentElement.setAttribute("data-theme", resolved);
        localStorage.setItem("theme", choice);
        updateActiveOption(choice);

        // Update meta theme-color
        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.content = themeColors[resolved] || "#22c55e";
        }

        // Notify other scripts (e.g. music.js visualizer)
        window.dispatchEvent(new CustomEvent("themechange", {
            detail: { theme: resolved, choice: choice }
        }));
    }

    function updateActiveOption(choice) {
        options.forEach(function (opt) {
            var isActive = opt.dataset.themeValue === choice;
            opt.classList.toggle("text-th-accent", isActive);
            opt.setAttribute("aria-selected", isActive ? "true" : "false");
        });
    }

    function openMenu() {
        menu.classList.remove("hidden");
        toggle.setAttribute("aria-expanded", "true");
    }

    function closeMenu() {
        menu.classList.add("hidden");
        toggle.setAttribute("aria-expanded", "false");
    }

    // Init: highlight the stored choice
    updateActiveOption(getStoredChoice());

    // Toggle menu open/close
    toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        if (menu.classList.contains("hidden")) {
            openMenu();
        } else {
            closeMenu();
        }
    });

    // Option selection
    options.forEach(function (opt) {
        opt.addEventListener("click", function (e) {
            e.stopPropagation();
            applyTheme(opt.dataset.themeValue);
            closeMenu();
        });
    });

    // Close on outside click
    document.addEventListener("click", function () {
        closeMenu();
    });

    // Prevent menu clicks from closing the menu
    menu.addEventListener("click", function (e) {
        e.stopPropagation();
    });

    // Close on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeMenu();
        }
    });

    // Listen for OS preference changes (matters when choice is "system")
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
        if (getStoredChoice() === "system") {
            applyTheme("system");
        }
    });
});
