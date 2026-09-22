"use strict";

const SIDEBAR_STORAGE_KEY = "nerisoft.sidebar.collapsed";
const PARTIAL_SWAP = "outerHTML swap:60ms settle:100ms";

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

function installShellDestinations() {
    const homeLink = document.querySelector('.nav-item[title="Inicio"]');
    if (homeLink && homeLink.getAttribute("href") === "#") {
        homeLink.setAttribute("href", "/");
    }

    const configurationLink = document.querySelector('.nav-item[title="Configuración"]');
    if (configurationLink && configurationLink.getAttribute("href") === "#") {
        configurationLink.setAttribute("href", "/configuracion/usuarios");
    }
}

function ensureStylesheet(path) {
    const exists = Array.from(document.querySelectorAll('link[rel="stylesheet"][href]')).some((link) => {
        try {
            return new URL(link.href, window.location.href).pathname === path;
        } catch {
            return false;
        }
    });

    if (exists) {
        return;
    }

    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = path;
    link.dataset.nerisoftSharedAsset = "";
    document.head.append(link);
}

function ensureScript(path) {
    const exists = Array.from(document.querySelectorAll("script[src]")).some((script) => {
        try {
            return new URL(script.src, window.location.href).pathname === path;
        } catch {
            return false;
        }
    });

    if (exists) {
        return;
    }

    const script = document.createElement("script");
    script.src = path;
    script.dataset.nerisoftSharedAsset = "";
    document.head.append(script);
}

function preloadAuthenticatedAssets() {
    if (!document.querySelector("[data-app-shell]")) {
        return;
    }

    ensureStylesheet("/static/css/dashboard.css");
    ensureStylesheet("/static/css/users.css");
    ensureScript("/static/js/setup.js");
}

function applyVisibleDataConventions(root = document) {
    const scope = root instanceof Element ? root : document;

    scope.querySelectorAll(".document-number").forEach((node) => {
        node.textContent = abbreviateDocumentLabel(node.textContent);
    });

    scope.querySelectorAll(".recent-documents-panel tbody td:nth-child(3)").forEach((node) => {
        node.classList.add("date-value");
    });

    scope.querySelectorAll(".due-date").forEach((node) => {
        if (/\b\d{2}\/\d{2}\/\d{4}\b/.test(node.textContent ?? "")) {
            node.classList.add("date-value");
        }
    });

    scope.querySelectorAll(".stock-panel tbody td:first-child").forEach((node) => {
        node.classList.remove("document-number");
        node.classList.add("code-value");
    });
}

function applyAuthenticatedUser(root = document) {
    const firstName = document.body.dataset.currentUserFirstName?.trim();
    const initials = document.body.dataset.currentUserInitials?.trim();
    const scope = root instanceof Element ? root : document;

    if (firstName) {
        const userName = document.querySelector(".user-name");
        const greeting = scope.querySelector(".dashboard-title-row h1");

        if (userName) {
            userName.textContent = firstName;
        }

        if (greeting) {
            greeting.textContent = `Buen día, ${firstName}`;
        }
    }

    if (initials) {
        const avatar = document.querySelector(".user-avatar");
        if (avatar) {
            avatar.textContent = initials;
        }
    }
}

function pagePath(value = window.location.href) {
    try {
        return new URL(value, window.location.href).pathname;
    } catch {
        return window.location.pathname;
    }
}

function updateShellNavigation(value = window.location.href) {
    const path = pagePath(value);
    const isHome = path === "/";
    const isUsers = path.startsWith("/configuracion/usuarios");

    const homeLink = document.querySelector('.nav-item[title="Inicio"]');
    const configurationLink = document.querySelector('.nav-item[title="Configuración"]');

    [[homeLink, isHome], [configurationLink, isUsers]].forEach(([link, active]) => {
        if (!link) {
            return;
        }

        link.classList.toggle("is-active", active);
        if (active) {
            link.setAttribute("aria-current", "page");
        } else {
            link.removeAttribute("aria-current");
        }
    });

    if (isHome) {
        document.title = `${window.NERISOFT.name} · Inicio`;
    } else if (isUsers) {
        document.title = `${window.NERISOFT.name} · Usuarios`;
    }
}

function installLogoutControl() {
    const actions = document.querySelector(".topbar-actions");
    const userControl = actions?.querySelector(".user-control");
    const csrfToken = document.body.dataset.csrfToken?.trim();

    if (!actions || !userControl || !csrfToken || actions.querySelector("[data-logout-form]")) {
        return;
    }

    const form = document.createElement("form");
    form.method = "post";
    form.action = "/logout";
    form.dataset.logoutForm = "";
    form.setAttribute("aria-label", "Cerrar sesión");

    const tokenInput = document.createElement("input");
    tokenInput.type = "hidden";
    tokenInput.name = "csrf_token";
    tokenInput.value = csrfToken;

    const button = document.createElement("button");
    button.type = "submit";
    button.className = "icon-button";
    button.setAttribute("aria-label", "Cerrar sesión");
    button.setAttribute("title", "Cerrar sesión");

    const icon = document.createElement("i");
    icon.className = "ti ti-logout";
    icon.setAttribute("aria-hidden", "true");

    button.append(icon);
    form.append(tokenInput, button);
    userControl.insertAdjacentElement("afterend", form);
}

