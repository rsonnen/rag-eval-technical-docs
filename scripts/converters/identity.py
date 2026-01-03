"""Identity converter for Markdown passthrough."""

from pathlib import Path


class IdentityConverter:
    """Passthrough converter for Markdown content.

    Returns content unchanged. Used when source is already Markdown.
    """

    output_format: str = "md"

    def convert(self, source_path: Path, content: str) -> str:  # noqa: ARG002
        """Return content unchanged.

        Args:
            source_path: Path to the source file (unused).
            content: Markdown content.

        Returns:
            The same content, unchanged.
        """
        return content
