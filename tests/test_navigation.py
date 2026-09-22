from app.account import router as account_router
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


def test_configuration_and_account_routes_are_registered() -> None:
    assert "" in _router_paths(configuration_router)
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
