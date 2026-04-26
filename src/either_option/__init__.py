"""either-option: a Railway-Oriented port of the C# Optional library."""

from either_option._core import (
    Either,
    Failure,
    Nothing,
    Option,
    Some,
    Success,
    flatten,
    nothing,
    some,
)
from either_option.unsafe import OptionValueMissingError

__all__ = [
    "Either",
    "Failure",
    "Nothing",
    "Option",
    "OptionValueMissingError",
    "Some",
    "Success",
    "flatten",
    "nothing",
    "some",
]
