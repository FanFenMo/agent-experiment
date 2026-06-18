# Agent Experiment

这是“软件产品综合开发实践（实验二）”的 Agent 实验仓库。项目实现了一个离线可运行的实验交付助手 Agent，用来读取实验要求、调用本地工具拆解交付物、规划报告结构、检查仓库文件，并生成一份可复现的运行记录。

这个仓库不依赖外部大模型 API，可以直接运行脚本看到 Agent 的工具调用过程。核心 prompt、context 和 tool definitions 均保存在仓库中。

## 目录说明

- `src/agent_experiment/agent.py`：Agent 编排逻辑，负责按任务调用工具并生成最终答复。
- `src/agent_experiment/tools.py`：工具定义和工具实现，包括 context 读取、rubric 解析、报告规划、反思草稿、仓库检查。
- `prompts/system_prompt.md`：Agent 的核心系统 prompt。
- `context/experiment2_rubric.md`：实验二 rubric 的结构化上下文。
- `scripts/run_demo.py`：运行一次完整 Agent 演示，并输出 JSON 运行记录。
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

运行后，终端会显示 Agent 的每一步工具调用，`demo_outputs/experiment2_run.json` 会保存完整 execution trace，`reports/assets/` 会生成用于报告的运行截图。

## Agent 功能概述

先读取实验要求 context，再提取截止时间、交付物和评分项，然后生成代码仓库检查清单、报告结构建议和 AI 使用反思草稿。它使用的上下文集成方式包括：文件型 rubric context、系统 prompt、工具 schema，以及执行 trace 中的中间结果。

## 工具列表

Agent 当前注册了 5 个工具：

- `read_context`：读取本地实验要求文档。
- `extract_rubric`：从 context 中提取 deadline、deliverables 和 evaluation。
- `plan_report`：根据 rubric 生成不超过 5 页的报告结构。
- `draft_reflection`：围绕一个具体 AI 技术困难生成简短反思。
- `validate_repository`：检查仓库中是否存在 prompt、context、代码、demo 和测试文件。
