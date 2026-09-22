document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    const targetId = button.getAttribute("aria-controls");
    const input = targetId ? document.getElementById(targetId) : null;
    const icon = button.querySelector("i");

    if (!(input instanceof HTMLInputElement) || !icon) {
        return;
    }

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
