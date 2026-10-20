import pytest

dlt = pytest.importorskip("dlt")

from dlt_parentsquare import parentsquare  # noqa: E402


def test_source_exposes_posts_and_calendar_resources() -> None:
    source = parentsquare("user@example.com", "secret")
    assert set(source.resources) == {"posts", "calendar_events"}
