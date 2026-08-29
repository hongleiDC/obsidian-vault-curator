# Obsidian Vault Curator 示例

这些示例用于校准输出风格，不要求逐字套用。

## 示例 1：单篇结构整理

### 输入

```markdown
ros noetic中tf是坐标变换，tf2更常用，我这里老是出现map到base_link断掉的问题，有时候是时间戳不对。

![[tf-tree.png]]

我需要检查 /tf 和 /tf_static，还要看use_sim_time。rosbag回放的时候clock也很重要。
```

### 输出

```markdown
---
tags:
  - ros/noetic
  - tf
aliases:
  - TF 排查
---

# ROS Noetic 中的 TF 排查

TF 用于维护坐标系之间的变换关系。当前问题表现为 `map` 到 `base_link` 的变换链偶尔中断，可能与时间戳有关。

![[tf-tree.png]]

## 重点检查项

- 检查 `/tf` 与 `/tf_static` 是否持续发布预期变换。
- 检查 `use_sim_time` 配置是否与当前运行模式一致。
- 回放 rosbag 时关注 `/clock`，确认各节点使用同一时间基准。
```

说明：只重排已有信息，没有凭空加入具体命令、数值或故障结论。

## 示例 2：概念补丁

### 输入片段

```markdown
- rosbag 回放时要注意 `use_sim_time`。
```

用户问：“use_sim_time 是什么？”

### 输出片段

```markdown
- rosbag 回放时要注意 `use_sim_time`。
  > [!question]- 补丁：`use_sim_time` 是什么？
  > `use_sim_time` 用来让 ROS 节点使用仿真时间而不是系统墙钟时间。启用后，节点通常从 `/clock` 获取当前时间，因此 rosbag 回放或仿真环境中的时间源是否正常会直接影响基于时间戳的处理。
```

## 示例 3：不要制造假双链

如果 Vault 中只确认存在：

- `ROS Noetic.md`
- `TF Debugging.md`

正文出现“时间同步”时，不要自动写成 `[[时间同步]]`，除非该笔记真实存在。可以在真正相关的位置写：

```markdown
这一问题也会影响 [[TF Debugging|TF 排查]]。
```

## 示例 4：保留插件字段

### 输入

```markdown
---
status: active
tags: [gnss]
custom_plugin_field: abc
---

baseline:: 1.2 m

- [ ] 检查 heading offset
```

整理后必须继续保留：

- `status: active`
- `custom_plugin_field: abc`
- `baseline:: 1.2 m`
- `- [ ]` 任务状态

可以扩充 `tags`，但不得通过模板覆盖掉未知字段。
