"""dlt resources for the shared ParentSquare client.

The dlt runtime is optional. Importing the package itself does not require it;
accessing one of the decorated resources gives a clear installation error when
the ``dlt`` extra has not been installed.
"""

__all__ = ["calendar_events", "parentsquare", "posts"]


def __getattr__(name: str):
    if name in __all__:
        from .source import calendar_events, parentsquare, posts

        return {"calendar_events": calendar_events, "parentsquare": parentsquare, "posts": posts}[
            name
        ]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
