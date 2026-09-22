"use strict";

const FILTER_SWAP = "outerHTML swap:60ms settle:100ms";

function usersFilterRequest(form) {
    if (!(form instanceof HTMLFormElement) || !form.matches(".users-filters")) {
        return null;
    }

    const workspace = form.closest(".workspace");
    if (!(workspace instanceof Element) || !window.htmx) {
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
    return { action, workspace };
}

document.addEventListener("submit", (event) => {
    const request = usersFilterRequest(event.target);
    if (!request) {
        return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();

    document.querySelectorAll(".nerisoft-select-menu").forEach((menu) => menu.remove());

    const path = `${request.action.pathname}${request.action.search}${request.action.hash}`;
    window.htmx.ajax("GET", path, {
        source: request.workspace,
        target: request.workspace,
        swap: FILTER_SWAP,
        select: ".workspace",
        push: path,
    });
}, true);
