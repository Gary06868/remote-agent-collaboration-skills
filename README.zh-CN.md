# Remote Agent Collaboration Lite

如果你和几个朋友、合伙人或 AI Agent 一起 vibe coding，一个项目很快会变成散乱聊天记录、重复修改和不清楚的任务归属。Remote Agent Collaboration Lite 用两个 Markdown Skill：Lead 和 Member，再加几个简单项目文件，把协作规则、软锁、日志、可选任务和可选模块边界固定下来。不需要服务器、不需要数据库、不需要 CLI、不需要 hooks。

同时安装两个 Skill：

- `team-lead-collaboration`
- `team-member-collaboration`

开一个 Lead thread：

```text
$team-lead-collaboration Set up lightweight collaboration for this project.
```

开 Member thread：

```text
$team-member-collaboration Work on my assigned scope and update the shared collaboration log.
```

团队通过 Markdown 文件协作：

- `AGENTS.md`：共享项目规则。
- `COLLAB_LOG.md`：当前工作锁、更新、阻塞和决策。
- `TEAM_TASKS.md`：当你启用任务分配模式时使用。
- `MODULE_OWNERSHIP.md`：当你启用模块 ownership 时使用。

## 这是什么

Remote Agent Collaboration Lite 是一个纯 Markdown 协作流程，适合一个项目 Lead 和多个贡献者一起工作。贡献者可以是真人、Codex thread、Claude thread、其他 AI Agent，或者它们的组合。

它不是权限系统。它让 Agent 明确读取同一组项目文件，编辑前声明工作范围，避免冲突，并在完成后留下简短交接记录。

## 给谁用

适合这些情况：

- 小团队或小公司在同一个仓库里开发。
- 多个 AI thread 可能修改相关文件。
- 你希望有一个 Lead Agent 负责协调，但不想引入基础设施。
- 你需要轻量日志和软锁，而不是完整项目管理系统。
- 你希望新成员 5 分钟内理解协作规则。

## 解决什么问题

- 分散聊天记录变成共享 Markdown 上下文。
- 通过 Active Work Locks 减少重复修改。
- 启用可选模块边界时，owner 和路径范围更清楚。
- 需要时可以启用任务模式，但默认仍保持轻量。
- Member 遇到冲突时知道该停止询问，而不是继续猜。

## 快速开始

1. 在你的 AI coding 环境中安装两个 Skill。
2. 启动 Lead thread：

   ```text
   $team-lead-collaboration Initialize collaboration for this existing project.
   ```

3. Lead 判断项目是空项目还是已有项目。
4. Lead 创建或更新 `AGENTS.md` 和 `COLLAB_LOG.md`。
5. Lead 询问是否启用 Task Assignment Mode。
6. Lead 询问是否启用 Module Ownership Mode。
7. 启动一个或多个 Member thread：

   ```text
   $team-member-collaboration Read the collaboration files and work on the scope I give you.
   ```

8. 每个 Member 编辑前检查 Active Work Locks，无冲突时添加 lock，完成后移除 lock 并写简短更新。

## Lead Thread 工作流

Lead 适合项目 owner、项目负责人、协作组织者，或负责协调多个 worker 的 AI thread。

Lead 应该：

- 写入前先读取现有项目结构。
- 创建或维护 `AGENTS.md`。
- 创建或维护 `COLLAB_LOG.md`。
- 说明软锁只是协作记录，不是安全控制。
- 主动询问："Do you want to enable Task Assignment Mode?"
- 如果启用，创建或更新 `TEAM_TASKS.md`。
- 主动询问："Do you want to define module boundaries and owners now?"
- 如果启用，创建或更新 `MODULE_OWNERSHIP.md`。
- 在任务模式有用时分配工作。
- 按需 review member 输出。
- 处理冲突和阻塞。
- 总结或压缩过长的协作日志。

Lead 不应该强制每个项目进入正式任务表或模块 ownership。

## Member Thread 工作流

Member 适合普通贡献者、执行者、模块开发者、AI worker 或另一个 AI coding thread。

每次开始时，Member 应该：

1. 读取 `AGENTS.md`。
2. 读取 `COLLAB_LOG.md`。
3. 检查 `# Active Work Locks`。
4. 如果存在 `TEAM_TASKS.md`，读取自己的任务。
5. 如果存在 `MODULE_OWNERSHIP.md`，读取相关模块边界。
6. 如果可选文件不存在，按 Casual Coordination Mode 工作，不报错。
7. 如果当前 actor 名称或子角色不清楚，询问用户。

工作中，Member 应该：

- 较大读写任务开始前，在无冲突时添加 soft lock。
- 如果已有 lock 和当前范围重叠，停止并询问。
- 只修改与当前任务或用户请求相关的文件。
- 完成后写简短更新。
- 如果启用了任务模式，更新自己的任务状态。
- 完成后移除自己的 lock。

