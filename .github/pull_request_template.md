## Summary

<!-- What does this PR change? -->

## Checklist

- [ ] `./scripts/ci.sh` and `./scripts/analyse.sh` pass locally (or Jenkins PR build is green)
- [ ] CLI smoke tests pass: `hello-world greet` and `hello-world stats "demo"`
- [ ] No secrets or credentials in the diff
- [ ] Version comes from git tags / setuptools-scm (no manual version bumps in `pyproject.toml`)
