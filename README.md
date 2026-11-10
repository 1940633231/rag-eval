# rag-eval

面向检索、生成和 Agent 工作流的独立评估平台。项目提供类型化契约、标准检索
指标、运行器/缓存/报告基础设施、回归门禁，以及可选的 HTTP/LLM 评审接口。

核心包不会导入业务项目，也不会启动 Docker、Elasticsearch、MySQL、Redis
或 Milvus。

## 安装

从 GitHub Release 安装：

```powershell
python -m pip install "rag-eval @ https://github.com/1940633231/rag-eval/releases/download/v0.1.0/rag_eval-0.1.0-py3-none-any.whl"
```

PyPI 发布后：

```powershell
python -m pip install "rag-eval>=0.1.0,<0.2.0"
```

## 命令行

```text
rag-eval validate <dataset-dir>
rag-eval run --config eval.yaml
rag-eval compare current.json baseline.json
rag-eval gate --config eval.yaml --baseline baseline.json --report report.json
rag-eval trend --report report.json --csv trend.csv
```

`rag-eval run` 还支持以下参数：

- `--baseline PATH`：在一条命令中完成运行和门禁检查
- `--save-baseline PATH`：保存新的基线
- `--trend-csv PATH`：追加指标历史
- `--json`：输出机器可读结果

## 适配器

适配器通过 `module:object` 加载，可以实现以下接口：

```python
class Adapter:
    name: str
    capabilities: set[str]

    def validate(self) -> list[str]: ...
    def run(self, sample, context): ...
    def warmup(self, context) -> None: ...  # 可选
```

`warmup` 会在第一次缓存未命中前执行一次，并且不受单样本超时限制。这样模型或
索引初始化就不会被误报为样本超时。

## 开发

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python -m build
python -m twine check dist/*
```

发布历史请参阅 `CHANGELOG.md`。
