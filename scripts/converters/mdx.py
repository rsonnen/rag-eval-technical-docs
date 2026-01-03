"""MDX to Markdown converter that strips JSX components.

MDX is Markdown + JSX (React components). There's no established Python library
for MDX parsing - tooling is JavaScript-based (mdx-js ecosystem). This converter
uses regex to strip JSX elements while preserving text content.

Limitations:
- Complex nested JSX may not parse correctly
- JSX expressions ({...}) inside tags are not handled
- Suitable for simple documentation MDX, not complex React components
"""

import re
from pathlib import Path


class MdxConverter:
    """Convert MDX to Markdown by stripping JSX components.

    MDX is Markdown with embedded JSX (React components). This converter
    removes JSX elements to produce clean Markdown while preserving
    the text content.
    """

    output_format: str = "md"

    # Pattern for self-closing JSX tags: <Component prop="value" />
    _SELF_CLOSING_TAG = re.compile(r"<[A-Z][a-zA-Z0-9]*\s*[^>]*/\s*>", re.MULTILINE)

    # Pattern for JSX tags with content: <Component>...</Component>
    # Non-greedy match to handle nested tags
    _TAG_WITH_CONTENT = re.compile(
        r"<([A-Z][a-zA-Z0-9]*)[^>]*>(.*?)</\1>",
        re.MULTILINE | re.DOTALL,
    )

    # Pattern for import statements
    _IMPORT_STATEMENT = re.compile(r"^import\s+.*$", re.MULTILINE)

    # Pattern for export statements
    _EXPORT_STATEMENT = re.compile(r"^export\s+.*$", re.MULTILINE)

    def convert(self, source_path: Path, content: str) -> str:  # noqa: ARG002
        """Convert MDX content to Markdown.

        Args:
            source_path: Path to the source file (unused).
            content: MDX content to convert.

        Returns:
            Markdown content with JSX stripped.
        """
        result = content

        # Remove import statements
        result = self._IMPORT_STATEMENT.sub("", result)

        # Remove export statements
        result = self._EXPORT_STATEMENT.sub("", result)

        # Remove self-closing JSX tags
        result = self._SELF_CLOSING_TAG.sub("", result)

        # Remove JSX tags but keep content (recursive for nested)
        prev_result = ""
        while prev_result != result:
            prev_result = result
            result = self._TAG_WITH_CONTENT.sub(r"\2", result)

        # Clean up multiple blank lines
        result = re.sub(r"\n{3,}", "\n\n", result)

        return result.strip() + "\n"
