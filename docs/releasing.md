# Releasing

## One-time PyPI setup

Create the `dlt-parentsquare` project on PyPI and TestPyPI, then add a Trusted
Publisher for each project with the matching environment:

- owner: `joebeeson`
- repository: `dlt-parentsquare`
- workflow: `.github/workflows/publish.yml`
- PyPI environment: `pypi`
- TestPyPI environment: `testpypi`

The workflow uses GitHub's OIDC token, so no PyPI API token belongs in GitHub
secrets. Configure the `testpypi` GitHub environment for candidate runs and
the `pypi` environment with required approval and final-tag restrictions.

Publish `parentsquare-client` first. The dlt package declares it as a normal
PyPI dependency (`>=0.2.4,<0.3`), so the client version must be visible on the
target index before dlt's lockfile is refreshed and dlt is published.

For a rehearsal, publish the client candidate to TestPyPI, refresh and test
dlt against that index, then publish both final versions to PyPI in dependency
order.

## Release flow

1. Update the version in `pyproject.toml` and run `uv lock`.
2. Confirm the referenced `parentsquare-client` version is available.
3. Run `uv run --extra dev --extra dlt pytest`, `ruff`, and `prek` locally.
4. Commit the version change and push a tag such as `v0.1.2`.
5. The tag workflow runs tests, builds the wheel and source archive, and creates
   the GitHub release with generated notes.
6. For a release candidate such as `v0.1.2rc1`, manually dispatch the publish
   workflow with `repository=testpypi` and test it before creating the final
   version.
7. For a final tag, manually dispatch the publish workflow with
   `repository=pypi` after the release has passed its final review. The
   production environment should only allow final version tags. Releases
   created with `GITHUB_TOKEN` do not re-trigger another workflow through the
   release event.
