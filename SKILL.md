---
name: obsidian-vault-curator
description: 分析、设计、整理和维护 Obsidian Markdown 笔记与 Vault，尤其适用于长期保存在 GitHub 仓库中的知识库。用于从仓库外私有状态恢复 Vault 绑定、当前项目进度与已采用的笔记方法；先分析现有数据形态，再按用户已有命名体系、项目结构和混合笔记方法整理；支持单篇/多篇重构、Properties、wikilinks、项目进度 checkpoint 与 GitHub PR-only 安全写回。所有 GitHub 修改必须通过 PR，验证后自动 squash merge，并在合并后清理临时分支。必须保护原始语义与隐私，不把用户仓库地址、私有路径、令牌、真实项目清单或笔记正文写入 Skill 源码仓库或 Skill 包。
---

# Obsidian Vault Curator

把已有内容整理成可检索、可关联、可持续维护的 Obsidian 知识库。不要把它当成单纯 Markdown 美化器：先恢复项目上下文和用户方法，再整理当前内容。

按需读取：
- `references/private-state.md`：私有持久化状态、绑定、权限和隐私。
- `references/project-progress.md`：跨对话项目进度恢复与 checkpoint。
- `references/github-backend.md`：PR-only、自动合并、分支清理、冲突与重试。
- `references/note-methodology.md`：Vault 诊断、笔记类型、用户命名体系、浅层目录与长期方法。
- `references/formatting-rules.md`：Properties、任务、代码、公式、callout。
- `references/vault-linking.md`：索引、真实双链、批量整理与迁移。
- `references/examples.md`：仅使用虚构通用示例。

## 不可破坏的边界

- 私有状态必须位于 Skill 仓库和 Vault Git 仓库之外。
- 真实 Vault repository、token、私有路径、真实项目清单和笔记正文不得进入公开 Skill 源码、示例或 ZIP。
- GitHub 远端文件是笔记正文的 source of truth；私有状态是工作流上下文的 source of truth。
- 不依赖聊天窗口记忆保存长期项目进度。
- 不根据文件/目录前缀的字面含义擅自推断用户语义；前缀含义从私有方法状态读取。

## 私有状态布局

默认解析 `OBSIDIAN_CURATOR_STATE_DIR`，否则使用 `~/.obsidian-vault-curator/`。

```text
<state-root>/
├── profiles/default.json
├── methods/note-system.json
├── projects/index.json
├── projects/<project-id>.json
├── runtime/last-success.json
├── cache/
└── locks/github-write.lock
```

首次绑定和方法持久化使用 `scripts/state_store.py`；项目进度使用 `scripts/project_state.py`。

## GitHub-backed 每次启动流程

1. 读取 `profiles/default.json` 恢复 Vault repository、base branch 和可选 root。
2. 读取 `methods/note-system.json` 恢复已采用的笔记方法、命名空间和项目前缀规则。
3. 读取 `projects/index.json` 并解析当前项目：用户明确项目名 → alias → active project → 从请求范围唯一推断。
4. 读取对应 `<project-id>.json`，恢复 phase、current_focus、completed、next_actions、blockers、decisions 和最近 GitHub 结果。
5. 用 GitHub connector 重新确认仓库、分支和当前远端文件；不要复用旧聊天中的正文或 SHA。
6. 在任何写入前检查 PR 分支清理能力：当前 GitHub 工具可以删除分支，或仓库已启用 `delete_branch_on_merge`。两者都没有时停止写入，避免制造垃圾分支。
7. 完成只读分析、保护检查和完整修改方案后再进入 PR 事务。

如果私有状态不存在，只询问真正缺失的绑定/项目/方法信息，并写入私有状态；以后不要重复询问。

## 跨对话项目进度

每个持续项目都维护独立状态。项目状态保存：

- `project_id`、`project_name`、aliases；
- status、phase、current_focus；
- concise completed；
- ordered next_actions；
- blockers；
- 影响后续整理的 decisions；
- 必要 working_set；
- 最近成功 PR、merge commit 和临时分支状态。

开始任务前必须读取项目状态；PR 成功合并并完成分支清理后才 checkpoint。失败时不要把任务记为 completed，而是更新 blocker 和 next action。

## 用户命名体系与浅目录硬规则

优先沿用用户已有命名体系，不另造第二套目录分类。用户的真实 roots、prefixes 和 prefix semantics 保存在私有 `methods/note-system.json`。

默认支持这种结构语义：

```text
NB.<AREA>/
└── <PREFIX>.<ProjectName>/
    ├── <Note>.md
    └── <OptionalGroup>/
        └── <Note>.md
```

规则：

