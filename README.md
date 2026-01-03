# rag-eval-technical-docs

Evaluation corpus of open source technical documentation for testing RAG systems.

## What This Is

This repository contains **evaluation data for RAG systems**:

- **corpus.yaml** - Evaluation scenarios for each corpus
- **metadata.json** - Document inventory
- **Generated questions** - Validated Q/A pairs (where available)

The actual documentation is not included. Use the download scripts to fetch from source repositories.

## Available Corpora

| Corpus | Documents | Description |
|--------|-----------|-------------|
| `django_docs` | 654 | Django web framework documentation |
| `git_docs` | 180 | Git version control documentation |
| `kubernetes_docs` | 1,200+ | Kubernetes container orchestration |
| `python_stdlib` | 500+ | Python standard library documentation |
| `rust_book` | 112 | The Rust Programming Language book |

## Quick Start

```bash
cd scripts
uv sync

# List available projects
uv run python download_docs.py --list

# Download documentation
uv run python download_docs.py rust-book --corpus rust_docs

# Download with document limit
uv run python download_docs.py django --corpus django_docs --max-docs 200
```

## Directory Structure

```
<corpus>/
    corpus.yaml         # Evaluation configuration
    metadata.json       # Document inventory
    docs/               # Documentation files (gitignored)

scripts/
    download_docs.py    # Download from git repositories
    config.yaml         # Project definitions
    converters/         # Format conversion modules
    extractors/         # Git clone utilities
```

## Available Projects

Projects are defined in `scripts/config.yaml`. The download script clones each git repository, extracts documentation files, and converts them to formats Docling can ingest.

| Project | Format | Converter | Description |
|---------|--------|-----------|-------------|
| `rust-book` | Markdown | identity | The Rust Programming Language book |
| `kubernetes` | Markdown | identity | Kubernetes documentation |
| `django` | RST | rst | Django web framework documentation |
| `python-stdlib` | RST | rst | Python standard library documentation |
| `react` | MDX | mdx | React documentation (strips JSX) |
| `git` | AsciiDoc | asciidoc | Git version control documentation |
| `postgresql` | DocBook | docbook | PostgreSQL database documentation |

## Converters

| Converter | Input | Output | Description |
|-----------|-------|--------|-------------|
| `identity` | Markdown | `.md` | Passthrough |
| `rst` | reStructuredText | `.html` | Converts via pypandoc |
| `asciidoc` | AsciiDoc | `.adoc` | Passthrough |
| `docbook` | DocBook/SGML | `.html` | Converts via pypandoc |
| `mdx` | MDX | `.md` | Strips JSX components |

## Metadata Format

```json
{
  "corpus": "rust_docs",
  "project": "rust-book",
  "source_url": "https://github.com/rust-lang/book.git",
  "version": "main",
  "license": "MIT/Apache-2.0",
  "converter": "identity",
  "total_documents": 112,
  "documents": {
    "ch01-00-getting-started": {
      "source_path": "src/ch01-00-getting-started.md",
      "title": "Getting Started",
      "file": "docs/src_ch01-00-getting-started.md",
      "size_bytes": 1234
    }
  }
}
```

## Adding New Projects

Edit `scripts/config.yaml`:

```yaml
projects:
  new-project:
    source_type: git
    repo_url: https://github.com/org/repo.git
    sparse_checkout:
      - docs
    file_pattern: "docs/**/*.md"
    converter: identity
    metadata:
      license: "MIT"
      version_tag: main
```
