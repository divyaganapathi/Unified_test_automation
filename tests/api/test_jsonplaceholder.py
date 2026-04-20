"""Sample API tests against JSONPlaceholder (https://jsonplaceholder.typicode.com).

These tests demonstrate the framework's API testing capabilities:
- HTTP GET / POST / PUT / PATCH / DELETE
- Fluent assertions (APIAssertions)
- Data-driven tests via DataProvider
"""

from __future__ import annotations

import pytest

from framework.api import APIClient, APIAssertions
from framework.utils.data_provider import DataProvider


# ---------------------------------------------------------------------------
# Module-level data provider
# ---------------------------------------------------------------------------

_data = DataProvider(seed=42)


# ===========================================================================
# GET tests
# ===========================================================================

class TestGetUser:
    """Tests for GET /users/{id}."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_existing_user_returns_200(self, api_client: APIClient) -> None:
        response = api_client.get("/users/1")
        (
            APIAssertions(response)
            .status(200)
            .has_key("id", "name", "email", "username")
            .key_equals("id", 1)
            .response_time_under(3000)
        )

    @pytest.mark.api
    def test_get_user_name_is_not_empty(self, api_client: APIClient) -> None:
        response = api_client.get("/users/1")
        APIAssertions(response).status(200).has_key("name")
        assert response.get("name"), "User name should not be empty"

    @pytest.mark.api
    def test_get_non_existent_user_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get("/users/9999")
        APIAssertions(response).status(404)

    @pytest.mark.api
    def test_get_all_users_returns_list(self, api_client: APIClient) -> None:
        response = api_client.get("/users")
        (
            APIAssertions(response)
            .status(200)
            .is_list()
            .list_length_at_least(5)
        )

    @pytest.mark.api
    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_multiple_users_have_required_fields(
        self, api_client: APIClient, user_id: int
    ) -> None:
        response = api_client.get(f"/users/{user_id}")
        APIAssertions(response).status(200).has_key("id", "name", "email")


# ===========================================================================
# GET posts
# ===========================================================================

class TestGetPost:
    """Tests for GET /posts."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_posts_returns_list(self, api_client: APIClient) -> None:
        response = api_client.get("/posts")
        (
            APIAssertions(response)
            .status(200)
            .is_list()
            .list_length_at_least(1)
        )

    @pytest.mark.api
    def test_get_single_post_schema(self, api_client: APIClient) -> None:
        response = api_client.get("/posts/1")
        (
            APIAssertions(response)
            .status(200)
            .has_key("userId", "id", "title", "body")
            .key_equals("id", 1)
        )

    @pytest.mark.api
    def test_get_posts_with_query_filter(self, api_client: APIClient) -> None:
        response = api_client.get("/posts", params={"userId": 1})
        APIAssertions(response).status(200).is_list()
        posts = response.body
        assert all(p["userId"] == 1 for p in posts), "All posts should belong to userId=1"


# ===========================================================================
# POST tests
# ===========================================================================

class TestCreatePost:
    """Tests for POST /posts."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_create_post_returns_201(self, api_client: APIClient) -> None:
        payload = _data.post(user_id=1)
        response = api_client.post("/posts", json=payload)
        (
            APIAssertions(response)
            .status(201)
            .has_key("id", "title", "body", "userId")
        )

    @pytest.mark.api
    def test_created_post_echoes_payload(self, api_client: APIClient) -> None:
        payload = _data.post(user_id=2, title="My Title", body="My body.")
        response = api_client.post("/posts", json=payload)
        APIAssertions(response).status(201)
        assert response.get("title") == "My Title"
        assert response.get("body") == "My body."
        assert response.get("userId") == 2


# ===========================================================================
# PUT / PATCH tests
# ===========================================================================

class TestUpdatePost:
    """Tests for PUT and PATCH /posts/{id}."""

    @pytest.mark.api
    def test_put_updates_post(self, api_client: APIClient) -> None:
        payload = {"id": 1, "title": "Updated Title", "body": "Updated body.", "userId": 1}
        response = api_client.put("/posts/1", json=payload)
        APIAssertions(response).status(200).key_equals("title", "Updated Title")

    @pytest.mark.api
    def test_patch_updates_title(self, api_client: APIClient) -> None:
        response = api_client.patch("/posts/1", json={"title": "Patched Title"})
        APIAssertions(response).status(200).key_equals("title", "Patched Title")


# ===========================================================================
# DELETE tests
# ===========================================================================

class TestDeletePost:
    """Tests for DELETE /posts/{id}."""

    @pytest.mark.api
    def test_delete_post_returns_200(self, api_client: APIClient) -> None:
        response = api_client.delete("/posts/1")
        APIAssertions(response).status(200)

    @pytest.mark.api
    def test_delete_returns_empty_body(self, api_client: APIClient) -> None:
        response = api_client.delete("/posts/1")
        # JSONPlaceholder returns {}
        assert response.body == {} or response.body == ""


# ===========================================================================
# Response-header tests
# ===========================================================================

class TestResponseHeaders:
    """Validate response headers."""

    @pytest.mark.api
    def test_content_type_is_json(self, api_client: APIClient) -> None:
        response = api_client.get("/posts/1")
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type
