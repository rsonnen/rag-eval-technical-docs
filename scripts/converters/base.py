"""Base converter protocol for documentation format conversion."""

from pathlib import Path
from typing import Protocol


class Converter(Protocol):
    """Protocol for document format converters.

    Converters transform source documentation formats into formats that
    Docling can ingest (MD, HTML, ADOC). Each converter specifies its
    output format via the output_format property.
    """

    output_format: str
    """Output file extension without dot (e.g., 'md', 'html', 'adoc')."""

    def convert(self, source_path: Path, content: str) -> str:
        """Convert source content to the target format.

        Args:
            source_path: Path to the source file (for context/error messages).
            content: Source content to convert.

        Returns:
            Converted content in the format specified by output_format.

        Raises:
            ConversionError: If conversion fails.
        """
        ...


class ConversionError(Exception):
    """Raised when document conversion fails."""

    def __init__(self, source_path: Path, message: str) -> None:
        """Initialize conversion error.

        Args:
            source_path: Path to the file that failed conversion.
            message: Error description.
        """
        self.source_path = source_path
        super().__init__(f"Failed to convert {source_path}: {message}")
