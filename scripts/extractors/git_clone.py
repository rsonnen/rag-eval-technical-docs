"""Git-based documentation extractor using sparse checkout."""

import logging
import re
import shutil
import subprocess
from pathlib import Path

from extractors.base import BaseExtractor, DocumentInfo

logger = logging.getLogger(__name__)


class GitExtractor(BaseExtractor):
    """Extract documentation from a git repository.

    Uses sparse checkout to efficiently clone only the documentation
    directories, avoiding download of the entire repository.

    Attributes:
        repo_url: URL of the git repository.
        sparse_paths: List of paths to include in sparse checkout.
        version_tag: Optional tag or branch to checkout.
    """

    def __init__(
        self,
        repo_url: str,
        sparse_paths: list[str] | None = None,
        version_tag: str | None = None,
    ) -> None:
        """Initialize the git extractor.

        Args:
            repo_url: URL of the git repository.
            sparse_paths: Paths to include in sparse checkout. If None,
                clones the entire repository.
            version_tag: Tag or branch to checkout. If None, uses default.
        """
        self.repo_url = repo_url
        self.sparse_paths = sparse_paths
        self.version_tag = version_tag

    def fetch_source(self, work_dir: Path) -> Path:
        """Clone the repository to the work directory.

        Args:
            work_dir: Directory to clone into.

        Returns:
            Path to the cloned repository.
        """
        repo_dir = work_dir / "repo"

        if repo_dir.exists():
            logger.info("Repository already exists at %s", repo_dir)
            return repo_dir

        logger.info("Cloning %s", self.repo_url)

        if self.sparse_paths:
            self._clone_sparse(repo_dir)
        else:
            self._clone_shallow(repo_dir)

        if self.version_tag:
            self._checkout_version(repo_dir)

        return repo_dir

    def _clone_sparse(self, repo_dir: Path) -> None:
        """Clone with sparse checkout for efficiency."""
        # S603/S607: git is called with controlled arguments from config, not user input
        cmd = [
            "git",
            "clone",
            "--filter=blob:none",
            "--sparse",
            "--depth=1",
            self.repo_url,
            str(repo_dir),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603

        # Set sparse checkout paths
        if self.sparse_paths:
            # S603/S607: git is called with controlled arguments from config
            cmd = ["git", "sparse-checkout", "set", *self.sparse_paths]
            subprocess.run(  # noqa: S603
                cmd,
                cwd=repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )

    def _clone_shallow(self, repo_dir: Path) -> None:
        """Clone with shallow depth when sparse checkout not needed."""
        # S603/S607: git is called with controlled arguments from config
        cmd = ["git", "clone", "--depth=1", self.repo_url, str(repo_dir)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603

    def _checkout_version(self, repo_dir: Path) -> None:
        """Checkout a specific version tag or branch."""
        if self.version_tag is None:
            return  # No version to checkout

        # S603/S607: git is called with controlled arguments from config
        fetch_cmd = [
            "git",
            "fetch",
            "--depth=1",
            "origin",
            f"tag {self.version_tag}",
        ]
        subprocess.run(  # noqa: S603
            fetch_cmd,
            cwd=repo_dir,
            check=False,  # May fail if it's a branch, not a tag
            capture_output=True,
            text=True,
        )

        # S603/S607: git is called with controlled arguments from config
        checkout_cmd = ["git", "checkout", self.version_tag]
        subprocess.run(  # noqa: S603
            checkout_cmd,
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )

    def list_documents(self, source_path: Path, pattern: str) -> list[DocumentInfo]:
        """List all documents matching the pattern.

        Args:
            source_path: Path to the cloned repository.
            pattern: Glob pattern to match files.

        Returns:
            List of DocumentInfo for each matching file.
        """
        documents: list[DocumentInfo] = []

        for file_path in source_path.glob(pattern):
            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(source_path)
            title = self._extract_title(file_path)
            doc_format = self._detect_format(file_path)

            documents.append(
                DocumentInfo(
                    source_path=relative_path,
                    title=title,
                    format=doc_format,
                )
            )

        logger.info("Found %d documents matching %s", len(documents), pattern)
        return documents

    def _extract_title(self, file_path: Path) -> str:
        """Extract title from document content or filename.

        Args:
            file_path: Path to the document.

        Returns:
            Extracted title or filename stem.
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            first_lines = content[:2000]  # Only check beginning

            # RST title pattern (underlined with =, -, or *)
            rst_match = re.search(r"^(.+)\n[=\-*]+\n", first_lines, re.MULTILINE)
            if rst_match:
                return rst_match.group(1).strip()

            # Markdown title pattern (# heading)
            md_match = re.search(r"^#\s+(.+)$", first_lines, re.MULTILINE)
            if md_match:
                return md_match.group(1).strip()

            # AsciiDoc title pattern (= heading)
            adoc_match = re.search(r"^=\s+(.+)$", first_lines, re.MULTILINE)
            if adoc_match:
                return adoc_match.group(1).strip()

        except OSError:
            pass

        # Fallback to filename
        return file_path.stem.replace("_", " ").replace("-", " ").title()

    def _detect_format(self, file_path: Path) -> str:
        """Detect document format from file extension.

        Args:
            file_path: Path to the document.

        Returns:
            Format identifier string.
        """
        suffix = file_path.suffix.lower()
        format_map = {
            ".rst": "rst",
            ".txt": "rst",  # Django uses .txt for RST
            ".md": "md",
            ".mdx": "mdx",
            ".adoc": "asciidoc",
            ".asciidoc": "asciidoc",
            ".sgml": "docbook",
            ".xml": "docbook",
        }
        return format_map.get(suffix, "unknown")

    def cleanup(self, work_dir: Path) -> None:
        """Remove the cloned repository.

        Args:
            work_dir: The work directory containing the clone.
        """
        repo_dir = work_dir / "repo"
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
            logger.info("Cleaned up repository at %s", repo_dir)
