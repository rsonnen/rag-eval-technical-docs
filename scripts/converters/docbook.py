"""DocBook XML to HTML converter using pypandoc.

DocBook is not supported by Docling, so we convert to HTML which Docling can ingest.
"""

import logging
from pathlib import Path

import pypandoc  # type: ignore[import-untyped]  # pypandoc lacks type stubs

from converters.base import ConversionError

logger = logging.getLogger(__name__)


class DocbookConverter:
    """Convert DocBook XML to HTML using pypandoc.

    Handles DocBook/SGML files like those used in PostgreSQL documentation.
    """

    output_format: str = "html"

    def convert(self, source_path: Path, content: str) -> str:
        """Convert DocBook content to HTML.

        Args:
            source_path: Path to the source file (for error messages).
            content: DocBook XML content to convert.

        Returns:
            HTML content.

        Raises:
            ConversionError: If pypandoc conversion fails.
        """
        try:
            html = pypandoc.convert_text(
                content,
                "html",
                format="docbook",
                extra_args=["--wrap=none"],
            )
            return str(html)
        except RuntimeError as e:
            logger.warning("DocBook conversion failed for %s: %s", source_path, e)
            raise ConversionError(source_path, str(e)) from e
