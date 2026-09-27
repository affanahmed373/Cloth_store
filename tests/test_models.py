import pytest

from cloth_store.models import SuggestionResult


def test_parses_a_dress_payload() -> None:
    result = SuggestionResult.from_payload(
        """{
          "image_summary": " Green fabric ",
          "dresses": [{
            "name": "Emerald Lawn",
            "category": "lawn suit",
            "occasion": "casual",
            "fabric": "lawn",
            "colors": "emerald",
            "description": "A light summer suit.",
            "why_it_matches": "It keeps the green."
          }, "skip me"]
        }"""
    )

    assert result.image_summary == "Green fabric"
    assert len(result.dresses) == 1
    dress = result.dresses[0]
    assert dress.name == "Emerald Lawn"
    assert dress.colors == ["emerald"]
    assert dress.image_path is None


def test_rejects_a_non_object_payload() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        SuggestionResult.from_payload("[1, 2]")
