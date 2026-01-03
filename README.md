# rag-eval-technical-docs

Evaluation corpus of open source technical documentation for testing RAG systems.

## What This Is

This repository contains **evaluation data for RAG systems**:

- **corpus.yaml** - Evaluation configuration defining domain context and testing scenarios
- **Generated questions** - Validated Q/A pairs for evaluation (where available)
- **metadata.json** - Document inventory with source info
- **Extract scripts** - Fetch and convert documentation from open source projects

The actual documentation is not included due to licensing - use the extract scripts to fetch from source repositories.

## Purpose

Technical documentation is a prime RAG use case. This corpus tests:

- **Retrieval**: Hierarchical navigation, API reference lookup, conceptual vs. reference content
- **Document processing**: Markdown with code blocks, RST with directives, interlinked pages
- **Query types**: "How do I use X?", "What's the difference between Y and Z?", troubleshooting

## Available Corpora

| Corpus | Project | Format | Description |
|--------|---------|--------|-------------|
| `django_docs` | Django | RST→HTML | Django web framework documentation |
| `git_docs` | Git | AsciiDoc | Git version control documentation |
| `kubernetes_docs` | Kubernetes | Markdown | Kubernetes container orchestration |
| `python_stdlib` | Python | RST→HTML | Python standard library documentation |
| `rust_book` | Rust | Markdown | The Rust Programming Language book |

## Usage

### Install dependencies

```bash
cd scripts
uv sync
```

### Extract documentation

```bash
# List available projects
uv run python extract_docs.py --list

# Extract a project
uv run python extract_docs.py rust-book --corpus rust_docs

# Extract with document limit
uv run python extract_docs.py django --corpus django_docs --max-docs 200
```

## Output Structure

```
<corpus_name>/
    corpus.yaml               # Evaluation configuration
    metadata.json             # Corpus metadata
    docs/                     # Extracted documents (gitignored)
        document_name.md      # Markdown
        another_doc.html      # HTML (from RST/DocBook)
```

## Available Projects

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
| `identity` | Markdown | `.md` | Passthrough (Docling supports MD natively) |
| `rst` | reStructuredText | `.html` | Converts via pypandoc |
| `asciidoc` | AsciiDoc | `.adoc` | Passthrough (Docling supports AsciiDoc natively) |
| `docbook` | DocBook/SGML | `.html` | Converts via pypandoc |
| `mdx` | MDX | `.md` | Strips JSX components, outputs Markdown |

## Adding New Projects

Edit `scripts/config.yaml` to add new projects:

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

## Licensing

**This repository** (scripts, configurations): MIT License

**Documentation content**: Licenses vary by project - check each project's license before use.
