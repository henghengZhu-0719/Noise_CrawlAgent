# 企业级改造 TODO

> 目标：将当前批处理脚本升级为可观测、可扩展、可维护的生产级系统。

---

## P0 — 基础工程化（必做，面试必问）

### 1. 测试体系
- [ ] 为 `filter_node` / `extract_node` 编写单元测试，mock LLM 响应
- [ ] 为 `CrawlHtml` 编写集成测试，使用 `responses` 库 mock HTTP
- [ ] 为 `crud.py` 编写数据库测试，使用 SQLite in-memory
- [ ] 配置 `pytest` + `pytest-cov`，覆盖率门槛 ≥ 70%

### 2. CI/CD 流水线
- [ ] 添加 `.github/workflows/ci.yml`：lint → test → build Docker image
- [ ] 配置 `ruff` 做代码风格检查（替代 flake8）
- [ ] 配置 `mypy` 做类型检查（`pyproject.toml` 中启用 strict 模式）
- [ ] PR 合并前必须通过 CI

### 3. 结构化日志
- [ ] 引入 `structlog`，替换所有 `print` 和裸 `logging`
- [ ] 每条日志携带 `trace_id`（每次 pipeline 运行生成一个 UUID）
- [ ] 日志输出 JSON 格式，便于 ELK / CloudWatch 接入

### 4. 配置管理
- [ ] 用 `pydantic-settings` 替换手动读取 `os.environ`
- [ ] 区分 `dev` / `staging` / `prod` 三套配置
- [ ] 敏感字段（API Key、DB 密码）标注 `SecretStr`，防止日志泄露

---

## P1 — API 服务化（核心亮点）

> 参考 `agent_service/改造方案_API服务化.md`

### 5. FastAPI 服务层
- [ ] 创建 `api_service/` 目录，实现以下端点：
  - `POST /tasks` — 提交 URL，返回 `task_id`
  - `GET /tasks/{task_id}` — 查询任务状态和结果
  - `GET /tasks` — 分页列表，支持按状态过滤
  - `DELETE /tasks/{task_id}` — 取消排队中的任务
- [ ] 用 Pydantic v2 定义请求/响应 schema
- [ ] 添加 OpenAPI 文档（FastAPI 自动生成，补充描述和示例）

### 6. 异步任务队列
- [ ] 集成 Celery + Redis（或 RQ）作为任务队列
- [ ] Pipeline 每个节点执行结果写回 Redis，支持断点续跑
- [ ] 任务超时、重试策略（最多 3 次，指数退避）

### 7. WebSocket 实时进度
- [ ] `GET /tasks/{task_id}/stream` — SSE 或 WebSocket 推送节点进度
- [ ] 前端可订阅：`crawl → filter → extract → search → download` 各阶段状态

---

## P2 — 可观测性（生产必备）

### 8. 指标监控
- [ ] 集成 `prometheus-client`，暴露 `/metrics` 端点
- [ ] 关键指标：任务吞吐量、各节点耗时 P50/P95、LLM 调用成功率、PDF 下载成功率
- [ ] 提供 `docker-compose` 中的 Prometheus + Grafana 配置示例

### 9. 分布式追踪
- [ ] 集成 OpenTelemetry，trace 覆盖 HTTP 请求 → LangGraph 节点 → DB 操作
- [ ] 每次 LLM 调用记录 token 用量和延迟

### 10. 健康检查
- [ ] `GET /health` — 返回服务状态
- [ ] `GET /health/ready` — 检查 DB 连接、Redis 连接、LLM API 可达性
- [ ] Docker Compose `healthcheck` 配置

---

## P3 — 数据与安全

### 11. 数据库迁移
- [ ] 引入 `Alembic`，管理 schema 变更历史
- [ ] 现有表结构生成初始 migration 文件
- [ ] CI 中加入 `alembic upgrade head` 检查

### 12. 错误处理与幂等性
- [ ] Pipeline 节点失败时写入 `error_message` 字段，不丢失中间结果
- [ ] 同一 URL 重复提交时返回已有 `task_id`（幂等提交）
- [ ] 数据库操作统一使用事务，避免部分写入

### 13. 安全加固
- [ ] API 添加 API Key 认证（`X-API-Key` header）
- [ ] 请求体大小限制，防止超大 payload
- [ ] 依赖扫描：`pip-audit` 加入 CI，检查已知 CVE

---

## P4 — 开发体验

### 14. 本地开发环境
- [ ] 提供 `docker-compose.dev.yml`，包含 MySQL + Redis + 热重载
- [ ] 编写 `Makefile`：`make dev` / `make test` / `make lint` / `make build`
- [ ] `.env.example` 列出所有必填变量（不含真实值）

### 15. 文档
- [ ] `README.md` 补充：架构图、快速启动、API 使用示例
- [ ] 每个服务目录下补充 `README.md` 说明职责和本地运行方式
- [ ] CHANGELOG.md 记录版本变更

---

## 优先级说明

| 优先级 | 内容 | 面试价值 |
|--------|------|----------|
| P0 | 测试 + CI/CD + 日志 + 配置管理 | 基础工程素养，必问 |
| P1 | FastAPI + Celery + WebSocket | 系统设计能力，加分项 |
| P2 | Prometheus + OpenTelemetry | 生产经验，高级岗必问 |
| P3 | Alembic + 幂等 + 安全 | 细节把控，体现严谨性 |
| P4 | 开发体验 + 文档 | 团队协作意识 |

**建议顺序：先做完 P0，再做 P1 的 FastAPI 部分，这两块在简历上最直接体现"企业级"。**
