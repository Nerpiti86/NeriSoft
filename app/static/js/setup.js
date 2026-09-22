"use strict";

(() => {
    function installPasswordToggles(root = document) {
        const scope = root instanceof Element ? root : document;

        scope.querySelectorAll("[data-password-toggle]").forEach((button) => {
            if (button.dataset.nerisoftPasswordToggleBound === "true") {
                return;
            }

            const targetId = button.getAttribute("aria-controls");
            const input = targetId ? document.getElementById(targetId) : null;
            const icon = button.querySelector("i");

            if (!(input instanceof HTMLInputElement) || !icon) {
                return;
            }

            button.dataset.nerisoftPasswordToggleBound = "true";
            button.addEventListener("click", () => {
                const isVisible = input.type === "text";

                input.type = isVisible ? "password" : "text";
                button.setAttribute("aria-pressed", String(!isVisible));
                button.setAttribute("aria-label", isVisible ? "Mostrar contraseña" : "Ocultar contraseña");
                icon.classList.toggle("ti-eye", isVisible);
                icon.classList.toggle("ti-eye-off", !isVisible);
                input.focus({ preventScroll: true });
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => installPasswordToggles());
    } else {
        installPasswordToggles();
    }

    document.addEventListener("htmx:afterSwap", () => {
        const workspace = document.querySelector(".workspace");
        installPasswordToggles(workspace ?? document);
    });

    window.NERISOFTPasswordToggle = Object.freeze({
        enhance: installPasswordToggles,
    });
})();
