# rag-eval

Standalone evaluation platform for retrieval, generation, and Agent workflows.
It provides typed contracts, standard retrieval metrics, runner/cache/report
infrastructure, regression gates, and optional HTTP/LLM judge interfaces.

The core package does not import business projects and does not start Docker,
Elasticsearch, MySQL, Redis, or Milvus.

## Install

From a GitHub Release:

```powershell
python -m pip install "rag-eval @ https://github.com/1940633231/rag-eval/releases/download/v0.1.0/rag_eval-0.1.0-py3-none-any.whl"
```

After PyPI publication:

```powershell
python -m pip install "rag-eval>=0.1.0,<0.2.0"
```

## CLI

```text
rag-eval validate <dataset-dir>
rag-eval run --config eval.yaml
rag-eval compare current.json baseline.json
rag-eval gate --config eval.yaml --baseline baseline.json --report report.json
rag-eval trend --report report.json --csv trend.csv
```

`rag-eval run` also supports:

- `--baseline PATH`: run and gate in one command
- `--save-baseline PATH`: save a new baseline
- `--trend-csv PATH`: append metric history
- `--json`: machine-readable output

## Adapters

Adapters are loaded with `module:object` and may implement:

```python
class Adapter:
    name: str
    capabilities: set[str]

    def validate(self) -> list[str]: ...
    def run(self, sample, context): ...
    def warmup(self, context) -> None: ...  # optional
```

`warmup` runs once before the first cache miss and outside the per-sample
timeout. This keeps model or index initialization from being reported as a
sample timeout.

## Development

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python -m build
python -m twine check dist/*
```

See `CHANGELOG.md` for release history.
