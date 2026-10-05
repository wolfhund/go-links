from tests.conftest import FRONTEND_URL


def test_known_slug_redirects_with_302(client, create_link) -> None:
    create_link("oncall", "https://example.com/rota")

    response = client.get("/oncall")

    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/rota"


def test_slug_lookup_is_case_insensitive(client, create_link) -> None:
    create_link("oncall", "https://example.com/rota")

    response = client.get("/OnCall")

    assert response.headers["location"] == "https://example.com/rota"


def test_unknown_slug_redirects_to_prefilled_create_form(client) -> None:
    response = client.get("/new-thing")

    assert response.status_code == 302
    assert response.headers["location"] == f"{FRONTEND_URL}/?slug=new-thing"


def test_redirect_does_not_shadow_api_routes(client) -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/api/links").status_code == 200