## 空项目设置

对于空目录或基本空目录，Lead 可以创建：

- `AGENTS.md`
- `COLLAB_LOG.md`

Lead 也可以建议轻量目录结构，但不要在用户没有要求时生成复杂架构。

Lead 应询问或推断：

- 项目名称。
- 项目目标。
- 技术栈。
- 是否需要任务分配模式。
- 是否需要模块 ownership。
- 是否需要建议目录结构。

## 已有项目设置

对于已有项目，Lead 必须先检查当前结构，再添加协作文件。至少检查：

- 现有 `README.md`。
- 现有 `AGENTS.md`，如果存在。
- 技术栈文件，例如 `package.json`、`pyproject.toml`、`Cargo.toml` 或 `go.mod`。
- `src`、`app`、`lib`、`docs`、`tests`、`frontend`、`backend` 等目录。
- 现有贡献指南或项目规则。
- 当前 Git 状态。

Lead 应尊重现有架构。不要为了这个 workflow 强行重排文件夹。

如果项目已有规则或日志，谨慎合并。如果现有项目规则和 Lite 默认规则冲突，停止并询问：

```text
There is a conflict between existing project rules and the default collaboration workflow. Do you want to prioritize the existing project rules or adopt the recommended Lite rules?
```

默认建议：已有项目规则优先。

## Casual Coordination Mode

Casual Coordination Mode 是默认模式。

它只使用：

- `AGENTS.md`
- `COLLAB_LOG.md`

Member 根据用户当前指令工作，编辑前检查 Active Work Locks，完成后写简短更新。不强制任务表或 review 队列。

## 可选 Task Assignment Mode

只有用户希望正式追踪任务时才启用。

启用后，Lead 创建或更新 `TEAM_TASKS.md`，并使用简单状态：

- `BACKLOG`
- `ASSIGNED`
- `IN_PROGRESS`
- `BLOCKED`
- `READY_FOR_REVIEW`
- `CHANGES_REQUESTED`
- `DONE`

任务条目保持实用即可：owner、范围、目标、验收说明、阻塞、最近更新。

## 可选 Module Ownership Mode

只有路径或模块边界重要时才启用。

启用后，Lead 创建或更新 `MODULE_OWNERSHIP.md`，记录：

- 模块名称。
- owner。
- 允许路径。
- 避免或受保护路径。
- 接口说明。
- 风险。
- 跨模块备注。

如果用户暂时不需要 module ownership，不创建该文件。

## Active Work Locks

`COLLAB_LOG.md` 必须把 `# Active Work Locks` 放在靠前位置。

lock 是软协作记录：

```markdown
- Actor:
  Agent:
  Role:
  Status: reading | writing | paused
  Scope:
  Task:
  Started:
  Last Updated:
  Expected Finish:
  Notes:
```

任何较大的读写任务开始前，Agent 都应该检查是否有重叠 lock。

如果没有冲突，添加自己的 lock，写明 actor、role、scope 和预计工作。如果有冲突，不要编辑。告诉用户哪个 actor 正在处理重叠范围，并询问下一步。

如果 lock 看起来过期，不要直接删除。先标记 stale，再询问用户。建议 stale 时间：2 小时。

## Markdown 文件

| 文件 | 必需 | 用途 |
| --- | --- | --- |
| `AGENTS.md` | 是 | 共享项目规则、启动检查、Git 规则、日志规则和冲突处理。 |
| `COLLAB_LOG.md` | 是 | 当前锁、当前摘要、阻塞、决策、更新、交接和历史。 |
| `TEAM_TASKS.md` | 可选 | 启用任务分配模式时使用的轻量任务表。 |
| `MODULE_OWNERSHIP.md` | 可选 | 启用模块 ownership 时记录 owner 和路径边界。 |

模板在 [`templates/`](templates/)。

## Tiny Team 示例

见 [`examples/tiny-team-project`](examples/tiny-team-project/)。

示例展示：

- Lead 初始化 `AGENTS.md` 和 `COLLAB_LOG.md`。
- 用户启用 Task Assignment Mode。
- 用户暂不启用 Module Ownership Mode。
- Member 检查 locks，添加 lock，完成工作，移除 lock，并写简短更新。
- Lead 总结日志并更新计划。

## 限制

- 这是软协作流程。
- 它不执行操作系统级权限。
- 它不能阻止某个人或某个 Agent 忽略规则。
- 它依赖 Agent 读取并遵守共享 Markdown 文件。
- 它有意不是服务器、数据库、CLI、hook 系统或企业权限模型。

## 高级分支

Advanced local protocol experiments are preserved on the `standard-local-protocol` branch.

## English

See [README.md](README.md).