function installSidebarControl() {
    const shell = document.querySelector("[data-app-shell]");
    const toggle = document.getElementById("sidebar-toggle");

    if (!shell || !toggle) {
        return;
    }

    applySidebarState(shell, toggle, readSidebarState());

    if (toggle.dataset.nerisoftSidebarBound === "true") {
        return;
    }

    toggle.dataset.nerisoftSidebarBound = "true";
    toggle.addEventListener("click", () => {
        const collapsed = !shell.classList.contains("sidebar-collapsed");
        applySidebarState(shell, toggle, collapsed);
        writeSidebarState(collapsed);
    });
}

function isPlainPrimaryClick(event) {
    return (
        event.button === 0
        && !event.defaultPrevented
        && !event.metaKey
        && !event.ctrlKey
        && !event.shiftKey
        && !event.altKey
    );
}

function partialNavigationUrl(anchor) {
    if (!(anchor instanceof HTMLAnchorElement)) {
        return null;
    }

    if (anchor.target && anchor.target !== "_self") {
        return null;
    }

    let url;
    try {
        url = new URL(anchor.href, window.location.href);
    } catch {
        return null;
    }

    if (url.origin !== window.location.origin) {
        return null;
    }

    const isShellDestination = anchor.matches(
        '.nav-item[title="Inicio"], .nav-item[title="Configuración"]'
    );
    const isUsersNavigation = Boolean(
        anchor.closest(".workspace")
        && url.pathname.startsWith("/configuracion/usuarios")
    );

    return isShellDestination || isUsersNavigation ? url : null;
}

function usersFilterUrl(form) {
    if (!(form instanceof HTMLFormElement) || !form.closest(".workspace")) {
        return null;
    }

    const method = (form.getAttribute("method") || "get").toLowerCase();
    const action = new URL(form.action || window.location.href, window.location.href);

    if (
        method !== "get"
        || action.origin !== window.location.origin
        || action.pathname !== "/configuracion/usuarios"
    ) {
        return null;
    }

    const params = new URLSearchParams();
    for (const [name, value] of new FormData(form).entries()) {
        if (typeof value === "string") {
            params.append(name, value);
        }
    }
    action.search = params.toString();
    return action;
}

function cleanDetachedSelectMenus() {
    document.querySelectorAll(".nerisoft-select-menu").forEach((menu) => menu.remove());
}

function runPartialNavigation(url, source) {
    const workspace = document.querySelector(".workspace");
    if (!window.htmx || !workspace || !(url instanceof URL)) {
        return false;
    }

    cleanDetachedSelectMenus();
    const path = `${url.pathname}${url.search}${url.hash}`;

    window.htmx.ajax("GET", path, {
        source,
        target: workspace,
        swap: PARTIAL_SWAP,
        select: ".workspace",
        push: path,
    });

    return true;
}

function redirectedHtmxRequest(event) {
    const xhr = event.detail?.xhr;
    const requestPath = event.detail?.requestConfig?.path;

    if (!xhr?.responseURL || !requestPath) {
        return false;
    }

    try {
        const responseUrl = new URL(xhr.responseURL, window.location.href);
        const requestedUrl = new URL(requestPath, window.location.href);

        if (
            responseUrl.origin === window.location.origin
            && requestedUrl.origin === window.location.origin
            && responseUrl.pathname !== requestedUrl.pathname
        ) {
            event.preventDefault();
            window.location.assign(responseUrl.href);
            return true;
        }
    } catch {
        return false;
    }

    return false;
}

function initializeDynamicContent(root = document, route = window.location.href) {
    applyVisibleDataConventions(root);
    applyAuthenticatedUser(root);
    updateShellNavigation(route);
}

document.addEventListener("DOMContentLoaded", () => {
    installShellDestinations();
    preloadAuthenticatedAssets();
    installLogoutControl();
    installSidebarControl();
    initializeDynamicContent();
});

document.addEventListener("click", (event) => {
    if (!isPlainPrimaryClick(event)) {
        return;
    }

    const anchor = event.target.closest?.("a");
    const url = partialNavigationUrl(anchor);
    if (!url) {
        return;
    }

    if (runPartialNavigation(url, anchor)) {
        event.preventDefault();
    }
});

document.addEventListener("submit", (event) => {
    const form = event.target;
    const url = usersFilterUrl(form);
    if (!url) {
        return;
    }

    if (runPartialNavigation(url, form)) {
        event.preventDefault();
    }
});

document.addEventListener("htmx:beforeSwap", (event) => {
    redirectedHtmxRequest(event);
});

document.addEventListener("htmx:afterSwap", (event) => {
    const workspace = document.querySelector(".workspace");
    if (!(workspace instanceof Element)) {
        return;
    }

    const route = event.detail?.requestConfig?.path ?? window.location.href;
    initializeDynamicContent(workspace, route);
});

document.addEventListener("htmx:historyRestore", () => {
    initializeDynamicContent(document, window.location.href);
});
