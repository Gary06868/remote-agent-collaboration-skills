# Remote Agent Collaboration Skills

同时安装两个 Skill，但每个 Codex thread 只能激活一个角色。

![演示](docs/assets/demo.gif)

> 当前本机验证状态：**FAILED CORE GATE**。在这个开发环境中，真实 Codex thread 没有观测到 hooks 运行。因此 `collabctl` 会在缺少真实 `session_id` 时 fail closed，`doctor` 不会报告 healthy。

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
