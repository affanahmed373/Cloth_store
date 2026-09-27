from cloth_store.ui.components.results import format_elapsed


def test_elapsed_time_is_readable() -> None:
    assert format_elapsed(None) is None
    assert format_elapsed(12.34) == "Took 12.3 s"
    assert format_elapsed(75) == "Took 1 min 15 s"
