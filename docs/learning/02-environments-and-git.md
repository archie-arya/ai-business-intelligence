# Lesson 2: Environments, Docker, and Git

## Why we need both Docker and a Python environment

They isolate different layers:

| Layer | Tool | What it isolates |
|---|---|---|
| Database service | Docker Compose | PostgreSQL, its version, configuration, and data volume |
| Application dependencies | Python `.venv` | pandas, database drivers, test tools, and our application code |
| Source history | Git | Changes to code, SQL, documentation, and configuration |

Docker does not replace a Python virtual environment. A PostgreSQL container
can run independently of Python, while our Python scripts still need a
repeatable package environment.

## Local PostgreSQL setup

After Docker Desktop is running:

```bash
docker compose up -d
docker compose ps
```

The database will be available at `localhost:5432` with the defaults in
`compose.yaml`. These credentials are for local development only.

Stop the service without deleting its data:

```bash
docker compose down
```

Remove the database volume only when intentionally starting over:

```bash
docker compose down -v
```

## Git basics

Git tracks the source of the project, not generated data or secrets. The
repository ignores `data/curated/`, `.venv/`, and local environment files.

Useful commands:

```bash
git status
git log --oneline
git diff
```

## References

- [Docker Compose getting started](https://docs.docker.com/compose/gettingstarted/)
- [Python `venv` documentation](https://docs.python.org/3/library/venv.html)
- [Git documentation](https://git-scm.com/doc)
