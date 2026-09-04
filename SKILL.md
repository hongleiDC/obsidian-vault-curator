---
name: obsidian-vault-curator
description: 分析、设计、整理和维护 Obsidian Markdown 笔记与 Vault，尤其适用于笔记长期保存在 GitHub 仓库中的知识库。用于先分析现有 Vault 的数据形态、目录、Frontmatter、标签、链接、任务、日志、来源与笔记长度等结构特征，再选择合适的混合笔记逻辑与方法；从仓库外私有持久化状态目录恢复 Vault 绑定、当前项目工作进度和已采用的笔记方法；所有 GitHub 修改必须通过临时分支和 PR，验证通过后自动 squash merge，并清理临时分支；默认按项目名称组织浅层目录，目录深度尽量不超过三级。必须保护原始语义与隐私，绝不把用户仓库地址、私有路径、令牌或个人笔记内容写入 Skill 源码仓库或 Skill 包。
---

# Obsidian Vault Curator

把已有内容整理成简洁、可检索、可关联、可长期维护的 Obsidian 知识库。不要只做 Markdown 美化；先理解现有数据结构、项目上下文和笔记方法，再决定怎么整理。

按需读取：
- `references/private-state.md`：外部私有状态、Vault 绑定、隐私边界。
- `references/project-progress.md`：跨对话项目进度恢复与 checkpoint。
- `references/github-backend.md`：PR-only 写回、自动合并、分支清理、冲突规则。
- `references/note-methodology.md`：Vault 诊断、笔记类型、混合方法、浅目录规则。
- `references/formatting-rules.md`：Properties、任务、代码、公式、callout。
- `references/vault-linking.md`：索引、真实双链、迁移和批量整理。
- `references/examples.md`：仅使用虚构通用示例。

## 核心工作模式

1. **Vault 诊断与方法设计**：先分析，再推荐适合当前数据的混合笔记方法。
2. **项目持续整理**：恢复当前项目进度，再处理该项目笔记。
3. **单篇 / 批量 GitHub 整理**：任何写入都走 PR。
4. **本地 / 上传 Markdown 整理**：不涉及 GitHub 时按本地交付。
5. **概念补丁**：只解释局部术语，不重排整篇。
6. **审计模式**：只报告问题，不写回。

## 私有状态必须与 Skill 仓库隔离

状态目录解析顺序：
1. `OBSIDIAN_CURATOR_STATE_DIR`；
2. 否则 `~/.obsidian-vault-curator/`。

状态目录必须位于 Skill 源码树和 Vault Git 仓库之外。不要在 Skill 源码、Skill ZIP、公开 README、示例或提交里保存真实 Vault repository、私有路径、token、cookie、真实笔记标题、附件名或正文。

建议布局：

```text
<state-root>/
├── profiles/default.json
├── methods/note-system.json
├── projects/
│   ├── index.json
│   └── <project-id>.json
├── runtime/last-success.json
├── cache/
│   ├── vault-index.json
│   └── vault-patterns.json
└── locks/github-write.lock
```

Vault 绑定和笔记方法使用 `scripts/state_store.py`；项目进度使用 `scripts/project_state.py`。

如果环境没有持久可写文件系统，不要假装已持久化，也不要把私有信息塞回 Skill 包；明确说明限制。

## GitHub-backed 启动流程

每次新对话或新任务都不要依赖聊天记忆，按顺序执行：

1. 读取 `profiles/default.json`，恢复 Vault repository、base branch、Vault root。
2. 读取 `projects/index.json`，解析当前项目；读取对应 `<project-id>.json`。
3. 项目解析优先级：用户明确项目名 → alias 命中 → active project → 顶层项目目录可唯一推断。
4. 恢复 `phase`、`current_focus`、`completed`、`next_actions`、`blockers`、关键 `decisions` 和最近成功 PR/merge 信息。
5. 若存在 `methods/note-system.json`，加载已采用的笔记方法。
6. 用 GitHub connector 重新读取远端当前文件；远端正文是内容真相，私有项目状态是工作进度真相。
7. 形成完整修改方案并做保护检查，然后进入 PR 流程。

不要让用户重复已经持久化的项目进度。只有项目匹配确实有歧义且会影响不同项目目录时才询问。

## 跨对话项目进度 checkpoint

项目状态只保存继续工作所需的紧凑信息：
- 项目名、别名、状态、阶段；
- 当前焦点；
- 已完成事项；
- 下一步；
- 阻塞点；
- 关键决策；
- 必要的私有 working set；
- 最近成功 PR、merge commit 和临时分支。

不要把整段对话历史或笔记正文写入项目状态。

