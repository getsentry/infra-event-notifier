# infra-event-notifier
Generic Python package used by infra tools to send notifications to Slack and Datadog events when changes are made.

## Releasing

Releases are cut with [Craft](https://github.com/getsentry/craft), configured in
[`.craft.yml`](.craft.yml). Nothing is released by merging to `main` — a release
is always started explicitly.

### 1. Start the release

Run the [Release workflow](../../actions/workflows/release.yml) from the Actions
tab, or:

```bash
gh workflow run release.yml -f version=1.2.3
```

`version` accepts any of:

| Value | Effect |
|---|---|
| `1.2.3` | Release exactly this version |
| `major` / `minor` / `patch` | Bump the current version accordingly |
| `auto` | Craft analyses commits since the last release to pick the bump |

The input is technically optional, but this repo does not set
`versioning.policy` in `.craft.yml` — which is what Craft falls back to when no
version is given — so pass a value explicitly.

Set `force=true` to release despite open issues labelled `release-blocker` —
otherwise the workflow cancels itself when any exist.

### 2. Craft prepares the release

Craft opens a release branch named `release/<version>` containing:

- the version written into `pyproject.toml` by
  [`scripts/bump-version.sh`](scripts/bump-version.sh)
- a new `CHANGELOG.md` section, generated from commit and PR titles because
  `changelogPolicy` is `auto`

Do not edit either by hand — both are generated, and edits will be overwritten.
The changelog is built from commit subjects, so those become the release notes.

### 3. The publish request

Craft opens an issue in [getsentry/publish](https://github.com/getsentry/publish)
titled `publish: getsentry/infra-event-notifier@<version>`, listing each target
as a checkbox.

**Releases for this repo are auto-approved, so there is nothing to label** —
publishing starts on its own. The issue is still worth knowing about: it is where
per-target progress shows up, so it is the place to look when a release does not
appear on an index. Checked targets are skipped, so a partially-published release
can be retried by unchecking just the target that failed.

### 4. Craft publishes

Each target in `.craft.yml` runs in order:

| Target | Result |
|---|---|
| `github` | Git tag plus a GitHub release, with notes read from `CHANGELOG.md` and the wheel/sdist from [`build.yml`](.github/workflows/build.yml) attached |
| `pypi` | [Public PyPI](https://pypi.org/project/sentry-infra-event-notifier/) |
| `sentry-pypi` | Internal index, `pypi.devinfra.sentry.io` |

Consumers such as `getsentry/ops` and TACOS install from the internal index, so
that is the one to check when confirming a release landed:

```bash
pip index versions sentry-infra-event-notifier \
  --index-url https://pypi.devinfra.sentry.io/simple
```

## Development

```bash
make test        # pytest
make lint        # black + flake8
make typecheck   # mypy
```
