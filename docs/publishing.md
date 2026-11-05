# Publishing

## GitHub Release

The `publish` workflow builds the sdist and wheel, validates them, and attaches
both files to the published GitHub Release.

Current release:

- `v0.1.0`
- `rag_eval-0.1.0-py3-none-any.whl`
- `rag_eval-0.1.0.tar.gz`

## PyPI Trusted Publishing

The PyPI job remains disabled until trusted publishing is configured.

1. Create or claim the `rag-eval` project on PyPI.
2. Add a trusted publisher:
   - owner: `1940633231`
   - repository: `rag-eval`
   - workflow: `publish.yml`
   - environment: `pypi`
3. Create the `pypi` environment in GitHub repository settings.
4. Add repository variable `PYPI_TRUSTED_PUBLISHING_READY=true`.
5. Publish a new tag/release, or manually run the `publish` workflow.

The workflow uses OpenID Connect and does not require a long-lived PyPI token.

## Business repository dependency

After PyPI publication, replace the bootstrap GitHub Release wheel with:

```text
rag-eval>=0.1.0,<0.2.0
```

Both `production-rag` and `kb-agent` already keep this range in their
`requirements-eval.txt` files.
