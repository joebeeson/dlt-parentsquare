# Configuration

`dlt-parentsquare` follows dlt's normal configuration providers. ParentSquare
credentials are secrets; connection and pipeline options are configuration.
Values passed explicitly to `parentsquare(...)` always take precedence over
injected values.

## Local `.dlt` files

For a local pipeline, copy the examples into the pipeline workspace:

```text
.dlt/secrets.toml
.dlt/config.toml
```

Put credentials in `.dlt/secrets.toml`:

```toml
[sources.parentsquare]
username = "parent@example.com"
password = "replace-me"
```

Put nonsecret options in `.dlt/config.toml`:

```toml
[sources.parentsquare]
base_url = "https://www.parentsquare.com"
```

Never commit `.dlt/secrets.toml`. The repository includes
`.dlt/secrets.toml.example` as a safe template.

## Environment variables

The equivalent environment variables use dlt's double-underscore naming:

```text
SOURCES__PARENTSQUARE__USERNAME=parent@example.com
SOURCES__PARENTSQUARE__PASSWORD=replace-me
SOURCES__PARENTSQUARE__BASE_URL=https://www.parentsquare.com
```

`SOURCES__PARENTSQUARE__MFA_CODE` may be supplied for a run that needs a
six-digit MFA code. Treat it as a short-lived secret and do not put it in a
committed config file. The underlying client raises `MFARequired` when a code
is needed and none is available.

Environment variables and supported dlt vault providers take precedence over
local TOML files. This keeps the same source code usable in a local DuckDB
pipeline, CI, and a managed runner without moving credentials into Python.

## Explicit Python values

Explicit values remain useful for tests or a caller that already owns secret
storage:

```python
pipeline.run(
    parentsquare(
        username="parent@example.com",
        password=get_password_from_your_secret_store(),
    )
)
```

The source uses the shared `parentsquare-client` for HTTP, login, MFA, session
renewal, pagination, and response parsing. `dlt-parentsquare` only adapts the
client's records to dlt resources; it does not create a second HTTP client.
