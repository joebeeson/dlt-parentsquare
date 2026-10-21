import pytest

# dlt is an optional test extra; imports below intentionally follow importorskip.
# ruff: noqa: E402, I001

dlt = pytest.importorskip("dlt")

from dlt_parentsquare import parentsquare  # noqa: E402
from dlt_parentsquare import source as source_module  # noqa: E402
from parentsquare import (
    Group,
    MFARequired,
    Post,
    School,
    Student,
    StudentClass,
    StudentDashboard,
)  # noqa: E402


def test_source_exposes_posts_and_calendar_resources() -> None:
    source = parentsquare("user@example.com", "secret")
    assert set(source.resources) == {"posts", "group_posts", "calendar_events"}


def test_source_uses_dlt_secret_and_config_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, str, str | None]] = []

    class FakeClient:
        def __init__(self, username: str, password: str, *, base_url: str) -> None:
            calls.append((username, password, base_url, None))

        async def ensure_authenticated(self) -> None:
            raise MFARequired("email", "p***@example.com")

        async def submit_mfa_code(self, code: str) -> None:
            calls[-1] = (*calls[-1][:3], code)

        async def discover_schools(self) -> list[School]:
            return [School(101, "Synthetic school")]

        async def fetch_posts(self, school: School, *, pages: int = 1) -> list[Post]:
            assert school == School(101, "Synthetic school")
            assert pages == 1
            return [
                Post(
                    id="post-1",
                    title="Synthetic post",
                    author=None,
                    published_at=None,
                    source_url="https://example.test/posts/post-1",
                    school_id=1,
                    school_name="Synthetic school",
                )
            ]

        async def discover_students(self) -> list[Student]:
            return []

        async def close(self) -> None:
            pass

    monkeypatch.setattr(source_module, "AsyncParentSquareClient", FakeClient)
    monkeypatch.setenv("SOURCES__PARENTSQUARE__USERNAME", "parent@example.com")
    monkeypatch.setenv("SOURCES__PARENTSQUARE__PASSWORD", "secret")
    monkeypatch.setenv("SOURCES__PARENTSQUARE__MFA_CODE", "123456")
    monkeypatch.setenv("SOURCES__PARENTSQUARE__BASE_URL", "https://fixture.test")

    source = parentsquare()
    records = list(source.resources["posts"])

    assert records[0]["id"] == "post-1"
    assert calls == [("parent@example.com", "secret", "https://fixture.test", "123456")]


def test_context_resources_are_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, username: str, password: str, *, base_url: str) -> None:
            pass

        async def ensure_authenticated(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def discover_schools(self) -> list[School]:
            return [School(101, "Synthetic school")]

        async def discover_students(self) -> list[Student]:
            return [Student(7, "Synthetic student", 101, "Synthetic school", "7th Grade")]

        async def fetch_student_dashboard(self, student: Student) -> StudentDashboard:
            return StudentDashboard(
                student.id,
                student.name,
                student.school_id,
                student.school_name,
                student.grade_level,
                (StudentClass("Science", ("Teacher",)),),
                ("Teacher",),
            )

        async def fetch_groups(
            self, school: School, *, students: list[Student] | None = None
        ) -> list[Group]:
            assert students == [
                Student(7, "Synthetic student", 101, "Synthetic school", "7th Grade")
            ]
            return [Group(55, "Cooking Club", school.id, school.name, student_ids=(7,))]

    monkeypatch.setattr(source_module, "AsyncParentSquareClient", FakeClient)
    source = parentsquare("user@example.com", "secret", include_context=True)
    assert set(source.resources) == {
        "posts",
        "group_posts",
        "calendar_events",
        "schools",
        "students",
        "student_dashboards",
        "groups",
        "school_features",
    }


def test_groups_resource_preserves_student_relationships(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, username: str, password: str, *, base_url: str) -> None:
            pass

        async def ensure_authenticated(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def discover_students(self) -> list[Student]:
            return [Student(7, "Synthetic student", 101, "Synthetic school", "7th Grade")]

        async def discover_schools(self) -> list[School]:
            return [School(101, "Synthetic school")]

        async def fetch_groups(
            self, school: School, *, students: list[Student] | None = None
        ) -> list[Group]:
            assert students is not None
            return [
                Group(55, "Cooking Club", school.id, school.name, student_ids=(students[0].id,))
            ]

    monkeypatch.setattr(source_module, "AsyncParentSquareClient", FakeClient)
    source = parentsquare("user@example.com", "secret", include_context=True)
    records = list(source.resources["groups"])

    assert records == [
        {
            "id": 55,
            "name": "Cooking Club",
            "school_id": 101,
            "school_name": "Synthetic school",
            "member_count": None,
            "description": None,
            "post_count": None,
            "student_ids": [7],
            "category": None,
            "visibility": None,
        }
    ]


def test_group_posts_use_feed_scoped_merge_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    school = School(101, "Synthetic school")
    group = Group(55, "Cooking Club", school.id, school.name, student_ids=(7,))
    post = Post(
        id="post-1",
        title="Club meeting",
        author="Teacher",
        published_at=None,
        source_url="https://example.test/groups/55/posts/post-1",
        school_id=school.id,
        school_name=school.name,
        group_id=group.id,
        group_name=group.name,
    )

    class FakeClient:
        def __init__(self, username: str, password: str, *, base_url: str) -> None:
            pass

        async def ensure_authenticated(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def discover_students(self) -> list[Student]:
            return [Student(7, "Synthetic student", school.id, school.name, "7th Grade")]

        async def discover_schools(self) -> list[School]:
            return [school]

        async def fetch_groups(
            self, selected_school: School, *, students: list[Student] | None = None
        ) -> list[Group]:
            assert selected_school == school
            assert students is not None
            return [group]

        async def fetch_group_posts(
            self, selected_school: School, selected_group: Group, *, pages: int = 1
        ) -> list[Post]:
            assert selected_school == school
            assert selected_group == group
            assert pages == 1
            return [post]

    monkeypatch.setattr(source_module, "AsyncParentSquareClient", FakeClient)
    source = parentsquare("user@example.com", "secret")
    records = list(source.resources["group_posts"])

    assert records == [
        {
            "id": "post-1",
            "title": "Club meeting",
            "author": "Teacher",
            "published_at": None,
            "source_url": "https://example.test/groups/55/posts/post-1",
            "school_id": 101,
            "school_name": "Synthetic school",
            "summary": None,
            "group_id": 55,
            "group_name": "Cooking Club",
            "source_id": "school:101:group:55:post:post-1",
        }
    ]
