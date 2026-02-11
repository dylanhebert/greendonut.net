document.addEventListener("DOMContentLoaded", function () {
    // ── Scroll-reveal animations ──
    const elements = document.querySelectorAll(".scroll-reveal");

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: "0px 0px -40px 0px",
        }
    );

    elements.forEach((el) => observer.observe(el));

    // ── Nav scroll animation ──
    const mainNav = document.getElementById("main-nav");
    const navLinks = document.getElementById("nav-links");
    const navInner = document.getElementById("nav-inner");
    const navBrand = document.getElementById("nav-brand");

    if (mainNav && navLinks && navInner) {
        function updateCenterOffset() {
            // Disable transitions for instant measurement
            navLinks.style.transition = "none";
            if (navBrand) navBrand.style.transition = "none";

            // Remove at-top to measure natural (right-aligned) positions
            const wasAtTop = mainNav.classList.contains("at-top");
            mainNav.classList.remove("at-top");
            void navLinks.offsetHeight;

            // Measure positions
            var containerRect = navInner.getBoundingClientRect();
            var linksRect = navLinks.getBoundingClientRect();
            var linksLeft = linksRect.left - containerRect.left;
            var centeredLeft = (containerRect.width - linksRect.width) / 2;
            var offset = centeredLeft - linksLeft;
            navLinks.style.setProperty("--center-offset", offset + "px");

            // Restore state
            if (wasAtTop) mainNav.classList.add("at-top");
            void navLinks.offsetHeight;
            navLinks.style.transition = "";
            if (navBrand) navBrand.style.transition = "";
        }

        function handleNavScroll() {
            if (window.scrollY <= 50) {
                mainNav.classList.add("at-top");
            } else {
                mainNav.classList.remove("at-top");
            }
        }

        // Initialize — suppress transitions so nothing animates on first paint
        navLinks.style.transition = "none";
        if (navBrand) navBrand.style.transition = "none";

        updateCenterOffset();
        handleNavScroll();

        // Re-enable transitions after the browser has painted the initial state
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                navLinks.style.transition = "";
                if (navBrand) navBrand.style.transition = "";
            });
        });

        window.addEventListener("resize", updateCenterOffset);
        window.addEventListener("scroll", handleNavScroll, { passive: true });
    }
});
