"""dlt resources for the shared ParentSquare client.

The dlt runtime is optional. Importing the package itself does not require it;
accessing one of the decorated resources gives a clear installation error when
the ``dlt`` extra has not been installed.
"""

__all__ = [
    "calendar_events",
    "group_posts",
    "groups",
    "parentsquare",
    "posts",
    "schools",
    "school_features",
    "student_dashboards",
    "students",
]


def __getattr__(name: str):
    if name in __all__:
        from .source import (
            calendar_events,
            group_posts,
            groups,
            parentsquare,
            posts,
            school_features,
            schools,
            student_dashboards,
            students,
        )

        return {
            "calendar_events": calendar_events,
            "group_posts": group_posts,
            "groups": groups,
            "parentsquare": parentsquare,
            "posts": posts,
            "schools": schools,
            "school_features": school_features,
            "student_dashboards": student_dashboards,
            "students": students,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
