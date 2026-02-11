"""Detection modules for supported modalities."""

from .image import ImageDetector  # noqa: F401

def __getattr__(name: str):
    if name == "TextDetector":
        from .text import TextDetector
        return TextDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