PR 成功合并并完成分支清理后才更新 checkpoint：把本次逻辑工作加入 `completed`，刷新 `current_focus`、`next_actions`、`blockers`，记录 PR 和 merge commit，并清空已删除的临时分支。若验证或合并失败，不要提前标记完成；把失败原因写入 blocker/next action。

使用：

```bash
python scripts/project_state.py init --id example --name "Example Project"
python scripts/project_state.py list
python scripts/project_state.py use --id example
python scripts/project_state.py status
python scripts/project_state.py read
python scripts/project_state.py update --focus "Current task" --next-action "Next task"
```

## GitHub 写回硬规则：每次都必须 PR

任何 GitHub 修改都禁止直接写基础分支，即使只改一个 Markdown 文件。

固定流程：
1. 从最新 base head 创建唯一临时分支。
2. 在内存中完成本批次全部修改。
3. 运行语义保护、链接和必要的结构检查。
4. 尽量把本批次变更合成一个原子 commit；否则在临时分支串行写入。
5. 创建 PR。
6. 重新检查 PR mergeability 和冲突。
7. 验证通过且 PR 可合并时自动 squash merge。
8. merge 成功后自动删除临时 head branch，并确认它已不存在。
9. 最后更新项目进度 checkpoint。

不允许通过私有配置重新开启 direct-write。若当前 GitHub 工具无法删除已合并分支，明确报告 cleanup 未完成；后续不得复用该分支。

错误规则：
- 同一路径绝不并行写。
- stale SHA / ref conflict 只刷新后重试 1 次。
- 权限、认证或 connector 失败立即停止，不循环重试。
- 分支名冲突只换一次后缀。
- 内容无变化不提交。
- base 在准备期间变化且产生冲突时，不 force push、不 force merge；保留 PR 并报告阻塞。

## 浅目录硬偏好

相对 Vault 根目录，目标目录深度尽量不超过 **3 层文件夹**。默认优先：

```text
<Project>/<Category>/<Note>.md
```

确有大型阶段或 workstream 时才增加第三层：

```text
<Project>/<Category>/<Workstream>/<Note>.md
```

规则：
- 项目相关工作优先以稳定项目名作为第一层。
- 第二层只保留少量功能类别，例如 `Notes`、`Meetings`、`Sources`、`Experiments`、`Decisions`、`Reference`。
- 第三层是例外，不是默认。
- 不用多级文件夹重复表达 tags、Properties、wikilinks 或 MOC 已能表达的分类。
- 现有深层目录不要一次性破坏性拍平；先设计浅层目标，再分批通过 PR 迁移并验证 backlink。

## Vault 诊断与笔记方法

当用户要求分析当前知识库如何整理时，先只读诊断，不先套 PARA、Zettelkasten 或统一模板。

分析：笔记数量/长度、目录深度、日期命名、Frontmatter keys、tags、wikilinks、tasks、source/url、代码、表格、callout、Dataview，以及反复出现的 note type。

常见功能类型：Capture、Source、Log/Daily/Experiment、Project、Concept/Evergreen、Decision、How-to/Troubleshooting、Reference、MOC/Hub。

优先选择混合方法。先挑 5–15 篇代表性笔记试点；用户接受后把方法保存到外部私有 `methods/note-system.json`，后续自动沿用。只有用户要求重设计或 Vault 明显漂移时才重新诊断。

本地/materialized Vault 可运行：

```bash
python scripts/analyze_vault_patterns.py <vault-root> --output <private-report.json>
```

## 核心保护契约

整理时不要无意改写、删除或破坏：
- 事实、数字、结论、引用和限定条件；
- Frontmatter / Properties 已有字段；
- fenced code、inline code、命令、配置；
- LaTeX / 数学公式；
- embeds、附件路径和尺寸；
- wikilinks、heading links、block links、block IDs；
- tasks、Dataview / DataviewJS；
- footnotes、引用块、HTML、Obsidian comments；
- callout 语义和折叠状态。

修改前后文件都可访问且脚本环境可用时运行：

```bash
python scripts/verify_note_preservation.py ORIGINAL CURATED
```

发现保护项丢失时先修复，再进入 PR。

## 单篇整理原则

1. 先完整读取，再编辑。
2. 判断笔记所属功能类型与当前项目阶段。
3. 标记保护对象。
4. 用最少层级重建结构。
5. 合并而不是覆盖 Properties。
6. 只新增真实存在且有语义价值的 wikilink。
7. 修正明显语病，但不改变原意。
8. 检查 YAML、标题、链接、任务、代码、公式、嵌入和保护项。

排版保持克制：正文优先 `##` / `###`，不为每两三句话建标题；表格只用于真实结构化数据；默认不加 emoji；普通笔记 callout 通常 0–2 个；不要在文末堆砌无语义“相关笔记”。
