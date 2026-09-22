"use strict";

const SIDEBAR_STORAGE_KEY = "nerisoft.sidebar.collapsed";

const DOCUMENT_PREFIXES = Object.freeze({
    FAC: "FC",
    NCA: "NC",
    NDA: "ND",
    REC: "RC",
    OP: "OP",
    OC: "OC",
    REM: "RM",
    PRE: "PR",
    PED: "PD",
});

function abbreviateDocumentLabel(value) {
    const text = String(value ?? "").trim();
    if (!text) {
        return text;
    }

    const [prefix, ...rest] = text.split(/\s+/);
    const abbreviation = DOCUMENT_PREFIXES[prefix];
    return abbreviation ? [abbreviation, ...rest].join(" ") : text;
}

window.NERISOFT = Object.freeze({
    name: "NERISOFT",
    documentAbbreviations: DOCUMENT_PREFIXES,
    abbreviateDocumentLabel,
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

function applyVisibleDataConventions() {
    document.querySelectorAll(".document-number").forEach((node) => {
        node.textContent = abbreviateDocumentLabel(node.textContent);
    });

    document.querySelectorAll(".recent-documents-panel tbody td:nth-child(3)").forEach((node) => {
        node.classList.add("date-value");
    });

    document.querySelectorAll(".due-date").forEach((node) => {
        if (/\b\d{2}\/\d{2}\/\d{4}\b/.test(node.textContent ?? "")) {
            node.classList.add("date-value");
        }
    });

    document.querySelectorAll(".stock-panel tbody td:first-child").forEach((node) => {
        node.classList.remove("document-number");
        node.classList.add("code-value");
    });
}

document.addEventListener("DOMContentLoaded", () => {
    applyVisibleDataConventions();

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
