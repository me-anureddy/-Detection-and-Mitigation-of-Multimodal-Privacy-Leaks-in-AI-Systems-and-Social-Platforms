"""Mitigation strategies for sensitive content."""

from .image import ImageMitigator  # noqa: F401

def __getattr__(name: str):
    if name == "TextMitigator":
        from .text import TextMitigator
        return TextMitigator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