- 第 1 层：稳定大类命名空间，例如 `NB.<AREA>`。
- 第 2 层：具体研究/工作/项目单元，形式为 `<PREFIX>.<ProjectName>`。
- 配置中的多个第 2 层 prefix 默认是**同级项目方向前缀**，不是笔记类型。
- 不因为 prefix 名字看起来像 `NAV` 就解释成导航页、MOC 或 Hub；必须读取私有 prefix mapping。
- 第 3 层：只在项目内部确有必要时建立一个小类/阶段/workstream。
- 默认不创建第 4 层文件夹；跨项目分类使用 Properties、tags、wikilinks 或 MOC。
- 保留用户现有拼写和命名风格，不擅自做英语“纠错”。
- 深层旧目录迁移必须分批 PR，并验证 backlink/附件引用。

完整方法见 `references/note-methodology.md`。

## GitHub 写回：PR-only + 自动闭环

任何 GitHub 修改都禁止直接写 base branch，包括单文件修改。

标准事务：

1. 从最新 base head 创建唯一临时分支。
2. 在内存中形成本批次完整最终内容。
3. 执行语义保护、链接和路径检查。
4. 尽量把本批次变更合成一个原子 commit。
5. 创建 PR。
6. 检查 PR mergeability 和验证结果。
7. 验证通过且可合并时自动 `squash` merge。
8. 合并成功后删除临时 head branch，并确认分支不存在。
9. 更新项目 checkpoint，记录完成项、下一步和 merge commit。
10. 释放写锁。

高风险 rename/move/delete/attachment 仍需用户先授权；一旦授权并验证通过，同样完成 PR → squash merge → branch cleanup，不故意遗留已合并分支。

错误规则：
- 同一路径不并行写。
- stale SHA/ref conflict 只刷新后重试 1 次。
- 权限/认证失败立即停止，不循环重试。
- branch name collision 只换一次后缀。
- byte-identical 内容不提交。
- 冲突 PR 不 force push、不 force merge。
- 分支清理未完成时不得把事务标记为完全完成，也不得复用该临时分支。

## Vault 诊断与笔记方法

用户要求“分析我的笔记怎么整理/设计笔记逻辑”时：

1. 先只读诊断，不立即改 Vault。
2. 分析目录深度、长度分布、Frontmatter、tags、links、tasks、日期/日志、sources、code、tables、callouts、Dataview 等结构特征。
3. 识别真实功能类型，例如 capture、source、log/experiment、project、concept、decision、how-to、reference、MOC/hub。
4. 找真正摩擦点，不把“格式不一致”误当“知识逻辑混乱”。
5. 优先设计最小混合方法，不强推 PARA/Zettelkasten/统一模板。
6. 先用 5–15 篇代表性笔记试点。
7. 用户接受后，把方法和命名规则写入私有 `methods/note-system.json`。
8. 后续整理自动沿用；只有用户要求或 Vault 明显漂移时重新诊断。

本地/materialized Vault 可运行：

```bash
python scripts/analyze_vault_patterns.py <vault-root> --output <private-report.json>
```

聚合报告默认不输出笔记正文、标题或路径。

## 核心保护契约

整理时可以重排结构，但不要无意改写、删除或破坏：

- 事实、数字、结论、例子、引用和限定条件；
- Frontmatter/Properties 未知字段和值；
- fenced/inline code、命令、配置；
- LaTeX/MathJax；
- embeds、Markdown 图片、附件路径与尺寸；
- wikilinks、heading links、block links；
- block IDs；
- tasks；
- Dataview/DataviewJS；
- footnotes、引用块、HTML、Obsidian comments；
- callout 语义和折叠状态。

原文件和整理后文件都可访问时运行：

```bash
python scripts/verify_note_preservation.py ORIGINAL CURATED
```

保护项丢失时先修复再写回。

## 单篇与批量整理

单篇：完整读取 → 判断项目和 note type → 保护语义 → 最少层级重构 → 合并 Properties → 验证 links → 保存。

批量：先按项目/研究单元选择小批次；每批默认最多 10 个 changed files；先单篇整理，再建立真实跨笔记关联；不要一开始全库重写。

## 内容组织原则

- Capture：快速记录，少格式。
- Source：来源与用户 synthesis 分开。
- Log/Daily/Experiment：保留时间线。
- Project：围绕目标、状态、行动、决策。
- Concept/Evergreen：保存可独立复用的理解。
- Decision：记录选择及理由。
- How-to/Troubleshooting：症状/目标 → 证据 → 步骤 → 验证 → 失败模式。
- Reference：强调快速检索，表格/列表可优先。
- MOC/Hub：用于成熟知识簇的导航，不是 backlink dump。

文件夹负责粗粒度位置，Properties/tags 负责横向分类，wikilinks 负责语义关系，MOC 负责成熟知识簇导航；不要四套系统重复表达同一分类。
