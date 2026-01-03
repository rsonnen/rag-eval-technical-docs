"""AsciiDoc passthrough converter.

Docling supports AsciiDoc natively, so no conversion is needed.
"""

from pathlib import Path


class AsciidocConverter:
    """Passthrough converter for AsciiDoc content.

    Returns content unchanged since Docling supports AsciiDoc natively.
    """

    output_format: str = "adoc"

    def convert(self, source_path: Path, content: str) -> str:  # noqa: ARG002
        """Return AsciiDoc content unchanged.

        Args:
            source_path: Path to the source file (unused).
            content: AsciiDoc content.

        Returns:
            The same content, unchanged.
        """
        return content
