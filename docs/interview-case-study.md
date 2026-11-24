# rag-eval 面试项目说明

## 一句话定位

`rag-eval` 是一个与业务代码解耦的 RAG 与 Agent 评估层：使用统一契约接入不同
应用，计算可解释指标，通过数据集哈希、执行配置哈希和固定种子保证结果可比，
再以基线门禁和 CI 形成回归闭环。

## 三个项目的分工

| 项目 | 角色 | 面试展示重点 |
|---|---|---|
| `production-rag` | 传统 RAG 服务基线 | 文档摄入、检索、重排、生成、引用、C-MTEB |
| `kb-agent` | Agentic RAG 进阶场景 | 检索前路由、自纠错、重试、人工审核、LLM Judge |
| `rag-eval` | 共用评估基础设施 | 契约、指标、缓存、基线、门禁、趋势和 CI |

叙事主线不是三个互不相关的仓库，而是：

```text
两个不同架构的 RAG 应用
        ↓ 统一适配器与数据契约
检索 / 生成 / Agent 指标
        ↓ 基线、阈值和覆盖率
CI 回归门禁与可解释报告
```

## 可演示闭环

```text
rag-eval validate <dataset>
rag-eval run --config eval.yaml --save-baseline baseline.json
rag-eval run --config eval.yaml --baseline baseline.json --trend-csv trend.csv
rag-eval gate --config eval.yaml --baseline baseline.json --report report.json
```

演示时建议完成一次“人为制造指标下降，门禁失败，再恢复后通过”的完整过程。
这比只展示最终指标更能说明门禁确实生效。

## 关键设计

- 数据集按样本 ID 排序后计算内容哈希，忽略无关行序变化。
- 执行配置哈希排除路径、阈值和门禁开关，避免同一次评估因输出位置不同而失效。
- 检索指标覆盖 Recall、Precision、MRR、NDCG、跨度 NDCG、证据命中和全文档命中。
- 生成指标覆盖期望值命中、引用有效性、引用覆盖率和拒答正确性。
- Agent 指标覆盖重试率、改写来源、最终证据命中、外来证据、外来引用、人工审核、
  延迟分位数、Token 估算和成本估算。
- 确定性指标负责门禁；LLM Judge 负责辅助判断，解析失败或调用失败不会被伪装成
  高分。

## 验收标准

- 单元测试全部通过，整体覆盖率不低于 82%。
- `wheel`、`sdist` 可构建，`twine check` 通过。
- `production-rag` 的本地 smoke 或 C-MTEB Gate 可运行。
- `kb-agent` 的 retrieval 和 L3 Agent Gate 可运行。
- 至少保留一份基线、一份报告和一条趋势记录。
- 工作区干净，演示入口、数据集版本和配置可复现。

## 已知边界

- 当前是库和 CLI，不提供 Web 界面、任务队列或分布式执行。
- 单样本超时使用守护线程记录，无法强制终止已经阻塞的第三方调用。
- LLM Judge 只适合辅助分析，不适合作为唯一门禁依据。
- 本项目不追求更多指标数量，而是优先保证口径一致、结果可比和回归可执行。

## 八分钟演示顺序

1. 说明三个项目的分工和统一评估目标。
2. 展示数据集契约和一次 `validate`。
3. 展示 `run --baseline` 生成的 JSON/Markdown 报告。
4. 展示人为回归后 `gate` 失败。
5. 展示恢复指标后门禁通过，并追加趋势 CSV。
6. 展示 CI 中的测试、覆盖率、构建和业务项目 smoke。
7. 最后说明 Judge、超时和可扩展性方面的边界。
