# Technical Documentation Corpus

Scripts to extract documentation from open source projects for RAG evaluation.

## Purpose

Technical documentation is a prime BiteSizeRAG use case. These corpora test:
- **Retrieval**: Hierarchical navigation, API reference lookup, conceptual vs. reference content
- **Document processing**: Markdown with code blocks, RST with directives, interlinked pages
- **Query types**: "How do I use X?", "What's the difference between Y and Z?", troubleshooting

## Usage

```bash
cd scripts/evaluation/technical_docs
uv sync

# List available projects
uv run python extract_docs.py --list

# Extract a project
uv run python extract_docs.py rust-book --corpus rust_docs

# Extract with document limit
uv run python extract_docs.py django --corpus django_docs --max-docs 200

# Extract to custom directory
uv run python extract_docs.py kubernetes --data-dir /path/to/output
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

## Output Structure

```
<corpus_name>/
    corpus.yaml               # Evaluation configuration
    metadata.json             # Corpus metadata
    docs/                     # Downloaded documents (gitignored)
        document_name.md      # Markdown (identity, mdx converters)
        another_doc.html      # HTML (rst, docbook converters)
        some_file.adoc        # AsciiDoc (asciidoc converter)
```

All output formats are directly ingestible by Docling (the document processor).

## Metadata Format

```json
{
  "corpus": "rust_docs",
  "project": "rust-book",
  "source_url": "https://github.com/rust-lang/book.git",
  "version": "main",
  "license": "MIT/Apache-2.0",
  "converter": "identity",
  "extraction_date": "2025-01-15T10:30:00+00:00",
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

Edit `config.yaml` to add new projects:

```yaml
projects:
  new-project:
    source_type: git
    repo_url: https://github.com/org/repo.git
    sparse_checkout:
      - docs
    file_pattern: "docs/**/*.md"
    converter: identity  # or rst, asciidoc, docbook, mdx
    metadata:
      license: "MIT"
      version_tag: main  # optional: specific tag/branch
```

## Converters

| Converter | Input | Output | Description |
|-----------|-------|--------|-------------|
| `identity` | Markdown | `.md` | Passthrough (Docling supports MD natively) |
| `rst` | reStructuredText | `.html` | Converts via pypandoc (Docling lacks RST support) |
| `asciidoc` | AsciiDoc | `.adoc` | Passthrough (Docling supports AsciiDoc natively) |
| `docbook` | DocBook/SGML | `.html` | Converts via pypandoc (Docling lacks DocBook support) |
| `mdx` | MDX | `.md` | Strips JSX components, outputs Markdown |

## Development

```bash
make install-dev
make all  # format, lint, security, typecheck
```

## License

Projects have varying licenses documented in their metadata. Check each project's license before use.
