# Autonomous Business Intelligence Agent

This repository is a learn-by-building project. We start with a trustworthy
analytics foundation and add capabilities in this order:

1. Clean and model a public retail dataset.
2. Load it into PostgreSQL and answer known SQL questions.
3. Give an LLM a safe SQL tool.
4. Add agent orchestration and Python analysis.
5. Add document retrieval (RAG), MCP, and scheduled reporting.

## Current milestone

Milestone 1 is complete when the raw UCI Online Retail workbook can be turned
into reproducible CSV files and loaded into PostgreSQL. The raw workbook is
never modified.

```bash
python scripts/prepare_data.py
```

The generated files are written to `data/curated/` (which is ignored by Git in
future setup). SQL definitions and learning notes live in `sql/` and
`docs/learning/`.

## Local development

PostgreSQL runs through Docker Compose, while Python dependencies run in a
project-local `.venv`:

```bash
source .venv/bin/activate
docker compose up -d
```

See `docs/learning/02-environments-and-git.md` for why both environments are
useful.

Docker is optional. When using the Homebrew PostgreSQL service instead, start
it with `brew services start postgresql@18`, create the database once with
`createdb retail_bi`, then run `python scripts/load_postgres.py`.

## First LLM SQL tool

With a local Ollama server running, ask a question with the guarded prototype:

```bash
source .venv/bin/activate
python -m bi_agent.cli --show-sql "What were the top five countries by revenue?"
```

This version accepts only read-only SQL and runs it in a time-limited
transaction. See `docs/learning/05-llm-sql-tool.md` before extending it.

## Dataset

The input is the UCI Online Retail dataset. It contains transaction line items
from 2010-12-01 through 2011-12-09. See the source documentation in the
learning note before changing any cleaning rule.

## Project principles

- Keep raw data immutable.
- Make cleaning assumptions explicit and testable.
- Prefer SQL with known answers before introducing an LLM.
- Treat generated answers as untrusted until checked against database results.
- Learn one layer at a time: data, database, tools, agents, retrieval, then
  automation.
