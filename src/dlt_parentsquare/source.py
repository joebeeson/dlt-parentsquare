"""Optional dlt resources built on ``parentsquare-client``."""

from __future__ import annotations

try:
    import dlt
except ImportError as exc:  # pragma: no cover - installation concern
    raise ImportError(
        "Install dlt-parentsquare[dlt] to use the ParentSquare dlt source"
    ) from exc

from parentsquare import AsyncParentSquareClient


@dlt.resource(name="posts", write_disposition="merge", primary_key="id")
async def posts(username: str, password: str):
    """Yield ParentSquare posts as dlt records."""
    async with AsyncParentSquareClient(username, password) as client:
        for post in await client.fetch_all_posts():
            yield post.to_record()


@dlt.resource(name="calendar_events", write_disposition="merge", primary_key="id")
async def calendar_events(username: str, password: str):
    """Yield ParentSquare calendar events as dlt records."""
    async with AsyncParentSquareClient(username, password) as client:
        for event in await client.fetch_all_calendar_events():
            yield event.to_record()


@dlt.source(name="parentsquare")
def parentsquare(username: str, password: str):
    """Return the posts and calendar event resources."""
    return [posts(username, password), calendar_events(username, password)]
