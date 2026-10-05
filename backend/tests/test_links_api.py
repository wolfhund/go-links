import pytest


def test_create_link_returns_201_with_body(create_link) -> None:
    response = create_link("oncall", "https://example.com/rota")

    assert response.status_code == 201
    body = response.json()
    assert body["slug"] == "oncall"
    assert body["target_url"] == "https://example.com/rota"
    assert "created_at" in body


def test_create_link_normalizes_slug_case_and_whitespace(create_link) -> None:
    response = create_link("  Design-System ")

    assert response.status_code == 201
    assert response.json()["slug"] == "design-system"


def test_create_duplicate_slug_returns_409(create_link) -> None:
    create_link("payroll")

    response = create_link("PAYROLL", "https://other.example.com/")

    assert response.status_code == 409
    assert "payroll" in response.json()["detail"]


@pytest.mark.parametrize(
    "slug",
    ["", "has space", "under_score", "-leading", "trailing-", "double--dash", "a" * 65],
)
def test_create_link_rejects_invalid_slug(create_link, slug: str) -> None:
    assert create_link(slug).status_code == 422


@pytest.mark.parametrize("slug", ["api", "health", "docs", "redoc"])
def test_create_link_rejects_reserved_slug(create_link, slug: str) -> None:
    assert create_link(slug).status_code == 422


@pytest.mark.parametrize(
    "target_url",
    ["javascript:alert(1)", "ftp://files.example.com", "not a url", ""],
)
def test_create_link_rejects_non_http_targets(create_link, target_url: str) -> None:
    assert create_link("valid", target_url).status_code == 422


def test_list_links_is_empty_initially(client) -> None:
    response = client.get("/api/links")

    assert response.status_code == 200
    assert response.json() == []


def test_list_links_returns_links_sorted_by_slug(client, create_link) -> None:
    create_link("payroll")
    create_link("design-system")
    create_link("oncall")

    slugs = [link["slug"] for link in client.get("/api/links").json()]

    assert slugs == ["design-system", "oncall", "payroll"]
