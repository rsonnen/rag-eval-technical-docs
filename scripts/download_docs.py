#!/usr/bin/env python
"""Download technical documentation for RAG evaluation.

Clones git repositories, extracts documentation files, and converts them
to formats Docling can ingest (MD, HTML, ADOC). Projects are defined in
config.yaml.

Usage:
    uv run python download_docs.py <project> --corpus <name> [--max-docs N]

    # List available projects
    uv run python download_docs.py --list

    # Download rust book
    uv run python download_docs.py rust-book --corpus rust_docs

    # Download with document limit
    uv run python download_docs.py django --corpus django_docs --max-docs 200
"""

import argparse
import json
import logging
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from tqdm import tqdm

from converters import Converter, get_converter
from converters.base import ConversionError
from extractors import DocumentInfo, GitExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default data directory for extracted documentation
DEFAULT_DATA_DIR = Path("/mnt/x/rag_datasets/technical_docs")


def load_config(config_path: Path) -> dict[str, Any]:
    """Load project configuration from YAML file.

    Args:
        config_path: Path to config.yaml file.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        yaml.YAMLError: If config file is invalid.
        TypeError: If config file doesn't contain a dictionary.
    """
    with config_path.open() as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        msg = f"Config must be a dictionary, got {type(config).__name__}"
        raise TypeError(msg)
    return config


def list_projects(config: dict[str, Any]) -> None:
    """Print available projects from configuration.

    Args:
        config: Configuration dictionary.
    """
    projects = config.get("projects", {})
    print("\nAvailable projects:")
    print("-" * 60)
    for name, project in projects.items():
        converter = project.get("converter", "unknown")
        repo_url = project.get("repo_url", "N/A")
        print(f"  {name:<20} ({converter}) - {repo_url}")
    print()


def create_extractor(project_config: dict[str, Any]) -> GitExtractor:
    """Create an extractor instance from project configuration.

    Args:
        project_config: Project configuration dictionary.

    Returns:
        Configured extractor instance.

    Raises:
        ValueError: If source_type is unsupported.
    """
    source_type = project_config.get("source_type", "git")

    if source_type == "git":
        return GitExtractor(
            repo_url=project_config["repo_url"],
            sparse_paths=project_config.get("sparse_checkout"),
            version_tag=project_config.get("metadata", {}).get("version_tag"),
        )

    msg = f"Unsupported source_type: {source_type}"
    raise ValueError(msg)


def sanitize_filename(path: Path) -> str:
    """Convert a file path to a safe filename.

    Args:
        path: Source file path.

    Returns:
        Sanitized filename suitable for output.
    """
    # Remove extension and convert path separators to underscores
    name = str(path.with_suffix("")).replace("/", "_").replace("\\", "_")
    # Remove leading underscores
    return name.lstrip("_")


def extract_project(
    project_name: str,
    project_config: dict[str, Any],
    corpus_name: str,
    data_dir: Path,
    max_docs: int | None = None,
) -> dict[str, Any]:
    """Extract documentation for a single project.

    Args:
        project_name: Name of the project to extract.
        project_config: Project configuration dictionary.
        corpus_name: Name for the output corpus directory.
        data_dir: Base directory for output data.
        max_docs: Maximum number of documents to extract.

    Returns:
        Metadata dictionary for the extracted corpus.
    """
    logger.info("Extracting project: %s -> %s", project_name, corpus_name)

    # Create output directory
    output_dir = data_dir / corpus_name
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Get extractor and converter
    extractor = create_extractor(project_config)
    converter_name = project_config.get("converter", "identity")
    converter = get_converter(converter_name)

    # Prepare metadata
    metadata: dict[str, Any] = {
        "corpus": corpus_name,
        "project": project_name,
        "source_url": project_config.get("repo_url", ""),
        "version": project_config.get("metadata", {}).get("version_tag", "latest"),
        "license": project_config.get("metadata", {}).get("license", "unknown"),
        "converter": converter_name,
        "extraction_date": datetime.now(UTC).isoformat(),
        "total_documents": 0,
        "documents": {},
    }

    # Extract in a temporary directory
    with tempfile.TemporaryDirectory() as work_dir:
        work_path = Path(work_dir)

        # Fetch source
        logger.info("Fetching source...")
        source_path = extractor.fetch_source(work_path)

        # List documents
        file_pattern = project_config.get("file_pattern", "**/*")
        documents = extractor.list_documents(source_path, file_pattern)

        # Limit document count if specified
        if max_docs and len(documents) > max_docs:
            logger.info("Limiting to %d documents (found %d)", max_docs, len(documents))
            documents = documents[:max_docs]

        # Convert and write documents
        converted_count = 0
        for doc in tqdm(documents, desc="Converting"):
            try:
                output_file = convert_document(
                    doc=doc,
                    source_path=source_path,
                    output_dir=docs_dir,
                    converter=converter,
                )

                metadata["documents"][doc.source_path.stem] = {
                    "source_path": str(doc.source_path),
                    "title": doc.title,
                    "file": f"docs/{output_file.name}",
                    "size_bytes": output_file.stat().st_size,
                }
                converted_count += 1

            except ConversionError as e:
                logger.warning("Skipping %s: %s", doc.source_path, e)
            except OSError as e:
                logger.warning("IO error for %s: %s", doc.source_path, e)

        metadata["total_documents"] = converted_count
        logger.info("Converted %d documents", converted_count)

        # Write metadata
        metadata_path = output_dir / "metadata.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)

        logger.info("Wrote metadata to %s", metadata_path)

    return metadata


def convert_document(
    doc: DocumentInfo,
    source_path: Path,
    output_dir: Path,
    converter: Converter,
) -> Path:
    """Convert a single document and write to output directory.

    Args:
        doc: Document information.
        source_path: Path to the source repository.
        output_dir: Directory to write converted files.
        converter: Converter instance to use.

    Returns:
        Path to the written output file.

    Raises:
        ConversionError: If conversion fails.
        OSError: If file operations fail.
    """
    # Read source content
    full_path = source_path / doc.source_path
    content = full_path.read_text(encoding="utf-8", errors="replace")

    # Convert to target format
    converted = converter.convert(doc.source_path, content)

    # Write output with format-appropriate extension
    output_name = sanitize_filename(doc.source_path) + f".{converter.output_format}"
    output_path = output_dir / output_name
    output_path.write_text(converted, encoding="utf-8")

    return output_path


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Extract technical documentation for RAG evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "project",
        nargs="?",
        help="Project to extract (use --list to see options)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available projects",
    )
    parser.add_argument(
        "--corpus",
        help="Name for the output corpus directory",
    )
    parser.add_argument(
        "--max-docs",
        type=int,
        help="Maximum number of documents to extract",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Base directory for output data (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "config.yaml",
        help="Path to configuration file",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", args.config)
        return 1
    except yaml.YAMLError as e:
        logger.error("Invalid configuration file: %s", e)
        return 1

    # List projects if requested
    if args.list:
        list_projects(config)
        return 0

    # Require project argument for extraction
    if not args.project:
        parser.print_help()
        return 1

    # Validate project
    projects = config.get("projects", {})
    if args.project not in projects:
        logger.error("Unknown project: %s", args.project)
        list_projects(config)
        return 1

    # Use project name as corpus name if not specified
    corpus_name = args.corpus or args.project.replace("-", "_")

    # Extract the project
    try:
        extract_project(
            project_name=args.project,
            project_config=projects[args.project],
            corpus_name=corpus_name,
            data_dir=args.data_dir,
            max_docs=args.max_docs,
        )
    except Exception as e:
        logger.exception("Extraction failed: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
