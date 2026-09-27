"""Stand-ins for the OpenAI client."""

from __future__ import annotations

from types import SimpleNamespace

SAMPLE_JSON = """{
  "image_summary": "Green fabric",
  "dresses": [{
    "name": "Emerald Lawn",
    "category": "lawn suit",
    "occasion": "casual",
    "fabric": "lawn",
    "colors": ["emerald", "ivory"],
    "description": "A light summer suit.",
    "why_it_matches": "It keeps the green."
  }]
}"""


class FakeCompletions:
    def __init__(self, content: str) -> None:
        self.content = content
        self.kwargs: dict | None = None

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.kwargs = kwargs
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class FakeChatClient:
    def __init__(self, content: str = SAMPLE_JSON) -> None:
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


class FakeImages:
    def __init__(
        self,
        edit_b64: str | None = None,
        generate_b64: str | None = None,
        edit_error: Exception | None = None,
        edit_data: list | None = None,
    ) -> None:
        self.edit_b64 = edit_b64
        self.generate_b64 = generate_b64
        self.edit_error = edit_error
        self.edit_data = edit_data
        self.edit_kwargs: dict | None = None
        self.generate_kwargs: dict | None = None

    def edit(self, **kwargs: object) -> SimpleNamespace:
        self.edit_kwargs = kwargs
        if self.edit_error:
            raise self.edit_error
        if self.edit_data is None:
            data = [SimpleNamespace(b64_json=self.edit_b64)]
        else:
            data = self.edit_data
        return SimpleNamespace(data=data)

    def generate(self, **kwargs: object) -> SimpleNamespace:
        self.generate_kwargs = kwargs
        if self.generate_b64 is None:
            raise RuntimeError("generate unavailable")
        return SimpleNamespace(data=[SimpleNamespace(b64_json=self.generate_b64)])


class FakeImageClient:
    def __init__(self, images: FakeImages) -> None:
        self.images = images
