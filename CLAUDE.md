# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool to clean up Wikipedia GlobalMessage delivery lists by checking when each listed user last made a contribution. Reads MediaWiki-formatted input files, queries the Wikimedia API, and outputs a TSV with each user's last edit date and an activity classification.

## Commands

All commands use `uv` to manage the Python 3.11 environment:

```bash
# Run the main script
uv run check-last-contribution <input_file> -o output.tsv

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_contribution_analyzer.py::TestContributionAnalyzer::test_active_user

# Lint
uv run ruff check .

# Lint and auto-fix
uv run ruff check . --fix
```

## Architecture

Source code lives under `src/` (standard src layout) in a single package `src/wikipedia_global_message_cleanup/`. The CLI entry point is `src/wikipedia_global_message_cleanup/cli.py`, registered as the `check-last-contribution` script via `[project.scripts]`. It delegates to `processor.py`. The package provides:

- **`cli.py`** — CLI entry point (`main` function)
- **`models.py`** — `UsernameWithSite` dataclass
- **`parsers.py`** — `MediaWikiParser` extracts `{{target | user = X | site = Y}}` patterns from input lines
- **`api_client.py`** — `WikimediaAPIClient` queries `/w/api.php?action=query&list=usercontribs` with exponential backoff (5 retries, sleeps between API calls to respect rate limits)
- **`analyzer.py`** — `ContributionAnalyzer` classifies users as `active` / `inactive` / `delete` / `none` based on year thresholds
- **`output_writer.py`** — `TSVWriter` writes tab-separated output with headers
- **`processor.py`** — `UserProcessor` orchestrates the pipeline; deduplicates API calls across files; expands each user to additional sites specified via `-s`

Tests live in `tests/` and use pytest.
