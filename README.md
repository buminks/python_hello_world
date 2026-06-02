# hello-world

Reference Python package demonstrating CI/CD with **GitHub** (PRs), **Jenkins**, **Artifactory**, and **JFrog Xray**.

Versioning uses [setuptools-scm](https://github.com/pypa/setuptools-scm) from git tags (`v1.0.0` → `1.0.0`). CI is **Jenkins-only** (no GitHub Actions workflows).

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
hello-world
python -m build
```

Run the full local pipeline (same steps as Jenkins, without publish):

```bash
chmod +x scripts/ci.sh
./scripts/ci.sh
```

With JFrog CLI v2 and credentials:

```bash
export JF_URL="https://your-instance.jfrog.io"
export JF_ACCESS_TOKEN="***"
jf scan dist/ --fail          # after ./scripts/ci.sh build, or:
CI_PUBLISH=true BUILD_NUMBER=1 ./scripts/ci.sh
```

## Versioning and releases

| Git state | Example version |
|-----------|-----------------|
| Tag `v1.0.0` on commit | `1.0.0` |
| Commits after last tag | `1.0.1.dev3+g1a2b3c4` (illustrative) |
| PR / feature branch | dev version from `git describe` |

**Release workflow**

1. Merge changes to `main`.
2. Create and push an annotated tag:

   ```bash
   git tag -a v1.0.0 -m "Release 1.0.0"
   git push origin v1.0.0
   ```

3. Jenkins builds the tag, runs tests, `jf scan`, and publishes wheels to Artifactory.

**Troubleshooting setuptools-scm**

- Jenkins checkout must use **full history** (`depth: 0`); shallow clones break versioning.
- Ensure tags are fetched: `git fetch --tags`.
- Tag format must match `v*` (e.g. `v1.0.0`), configured in `pyproject.toml`.

## Jenkins setup

### Multibranch pipeline (GitHub)

1. **New Item** → **Multibranch Pipeline**.
2. **Branch Sources** → GitHub → select repository.
3. Enable **Discover pull requests** (from origin).
4. **Behaviors** → **Discover tags** with filter `v*` (optional: tag build strategy).
5. **Build Configuration** → Script Path: `Jenkinsfile`.

### Credentials (JFrog CLI v2)

Create Jenkins credentials (IDs must match `Jenkinsfile` or update the file):

| Credential ID | Type | Purpose |
|---------------|------|---------|
| `jf-url` | Secret text | Platform URL (`JF_URL`) |
| `jf-access-token` | Secret text | Access token (`JF_ACCESS_TOKEN`) |

Optional job environment variable:

| Variable | Default | Purpose |
|----------|---------|---------|
| `JF_RT_REPO` | `pypi-local` | Artifactory repository key for uploads |

Agents need **Python 3.10+**, **git**, and **`jf`** (JFrog CLI v2) on `PATH` for scan/publish stages.

### Pipeline behavior

| Build type | Lint / test / build | `jf scan` | `jf rt upload` |
|------------|---------------------|-----------|----------------|
| Pull request | yes | yes (if `jf` present) | no |
| Feature branch | yes | yes | no |
| `main` | yes | yes | yes |
| Tag `v*` | yes | yes | yes |

Publish runs when `IS_RELEASE` is true (`main` or tag) and the build is **not** a change request (`CHANGE_ID` unset).

### GitHub PR checks

1. Configure the multibranch job webhook / GitHub App (push + `pull_request`).
2. In GitHub **branch protection** for `main`, require the Jenkins check (e.g. `Jenkins / … / PR-123`) before merge.
3. Opening or updating a PR triggers Jenkins; Xray failures fail the PR build.

## Artifactory layout

Upload target (configurable via `JF_RT_REPO`):

```text
{pypi-local}/hello-world/{version}/
  hello_world-{version}-py3-none-any.whl
  hello_world-{version}.tar.gz
```

Build info: `hello-world` / `${BUILD_NUMBER}` via `jf rt build-publish`.

## Project layout

```text
├── Jenkinsfile
├── pyproject.toml
├── src/hello_world/
├── tests/
└── scripts/ci.sh
```

## License

MIT
