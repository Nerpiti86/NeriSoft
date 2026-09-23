from app.core.templates import templates


def test_core_templates_parse() -> None:
    for template_name in (
        "account.html",
        "authenticated.html",
        "base.html",
        "configuration.html",
        "company.html",
        "index.html",
        "login.html",
        "roles.html",
        "setup.html",
        "users.html",
    ):
        templates.get_template(template_name)
