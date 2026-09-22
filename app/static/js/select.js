"use strict";

(() => {
    const SELECTOR = "select:not([multiple]):not([data-native-select])";
    const instances = new WeakMap();
    let instanceCounter = 0;
    let openInstance = null;

    function optionElements(select) {
        return Array.from(select.options);
    }

    function selectedOption(select) {
        return optionElements(select).find((option) => option.selected) ?? select.options[0] ?? null;
    }

    function accessibleLabel(select) {
        const explicit = select.getAttribute("aria-label")?.trim();
        if (explicit) {
            return explicit;
        }

        const labelledBy = select.getAttribute("aria-labelledby");
        if (labelledBy) {
            const labelText = labelledBy
                .split(/\s+/)
                .map((id) => document.getElementById(id)?.textContent?.trim() ?? "")
                .filter(Boolean)
                .join(" ");
            if (labelText) {
                return labelText;
            }
        }

        const parentLabel = select.closest("label");
        if (parentLabel) {
            const clone = parentLabel.cloneNode(true);
            clone.querySelectorAll("select, .sr-only").forEach((node) => node.remove());
            const visibleText = clone.textContent?.trim();
            if (visibleText) {
                return visibleText;
            }

            const srOnlyText = parentLabel.querySelector(".sr-only")?.textContent?.trim();
            if (srOnlyText) {
                return srOnlyText;
            }
        }

        if (select.id) {
            const externalLabel = document.querySelector(`label[for="${CSS.escape(select.id)}"]`);
            const text = externalLabel?.textContent?.trim();
            if (text) {
                return text;
            }
        }

        return select.name ? `Seleccionar ${select.name}` : "Seleccionar opción";
    }

    function hostLabelCanCollapse(label, select) {
        if (!label) {
            return false;
        }

        const clone = label.cloneNode(true);
        clone.querySelectorAll("select, .sr-only").forEach((node) => node.remove());
        return !(clone.textContent ?? "").trim() && label.querySelectorAll("input, button, textarea").length === 0;
    }

    class NerisoftSelect {
        constructor(select) {
            this.select = select;
            this.id = ++instanceCounter;
            this.menuId = `nerisoft-select-menu-${this.id}`;
            this.label = accessibleLabel(select);
            this.optionNodes = [];
            this.hostLabel = select.closest("label");
            this.collapsedHostLabel = hostLabelCanCollapse(this.hostLabel, select);
            this.originalTabIndex = select.getAttribute("tabindex");
            this.resetHandler = null;

            this.build();
            this.bind();
            this.syncFromNative();
            instances.set(select, this);
        }

        build() {
            const rect = this.select.getBoundingClientRect();
            const measuredWidth = Math.max(Math.round(rect.width || 0), 142);

            this.root = document.createElement("div");
            this.root.className = "nerisoft-select";
            this.root.style.setProperty("--nerisoft-select-width", `${measuredWidth}px`);

            this.trigger = document.createElement("button");
            this.trigger.type = "button";
            this.trigger.className = "nerisoft-select-trigger";
            this.trigger.setAttribute("aria-haspopup", "listbox");
            this.trigger.setAttribute("aria-expanded", "false");
            this.trigger.setAttribute("aria-controls", this.menuId);
            this.trigger.setAttribute("aria-label", this.label);

            this.valueNode = document.createElement("span");
            this.valueNode.className = "nerisoft-select-value";

            this.chevron = document.createElement("i");
            this.chevron.className = "ti ti-chevron-down nerisoft-select-chevron";
            this.chevron.setAttribute("aria-hidden", "true");

            this.trigger.append(this.valueNode, this.chevron);
            this.root.append(this.trigger);

            this.menu = document.createElement("div");
            this.menu.id = this.menuId;
            this.menu.className = "nerisoft-select-menu";
            this.menu.setAttribute("role", "listbox");
            this.menu.setAttribute("aria-label", this.label);
            this.menu.hidden = true;

            this.buildOptions();
            document.body.append(this.menu);

            this.select.classList.add("nerisoft-select-native");
            this.select.dataset.nerisoftSelectEnhanced = "true";
            this.select.tabIndex = -1;

            if (this.collapsedHostLabel) {
                this.hostLabel.classList.add("nerisoft-select-host-label--collapsed");
            }

            const insertionPoint = this.hostLabel ?? this.select;
            insertionPoint.insertAdjacentElement("afterend", this.root);

            this.trigger.disabled = this.select.disabled;
            this.root.classList.toggle("is-disabled", this.select.disabled);
        }

        buildOptions() {
            this.menu.replaceChildren();
            this.optionNodes = [];

            const appendOption = (option) => {
                if (option.hidden) {
                    return;
                }

                const node = document.createElement("div");
                node.className = "nerisoft-select-option";
                node.setAttribute("role", "option");
                node.setAttribute("tabindex", "-1");
                node.dataset.value = option.value;
                node.dataset.optionIndex = String(option.index);

                const groupDisabled = option.parentElement instanceof HTMLOptGroupElement && option.parentElement.disabled;
                if (option.disabled || groupDisabled) {
                    node.classList.add("is-disabled");
                    node.setAttribute("aria-disabled", "true");
                }

                const text = document.createElement("span");
                text.className = "nerisoft-select-option-text";
                text.textContent = option.textContent ?? "";

                const check = document.createElement("i");
                check.className = "ti ti-check nerisoft-select-check";
                check.setAttribute("aria-hidden", "true");

                node.append(text, check);
                this.menu.append(node);
                this.optionNodes.push(node);
            };

            Array.from(this.select.children).forEach((child) => {
                if (child instanceof HTMLOptGroupElement) {
                    const group = document.createElement("div");
                    group.className = "nerisoft-select-group";
                    group.textContent = child.label;
                    group.setAttribute("aria-hidden", "true");
                    this.menu.append(group);
                    Array.from(child.children).forEach((option) => appendOption(option));
                    return;
                }

                if (child instanceof HTMLOptionElement) {
                    appendOption(child);
                }
            });
        }

        bind() {
            this.trigger.addEventListener("click", () => {
                this.isOpen() ? this.close() : this.open();
            });

            this.trigger.addEventListener("keydown", (event) => {
                if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
                    event.preventDefault();
                    if (!this.isOpen()) {
                        this.open();
                    }
                    this.focusByKey(event.key);
                    return;
                }

                if (event.key === "Escape" && this.isOpen()) {
                    event.preventDefault();
                    this.close({ restoreFocus: true });
                }
            });

            this.menu.addEventListener("click", (event) => {
                const optionNode = event.target.closest(".nerisoft-select-option");
                if (!optionNode || optionNode.classList.contains("is-disabled")) {
                    return;
                }
                this.selectOptionNode(optionNode);
            });

            this.menu.addEventListener("keydown", (event) => {
                const navigationKeys = ["ArrowDown", "ArrowUp", "Home", "End"];
                if (navigationKeys.includes(event.key)) {
                    event.preventDefault();
                    this.focusByKey(event.key);
                    return;
                }

                if (event.key === "Enter" || event.key === " ") {
                    const focused = document.activeElement?.closest?.(".nerisoft-select-option");
                    if (focused && !focused.classList.contains("is-disabled")) {
                        event.preventDefault();
                        this.selectOptionNode(focused);
                    }
                    return;
                }

                if (event.key === "Escape") {
                    event.preventDefault();
                    this.close({ restoreFocus: true });
                    return;
                }

                if (event.key === "Tab") {
                    this.close();
                }
            });

            this.select.addEventListener("change", () => this.syncFromNative());

            if (this.select.form) {
                this.resetHandler = () => {
                    window.setTimeout(() => this.syncFromNative(), 0);
                };
                this.select.form.addEventListener("reset", this.resetHandler);
            }
        }

        enabledOptionNodes() {
            return this.optionNodes.filter((node) => !node.classList.contains("is-disabled"));
        }

        currentOptionNode() {
            return this.optionNodes.find((node) => {
                const optionIndex = Number(node.dataset.optionIndex);
                return this.select.options[optionIndex]?.selected;
            }) ?? null;
        }

        focusByKey(key) {
            const options = this.enabledOptionNodes();
            if (!options.length) {
                return;
            }

            if (key === "Home") {
                options[0].focus();
                return;
            }

            if (key === "End") {
                options[options.length - 1].focus();
                return;
            }

            const focused = document.activeElement?.closest?.(".nerisoft-select-option");
            let index = options.indexOf(focused);

            if (index === -1) {
                const current = this.currentOptionNode();
                index = Math.max(options.indexOf(current), 0);
            } else {
                index += key === "ArrowDown" ? 1 : -1;
                if (index < 0) {
                    index = options.length - 1;
                }
                if (index >= options.length) {
                    index = 0;
                }
            }

            options[index].focus();
        }

        selectOptionNode(node) {
            const optionIndex = Number(node.dataset.optionIndex);
            const option = this.select.options[optionIndex];
            const groupDisabled = option?.parentElement instanceof HTMLOptGroupElement && option.parentElement.disabled;
            if (!option || option.disabled || groupDisabled) {
                return;
            }

            this.select.value = option.value;
            this.select.dispatchEvent(new Event("change", { bubbles: true }));
            this.close({ restoreFocus: true });
        }

        syncFromNative() {
            const selected = selectedOption(this.select);
            this.valueNode.textContent = selected?.textContent ?? "";
            this.trigger.disabled = this.select.disabled;
            this.root.classList.toggle("is-disabled", this.select.disabled);

            this.optionNodes.forEach((node) => {
                const optionIndex = Number(node.dataset.optionIndex);
                const isSelected = Boolean(this.select.options[optionIndex]?.selected);
                node.classList.toggle("is-selected", isSelected);
                node.setAttribute("aria-selected", String(isSelected));
            });
        }

        isOpen() {
            return openInstance === this;
        }

        open() {
            if (this.select.disabled || !this.optionNodes.length) {
                return;
            }

            if (openInstance && openInstance !== this) {
                openInstance.close();
            }

            openInstance = this;
            this.root.classList.add("is-open");
            this.menu.hidden = false;
            this.trigger.setAttribute("aria-expanded", "true");
            this.positionMenu();

            const current = this.currentOptionNode() ?? this.enabledOptionNodes()[0];
            current?.focus({ preventScroll: true });
            current?.scrollIntoView({ block: "nearest" });
        }

        close({ restoreFocus = false } = {}) {
            if (!this.isOpen()) {
                return;
            }

            openInstance = null;
            this.root.classList.remove("is-open");
            this.menu.hidden = true;
            this.trigger.setAttribute("aria-expanded", "false");

            if (restoreFocus && this.trigger.isConnected) {
                this.trigger.focus({ preventScroll: true });
            }
        }

        positionMenu() {
            if (this.menu.hidden || !this.trigger.isConnected) {
                return;
            }

            const rect = this.trigger.getBoundingClientRect();
            const viewportPadding = 8;
            const gap = 5;
            const maxHeight = 260;
            const spaceBelow = window.innerHeight - rect.bottom - viewportPadding;
            const spaceAbove = rect.top - viewportPadding;
            const openAbove = spaceBelow < 180 && spaceAbove > spaceBelow;

            this.menu.style.minWidth = `${Math.round(rect.width)}px`;
            this.menu.style.maxWidth = `${Math.max(Math.round(rect.width), 360)}px`;
            this.menu.style.left = `${Math.max(viewportPadding, Math.round(rect.left))}px`;
            this.menu.style.maxHeight = `${Math.min(maxHeight, Math.max(112, openAbove ? spaceAbove - gap : spaceBelow - gap))}px`;

            if (openAbove) {
                this.menu.style.top = "auto";
                this.menu.style.bottom = `${Math.max(viewportPadding, Math.round(window.innerHeight - rect.top + gap))}px`;
            } else {
                this.menu.style.bottom = "auto";
                this.menu.style.top = `${Math.round(rect.bottom + gap)}px`;
            }

            const menuRect = this.menu.getBoundingClientRect();
            if (menuRect.right > window.innerWidth - viewportPadding) {
                const correctedLeft = Math.max(viewportPadding, window.innerWidth - viewportPadding - menuRect.width);
                this.menu.style.left = `${Math.round(correctedLeft)}px`;
            }
        }

        destroy() {
            if (this.isOpen()) {
                this.close();
            }

            if (this.resetHandler && this.select.form) {
                this.select.form.removeEventListener("reset", this.resetHandler);
            }

            this.menu.remove();
            this.root.remove();
            this.select.classList.remove("nerisoft-select-native");
            delete this.select.dataset.nerisoftSelectEnhanced;
            if (this.originalTabIndex === null) {
                this.select.removeAttribute("tabindex");
            } else {
                this.select.setAttribute("tabindex", this.originalTabIndex);
            }
            if (this.collapsedHostLabel) {
                this.hostLabel?.classList.remove("nerisoft-select-host-label--collapsed");
            }
            instances.delete(this.select);
        }
    }

    function enhanceSelects(root = document) {
        const scope = root instanceof Element || root instanceof Document ? root : document;
        scope.querySelectorAll(SELECTOR).forEach((select) => {
            if (select.dataset.nerisoftSelectEnhanced === "true" || instances.has(select)) {
                return;
            }
            new NerisoftSelect(select);
        });
    }

    function destroyWithin(root) {
        if (!(root instanceof Element) && !(root instanceof Document)) {
            return;
        }

        const candidates = [];
        if (root instanceof HTMLSelectElement && root.matches(SELECTOR)) {
            candidates.push(root);
        }
        candidates.push(...root.querySelectorAll("select[data-nerisoft-select-enhanced='true']"));

        candidates.forEach((select) => {
            instances.get(select)?.destroy();
        });
    }

    document.addEventListener("pointerdown", (event) => {
        if (!openInstance) {
            return;
        }
        if (!openInstance.root.contains(event.target) && !openInstance.menu.contains(event.target)) {
            openInstance.close();
        }
    });

    window.addEventListener("resize", () => {
        openInstance?.positionMenu();
    });

    window.addEventListener(
        "scroll",
        () => {
            openInstance?.positionMenu();
        },
        true,
    );

    document.addEventListener("DOMContentLoaded", () => {
        enhanceSelects();

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node instanceof Element) {
                        destroyWithin(node);
                    }
                });

                mutation.addedNodes.forEach((node) => {
                    if (!(node instanceof Element)) {
                        return;
                    }

                    if (node.matches?.(SELECTOR)) {
                        if (node.dataset.nerisoftSelectEnhanced !== "true") {
                            new NerisoftSelect(node);
                        }
                        return;
                    }

                    enhanceSelects(node);
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    });

    window.NERISOFTSelect = Object.freeze({
        enhance: enhanceSelects,
        destroyWithin,
    });
})();
