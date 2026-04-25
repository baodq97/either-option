"""optional-python: a Railway-Oriented port of the C# Optional library."""

from optional_python._core import (
    Either,
    Failure,
    Nothing,
    Option,
    Some,
    Success,
    nothing,
    some,
)
from optional_python.unsafe import OptionValueMissingError

__all__ = [
    "Either",
    "Failure",
    "Nothing",
    "Option",
    "OptionValueMissingError",
    "Some",
    "Success",
    "nothing",
    "some",
]
