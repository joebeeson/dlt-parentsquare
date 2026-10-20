"""Optional dlt resources built on ``parentsquare-client``.

The source follows dlt's normal configuration conventions: credentials use
``dlt.secrets.value`` and non-secret options use ordinary defaults that dlt can
override from its config providers. Explicit Python arguments continue to work
for scripts and tests.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

try:
    import dlt
except ImportError as exc:  # pragma: no cover - installation concern
    raise ImportError("Install dlt-parentsquare[dlt] to use the ParentSquare dlt source") from exc

from dlt.common.typing import TSecretStrValue

from parentsquare import AsyncParentSquareClient, MFARequired


@asynccontextmanager
async def _client(
    username: str,
    password: str,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
) -> AsyncIterator[AsyncParentSquareClient]:
    """Open one client and complete an optional MFA challenge."""
    client = AsyncParentSquareClient(username, password, base_url=base_url)
    try:
        try:
            await client.ensure_authenticated()
        except MFARequired:
            if not mfa_code:
                raise
            await client.submit_mfa_code(str(mfa_code))
        yield client
    finally:
        await client.close()


@dlt.resource(name="posts", write_disposition="merge", primary_key="id")
async def posts(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Yield ParentSquare posts as dlt records."""
    async with _client(username, password, mfa_code=mfa_code, base_url=base_url) as client:
        for post in await client.fetch_all_posts():
            yield post.to_record()


@dlt.resource(name="calendar_events", write_disposition="merge", primary_key="id")
async def calendar_events(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Yield ParentSquare calendar events as dlt records."""
    async with _client(username, password, mfa_code=mfa_code, base_url=base_url) as client:
        for event in await client.fetch_all_calendar_events():
            yield event.to_record()


@dlt.source(name="parentsquare")
def parentsquare(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Return the posts and calendar event resources.

    ``username`` and ``password`` are required secrets when omitted. An MFA
    code is optional and should normally be passed for a single run rather
    than stored as a long-lived pipeline setting.
    """
    return [
        posts(username, password, mfa_code=mfa_code, base_url=base_url),
        calendar_events(username, password, mfa_code=mfa_code, base_url=base_url),
    ]
