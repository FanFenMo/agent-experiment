# Agent 实验二仓库

这是“软件产品综合开发实践（实验二）”的 Agent 实验仓库。项目实现了一个离线可运行的实验交付助手 Agent，用来读取实验要求、调用本地工具拆解交付物、规划报告结构、检查仓库文件，并生成一份可复现的运行记录。

这个仓库刻意不依赖外部大模型 API。这样演示时不需要 API key 或网络，老师可以直接运行脚本看到 Agent 的 tool 调用过程。核心 prompt、context 和 tool definitions 都保存在仓库中，便于评分时检查。

## 目录说明

- `src/agent_experiment/agent.py`：Agent 编排逻辑，负责按任务调用 tool 并生成最终答复。
- `src/agent_experiment/tools.py`：tool 定义和实现，包括 context 读取、rubric 解析、报告规划、反思草稿、仓库检查。
- `prompts/system_prompt.md`：Agent 的核心系统 prompt。
- `context/experiment2_rubric.md`：实验二 rubric 的结构化上下文。
- `scripts/run_demo.py`：运行一次完整 Agent demo，并输出 JSON 运行记录。
- `scripts/render_execution_screens.py`：把运行记录渲染成 3 张报告截图。
- `tests/test_agent.py`：核心解析和 Agent 执行的单元测试。
- `reports/`：实验报告和运行截图输出目录。

## 快速运行

```powershell
$env:PYTHONPATH = "src"
python .\scripts\run_demo.py --output .\demo_outputs\experiment2_run.json
python .\scripts\render_execution_screens.py .\demo_outputs\experiment2_run.json --output-dir .\reports\assets
python -m unittest discover -s tests
```

运行后，终端会显示 Agent 的每一步 tool 调用，`demo_outputs/experiment2_run.json` 会保存完整 execution trace，`reports/assets/` 会生成用于报告的运行截图。

## Agent 功能概述

这个 Agent 的目标是帮助学生完成实验二交付物。它会先读取实验要求 context，再提取截止时间、交付物和评分项，然后生成代码仓库检查清单、报告结构建议和 AI 使用反思草稿。它使用的上下文集成方式包括：文件型 rubric context、系统 prompt、tool schema，以及 execution trace 中的中间结果。

## 工具列表

Agent 当前注册了 5 个工具：

- `read_context`：读取本地实验要求文档。
- `extract_rubric`：从 context 中提取截止时间、交付物和评分项。
- `plan_report`：根据 rubric 生成不超过 5 页的报告结构。
- `draft_reflection`：围绕一个具体 AI 技术困难生成简短反思。
- `validate_repository`：检查仓库中是否存在 prompt、context、代码、demo 和测试文件。

## 设计取舍

项目没有把 Agent 做成联网聊天机器人，而是做成一个可复现的本地工具型 Agent。这样更适合课堂实验评分：执行路径稳定、tool 定义明确、报告截图可以重复生成，也能清楚展示 prompt、context 和 tool calling 的关系。
