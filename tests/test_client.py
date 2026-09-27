import pytest

from cloth_store.services.client import make_client


def test_client_points_at_a_compatible_base_url() -> None:
    client = make_client("test-key", "http://localhost:8000/v1/")
    assert "localhost:8000/v1" in str(client.base_url)


def test_client_rejects_a_base_url_without_a_scheme() -> None:
    with pytest.raises(ValueError, match="http"):
        make_client("test-key", "api.example.com/v1")
