"use strict";

const SIDEBAR_STORAGE_KEY = "nerisoft.sidebar.collapsed";
const PARTIAL_SWAP = "outerHTML swap:60ms settle:100ms";

window.NERISOFT = Object.freeze({ name: "NERISOFT" });

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
    const isRoles = path.startsWith("/configuracion/roles");
    const isConfiguration = path === "/configuracion" || path.startsWith("/configuracion/");
    const isAccount = path === "/mi-cuenta";

    const homeLink = document.querySelector('.nav-item[title="Inicio"]');
    const configurationLink = document.querySelector('.nav-item[title="Configuración"]');
    const accountLink = document.querySelector('.user-control[title="Mi cuenta"]');

    [[homeLink, isHome], [configurationLink, isConfiguration]].forEach(([link, active]) => {
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

    if (accountLink) {
        if (isAccount) {
            accountLink.setAttribute("aria-current", "page");
        } else {
            accountLink.removeAttribute("aria-current");
        }
    }

    if (isHome) {
        document.title = `${window.NERISOFT.name} · Inicio`;
    } else if (isUsers) {
        document.title = `${window.NERISOFT.name} · Usuarios`;
    } else if (isRoles) {
        document.title = `${window.NERISOFT.name} · Roles y permisos`;
    } else if (path === "/configuracion") {
        document.title = `${window.NERISOFT.name} · Configuración`;
    } else if (isAccount) {
        document.title = `${window.NERISOFT.name} · Mi cuenta`;
    }
}

function updatePermissionSelectionCount() {
    const counter = document.querySelector(".permission-selection-count");
    if (!counter) {
        return;
    }

    const selected = document.querySelectorAll(
        '.permission-option input[name="permissions"]:checked'
    ).length;
    counter.textContent = `${selected} seleccionados`;
}

function partialNavigationUrl(anchor) {
    if (!(anchor instanceof HTMLAnchorElement)) {
        return null;
    }

    if (anchor.getAttribute("aria-disabled") === "true") {
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
        '.nav-item[title="Inicio"], .nav-item[title="Configuración"], .user-control[title="Mi cuenta"]'
    );
    const isWorkspaceNavigation = Boolean(
        anchor.closest(".workspace")
        && (
            url.pathname === "/configuracion"
            || url.pathname.startsWith("/configuracion/")
            || url.pathname === "/mi-cuenta"
        )
    );

    return isShellDestination || isWorkspaceNavigation ? url : null;
}

function usersFilterUrl(form) {
    if (!(form instanceof HTMLFormElement) || !form.matches(".users-filters")) {
        return null;
    }

    const workspace = form.closest(".workspace");
    if (!(workspace instanceof Element)) {
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
    return { url: action, workspace };
}

function runPartialNavigation(url, source) {
    const workspace = document.querySelector(".workspace");
    if (!window.htmx || !workspace || !(url instanceof URL)) {
        return false;
    }

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

function initializeDynamicContent(route = window.location.href) {
    updateShellNavigation(route);
    updatePermissionSelectionCount();
}

document.addEventListener("DOMContentLoaded", () => {
    installSidebarControl();
    initializeDynamicContent();
});

document.addEventListener("click", (event) => {
    const disabledAnchor = event.target.closest?.('a[aria-disabled="true"]');
    if (disabledAnchor) {
        event.preventDefault();
        return;
    }

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

document.addEventListener("change", (event) => {
    if (event.target.matches?.('.permission-option input[name="permissions"]')) {
        updatePermissionSelectionCount();
    }
});

document.addEventListener("submit", (event) => {
    const request = usersFilterUrl(event.target);
    if (!request) {
        return;
    }

    if (runPartialNavigation(request.url, request.workspace)) {
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
    initializeDynamicContent(route);
});

document.addEventListener("htmx:historyRestore", () => {
    initializeDynamicContent(window.location.href);
});
