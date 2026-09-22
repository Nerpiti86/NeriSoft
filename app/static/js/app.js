"use strict";

const SIDEBAR_STORAGE_KEY = "nerisoft.sidebar.collapsed";

window.NERISOFT = Object.freeze({
    name: "NERISOFT",
});

function readSidebarState() {
    try {
        return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === "1";
    } catch {
        return false;
    }
}

function writeSidebarState(collapsed) {
    try {
        window.localStorage.setItem(SIDEBAR_STORAGE_KEY, collapsed ? "1" : "0");
    } catch {
        // El almacenamiento local no es crítico para el funcionamiento del shell.
    }
}

function applySidebarState(shell, toggle, collapsed) {
    shell.classList.toggle("sidebar-collapsed", collapsed);
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.setAttribute("aria-label", collapsed ? "Expandir menú" : "Contraer menú");
    toggle.setAttribute("title", collapsed ? "Expandir menú" : "Contraer menú");

    const label = toggle.querySelector(".toggle-label");
    if (label) {
        label.textContent = collapsed ? "Expandir menú" : "Contraer menú";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const shell = document.querySelector("[data-app-shell]");
    const toggle = document.getElementById("sidebar-toggle");

    if (!shell || !toggle) {
        return;
    }

    applySidebarState(shell, toggle, readSidebarState());

    toggle.addEventListener("click", () => {
        const collapsed = !shell.classList.contains("sidebar-collapsed");
        applySidebarState(shell, toggle, collapsed);
        writeSidebarState(collapsed);
    });
});
