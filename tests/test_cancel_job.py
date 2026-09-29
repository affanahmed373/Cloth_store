"""Cancel clears a running generate job from session state."""

from __future__ import annotations

import threading

from cloth_store.ui.pages.finder import CANCEL_NOTICE, cancel_active_job


def test_cancel_frees_the_page_and_ignores_the_old_job() -> None:
    cancel = threading.Event()
    session = {
        "active_job": {
            "kind": "image",
            "cancel": cancel,
            "holder": {},
        },
        "image_job": True,
    }

    cancel_active_job(session)

    assert cancel.is_set()
    assert "active_job" not in session
    assert session["image_job"] is False
    assert session["cancel_notice"] is True
    assert "Stopped" in CANCEL_NOTICE
    assert "charged" in CANCEL_NOTICE
