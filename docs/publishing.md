# 发布

## GitHub Release

`publish` 工作流会构建 sdist 和 wheel、校验产物，并将两个文件附加到已发布的
GitHub Release。

当前版本：

- `v0.1.0`
- `rag_eval-0.1.0-py3-none-any.whl`
- `rag_eval-0.1.0.tar.gz`

## PyPI 可信发布

在完成可信发布配置前，PyPI 发布任务保持禁用。

1. 在 PyPI 创建或认领 `rag-eval` 项目。
2. 添加可信发布者：
   - 所有者：`1940633231`
   - 仓库：`rag-eval`
   - 工作流：`publish.yml`
   - 环境：`pypi`
3. 在 GitHub 仓库设置中创建 `pypi` 环境。
4. 添加仓库变量 `PYPI_TRUSTED_PUBLISHING_READY=true`。
5. 发布新的 tag/Release，或手动运行 `publish` 工作流。

该工作流使用 OpenID Connect，不需要长期保存的 PyPI token。

## 业务仓库依赖

PyPI 发布后，将引导用的 GitHub Release wheel 替换为：

```text
rag-eval>=0.1.0,<0.2.0
```

`production-rag` 和 `kb-agent` 的 `requirements-eval.txt` 文件中已经保留了
这个版本范围。
