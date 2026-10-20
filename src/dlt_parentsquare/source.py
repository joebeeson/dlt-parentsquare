"""Optional dlt resources built on ``parentsquare-client``.

The source follows dlt's normal configuration conventions: credentials use
``dlt.secrets.value`` and non-secret options use ordinary defaults that dlt can
override from its config providers. Explicit Python arguments continue to work
for scripts and tests.
"""

from __future__ import annotations

# The optional dlt import and the external client import form one runtime
# dependency group; keep this ordering stable across Ruff platform resolvers.
# ruff: noqa: I001

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


@dlt.resource(name="schools", write_disposition="replace", primary_key="id")
async def schools(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Yield schools visible to the authenticated parent account."""
    async with _client(username, password, mfa_code=mfa_code, base_url=base_url) as client:
        for school in await client.discover_schools():
            yield school.to_record()


@dlt.resource(name="students", write_disposition="replace", primary_key="id")
async def students(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Yield only students linked to the authenticated parent account."""
    async with _client(username, password, mfa_code=mfa_code, base_url=base_url) as client:
        for student in await client.discover_students():
            yield student.to_record()


@dlt.resource(name="student_dashboards", write_disposition="replace", primary_key="student_id")
async def student_dashboards(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Yield parent-visible school, class, and teacher context for each student."""
    async with _client(username, password, mfa_code=mfa_code, base_url=base_url) as client:
        for student in await client.discover_students():
            yield (await client.fetch_student_dashboard(student)).to_record()


@dlt.resource(name="groups", write_disposition="replace", primary_key="id")
async def groups(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
):
    """Yield groups and their linked ParentSquare student IDs.

    The ``student_ids`` list is a stable relationship field. Join it to the
    ``students`` resource's ``id`` column when a downstream model needs names
    or school context; names are intentionally kept in the student dimension
    instead of duplicated on every group row.
    """
    async with _client(username, password, mfa_code=mfa_code, base_url=base_url) as client:
        linked_students = await client.discover_students()
        for school in await client.discover_schools():
            for group in await client.fetch_groups(school, students=linked_students):
                yield group.to_record()


@dlt.source(name="parentsquare")
def parentsquare(
    username: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    *,
    mfa_code: TSecretStrValue | None = None,
    base_url: str = "https://www.parentsquare.com",
    include_context: bool = False,
):
    """Return the default posts and calendar resources.

    ``username`` and ``password`` are required secrets when omitted. An MFA
    code is optional and should normally be passed for a single run rather
    than stored as a long-lived pipeline setting. Set ``include_context=True``
    to explicitly include parent-visible schools, students, dashboards, and
    groups. Context resources are opt-in because they contain household and
    school-directory data.
    """
    resources = [
        posts(username, password, mfa_code=mfa_code, base_url=base_url),
        calendar_events(username, password, mfa_code=mfa_code, base_url=base_url),
    ]
    if include_context:
        resources.extend(
            [
                schools(username, password, mfa_code=mfa_code, base_url=base_url),
                students(username, password, mfa_code=mfa_code, base_url=base_url),
                student_dashboards(username, password, mfa_code=mfa_code, base_url=base_url),
                groups(username, password, mfa_code=mfa_code, base_url=base_url),
            ]
        )
    return resources
