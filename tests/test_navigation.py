from app.account import router as account_router
from app.company import router as company_router
from app.configuration import router as configuration_router
from app.core.templates import templates


def _template_source(name: str) -> str:
    loader = templates.env.loader
    assert loader is not None
    source, _, _ = loader.get_source(templates.env, name)
    return source


def _router_paths(router) -> set[str]:
    return {
        path
        for route in router.routes
        if (path := getattr(route, "path", None))
    }


def test_configuration_company_and_account_routes_are_registered() -> None:
    assert "/configuracion" in _router_paths(configuration_router)
    assert "/configuracion/empresa" in _router_paths(company_router)
    assert "/mi-cuenta" in _router_paths(account_router)


def test_configuration_children_do_not_render_sibling_tabs() -> None:
    assert 'class="config-tabs"' not in _template_source("users.html")
    assert 'class="config-tabs"' not in _template_source("roles.html")


def test_users_table_represents_access_instead_of_admin_as_role() -> None:
    source = _template_source("users.html")
    assert "<th>Acceso</th>" in source
    assert "Acceso total · no requiere roles" in source


def test_shell_links_configuration_and_account_to_their_own_destinations() -> None:
    source = _template_source("authenticated.html")
    assert 'href="/configuracion"' in source
    assert 'href="/mi-cuenta"' in source


def test_configuration_exposes_company_card_only_through_permission_context() -> None:
    source = _template_source("configuration.html")
    assert "{% if can_manage_company %}" in source
    assert 'href="/configuracion/empresa"' in source
    assert "Datos de la empresa" in source
    assert source.index('id="company-settings-title"') < source.index('id="access-settings-title"')


def test_company_form_has_only_approved_sections_and_fields() -> None:
    source = _template_source("company.html")

    for heading in ("Datos generales", "Domicilio fiscal", "Contacto"):
        assert heading in source

    for field_name in (
        "legal_name",
        "trade_name",
        "tax_id",
        "tax_condition",
        "fiscal_address",
        "city",
        "province",
        "postal_code",
        "phone",
        "email",
    ):
        assert f'name="{field_name}"' in source

    assert 'name="currency"' not in source
    assert 'for="company-tax-condition"' in source
    assert 'id="company-tax-condition"' in source
    assert 'name="tax_condition"' in source
    assert "data-native-select" not in source
    assert "Nueva empresa" not in source
    assert "config-tabs" not in source


def test_shell_does_not_show_obsolete_unconfigured_company_placeholder() -> None:
    source = _template_source("authenticated.html")
    assert "Empresa sin configurar" not in source
    assert "<strong>Sin configurar</strong>" not in source
