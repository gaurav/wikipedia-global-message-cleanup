# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool to clean up Wikipedia GlobalMessage delivery lists by checking when each listed user last made a contribution. Reads MediaWiki-formatted input files, queries the Wikimedia API, and outputs a TSV with each user's last edit date and an activity classification.

## Commands

All commands use `uv` to manage the Python 3.11 environment:

```bash
# Run the main script
uv run check-last-contribution.py <input_file> -o output.tsv

# Run tests
uv run python -m pytest test_modules.py

# Run a single test
uv run python -m pytest test_modules.py::TestClassName::test_method_name

# Lint
uv run ruff check .

# Lint and auto-fix
uv run ruff check . --fix
```

## Architecture

The CLI entry point is `check-last-contribution.py`, which delegates to `lib/processor.py`. The `lib/` package provides:

- **`models.py`** — `UsernameWithSite` and `ContributionResult` dataclasses
- **`parsers.py`** — `MediaWikiParser` extracts `{{target | user = X | site = Y}}` patterns from input lines
- **`api_client.py`** — `WikimediaAPIClient` queries `/w/api.php?action=query&list=usercontribs` with exponential backoff (5 retries, 1.5s sleep between lines)
- **`analyzer.py`** — `ContributionAnalyzer` classifies users as `active` / `inactive` / `delete` / `none` based on year thresholds
- **`output_writer.py`** — `TSVWriter` writes tab-separated output with headers
- **`processor.py`** — `UserProcessor` orchestrates the pipeline; deduplicates API calls across files; expands each user to additional sites specified via `-s`

The test suite is `test_modules.py` using Python's `unittest` framework (12 tests).
