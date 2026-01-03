"""Base extractor interface for documentation sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentInfo:
    """Information about a document to be extracted.

    Attributes:
        source_path: Path to the source file relative to the docs root.
        title: Document title extracted from content or filename.
        format: Source format (e.g., 'rst', 'md', 'asciidoc').
    """

    source_path: Path
    title: str
    format: str


class BaseExtractor(ABC):
    """Abstract base class for documentation extractors.

    Extractors are responsible for fetching documentation sources and
    listing the documents available for conversion.
    """

    @abstractmethod
    def fetch_source(self, work_dir: Path) -> Path:
        """Fetch documentation source to work directory.

        Args:
            work_dir: Directory to store fetched source.

        Returns:
            Path to the root of the documentation within work_dir.
        """

    @abstractmethod
    def list_documents(self, source_path: Path, pattern: str) -> list[DocumentInfo]:
        """List documents matching the given pattern.

        Args:
            source_path: Path returned by fetch_source.
            pattern: Glob pattern to match files (e.g., '**/*.rst').

        Returns:
            List of DocumentInfo for each matching document.
        """

    @abstractmethod
    def cleanup(self, work_dir: Path) -> None:
        """Clean up any temporary resources.

        Args:
            work_dir: The work directory passed to fetch_source.
        """
