# Remote Agent Collaboration Skills

给小团队、小公司、开源协作和多人 AI vibe coding 用的 Codex 协作管理层。

同时安装两个 Skill，但每个 Codex thread 只能激活一个角色。

<p>
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-0f766e">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-2563eb">
  <img alt="Tests passing" src="https://img.shields.io/badge/tests-7%20passing-16a34a">
  <img alt="Phase 0 failed core gate" src="https://img.shields.io/badge/Phase%200-FAILED%20CORE%20GATE-dc2626">
</p>

![演示](docs/assets/demo.gif)

上面的动画由 `scripts/generate_demo.py` 根据真实 `collabctl` 命令生成，覆盖 Skill 验证、lead 激活、同线程 member 被拒绝、member 工作、请求日志压缩、lead 压缩日志和 SHA-256 校验。

如果你正在让多个人类和多个 AI Agent 一起做项目，这个 Skill 解决的是协作失控问题：谁是 lead、谁是 member、谁能发全局公告、谁只能改自己的模块、日志什么时候压缩、任务状态怎么流转，都用同一套本地协议记录下来。

适合这些场景：

- 小团队或小公司用 Codex 共同推进一个代码库
- 多个 Codex thread 同时工作，但每个 thread 必须保持固定角色
- lead 负责分配任务、审核、公告和日志压缩，member 只处理授权模块
- 把 vibe coding 从聊天驱动变成可追踪、可审计、可交接的协作流程

> 当前本机验证状态：**FAILED CORE GATE**。在这个开发环境中，真实 Codex thread 没有观测到 hooks 运行。因此 `collabctl` 会在缺少真实 `session_id` 时 fail closed，`doctor` 不会报告 healthy。

快速入口：[Agent 安装](#给-ai-agent安装两个-skill每个线程只激活一个角色) · [快速开始](#快速开始) · [角色模型](#角色模型) · [示例项目](examples/vibe-coding-team/README.md) · [English README](README.md)

## 它管理什么

- **角色：** 两个显式入口，`$team-lead-collaboration` 和 `$team-member-collaboration`。
- **线程角色锁：** 一个 Codex thread 激活角色后不应切换；缺少 session 上下文时 `collabctl` 对角色写操作 fail closed。
- **项目协作：** 成员、模块、任务分配、任务状态、handoff、公告、确认、请求和审核流。
- **运行记忆：** append-only JSONL 日志、模块摘要、日志压缩 archive 和 SHA-256 校验记录。
- **Agent 安装路径：** marketplace 元数据、两个 Skill、hooks、doctor 输出和 `/hooks` 信任说明。

## 给 AI Agent：安装两个 Skill，每个线程只激活一个角色

新 Agent 可以只读本节完成安装。

1. 添加 marketplace：

   ```bash
   codex plugin marketplace add Gary06868/remote-agent-collaboration-skills
   ```

2. 打开 `/plugins`，安装 **Remote Agent Collaboration**。
3. 验证两个 Skill 都已安装且名称不同：
   - `team-lead-collaboration`
   - `team-member-collaboration`
4. 打开 `/hooks`，审核并信任 hooks。
5. 新建 Codex thread。
6. 明确调用其中一个：

   ```text
   $team-lead-collaboration Initialize and govern collaboration for this project as the registered lead actor.
   ```

   或：

   ```text
   $team-member-collaboration Read current announcements, accept my assigned task, and work only inside my authorized module.
   ```

7. 不得在同一个 thread 调用另一个角色。
8. 运行：

   ```bash
   collabctl doctor --json
   ```

9. 报告安装路径、Plugin 状态、hook 状态和 `role_lock_enforced`。

可复制给 Agent 的安装指令：

```text
Install the remote-agent-collaboration plugin from Gary06868/remote-agent-collaboration-skills. Install both bundled Skills. Do not activate either role during installation. Open /hooks, review and trust hooks, start a new Codex thread, choose exactly one role with $team-lead-collaboration or $team-member-collaboration, run collabctl doctor --json, and report plugin status, hook status, installed paths, and role_lock_enforced.
```

当前 CLI 说明：本机 `codex-cli 0.130.0-alpha.5` 只有 `codex plugin marketplace add|upgrade|remove` 和交互式 `/plugins`，没有 `codex plugin add --json` 或 `codex plugin list --json`。如果新版 CLI 支持自动化安装/列表命令，必须用真实测试结果更新文档。

## 快速开始

```bash
python -m pip install -e .
collabctl init --project-id demo --yes
collabctl actor bootstrap --actor-id lead --role lead --yes
collabctl session activate --session-id thread-lead --role lead --skill team-lead-collaboration --actor-id lead
collabctl doctor --json
```

## 角色模型

| 角色 | Skill | 允许 | 禁止 |
| --- | --- | --- | --- |
| Lead | `$team-lead-collaboration` | 成员、模块、任务、公告、审核、日志压缩治理 | 在同线程切换到 member |
| Member | `$team-member-collaboration` | 处理分配任务、确认公告、写授权模块日志、创建 request | 审核自己、压缩日志、修改全局策略、切换到 lead |

Hooks 只是防护栏；确定性校验由 `collabctl` 执行。
