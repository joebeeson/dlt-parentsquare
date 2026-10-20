# dlt-parentsquare

[![CI](https://github.com/joebeeson/dlt-parentsquare/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/joebeeson/dlt-parentsquare/actions/workflows/ci.yml)
[![Prek](https://github.com/joebeeson/dlt-parentsquare/actions/workflows/prek.yml/badge.svg?branch=master)](https://github.com/joebeeson/dlt-parentsquare/actions/workflows/prek.yml)
[![CodeQL](https://github.com/joebeeson/dlt-parentsquare/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/joebeeson/dlt-parentsquare/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/joebeeson/dlt-parentsquare/badge)](https://securityscorecards.dev/viewer/?uri=github.com/joebeeson/dlt-parentsquare)
[![Latest release](https://img.shields.io/github/v/release/joebeeson/dlt-parentsquare?sort=semver)](https://github.com/joebeeson/dlt-parentsquare/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An unofficial, read-only [dlt](https://dlthub.com/) source for ParentSquare
posts and calendar events. The reusable HTTP client lives in the separate
[`parentsquare-client`](https://github.com/joebeeson/parentsquare-client)
repository so applications can use it without installing dlt.

ParentSquare does not publish a parent-facing API. This project reads the
authenticated parent web experience and therefore may stop working when
ParentSquare changes its site or account protections. It is not affiliated with
or endorsed by ParentSquare, Inc. Review ParentSquare's current terms and your
district's policies before using it.

Install the dlt adapter:

```python
pip install "dlt-parentsquare[dlt] @ git+https://github.com/joebeeson/dlt-parentsquare.git@v0.1.1"
```

Then run the source:

```python
import dlt
from dlt_parentsquare import parentsquare

pipeline = dlt.pipeline("parentsquare", destination="duckdb", dataset_name="school")
pipeline.run(parentsquare(username="parent@example.com", password="password"))
```

The source exposes `posts` and `calendar_events` resources. IDs are stable
within ParentSquare's account and are used as merge keys. A local DuckDB
example is in `examples/duckdb_pipeline.py`. Synthetic fixtures are used in
tests; real messages, cookies, credentials, and calendar URLs must never be
committed.

## Authentication

The shared client supports the normal sign-in flow and a six-digit MFA
challenge. An embedding application handles `MFARequired` by presenting the
masked destination and calling `submit_mfa_code`. The client does not persist
credentials or cookies; the embedding application owns that storage policy.

## Status

This is an early alpha. Reads only are implemented. Replies, acknowledgements,
forms, sign-ups, payments, attachments, and action extraction are deliberately
out of scope.

## Development

Run `uv run --extra dev --extra dlt pytest` for the test suite. Install `prek`
with `uvx prek install` to run the same checks as CI. Tagged releases create
GitHub release artifacts, and the publish workflow supports PyPI Trusted
Publishing plus manual TestPyPI verification.

See [docs/releasing.md](docs/releasing.md) for the one-time Trusted Publisher
configuration and tag workflow.
