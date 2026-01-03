"""Converters for transforming documentation formats for Docling ingestion."""

from converters.asciidoc import AsciidocConverter
from converters.base import Converter
from converters.docbook import DocbookConverter
from converters.identity import IdentityConverter
from converters.mdx import MdxConverter
from converters.rst import RstConverter

__all__ = [
    "AsciidocConverter",
    "Converter",
    "DocbookConverter",
    "IdentityConverter",
    "MdxConverter",
    "RstConverter",
]


def get_converter(name: str) -> Converter:
    """Get a converter by name.

    Args:
        name: Converter name (identity, rst, asciidoc, docbook, mdx).

    Returns:
        Converter instance.

    Raises:
        ValueError: If converter name is unknown.
    """
    converters: dict[str, type[Converter]] = {
        "identity": IdentityConverter,
        "rst": RstConverter,
        "asciidoc": AsciidocConverter,
        "docbook": DocbookConverter,
        "mdx": MdxConverter,
    }

    if name not in converters:
        valid = ", ".join(converters.keys())
        msg = f"Unknown converter: {name}. Valid options: {valid}"
        raise ValueError(msg)

    return converters[name]()
