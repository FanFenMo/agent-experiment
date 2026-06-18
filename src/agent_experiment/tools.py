from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, str]
    handler: ToolHandler = field(repr=False, compare=False)

    def public_spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


def read_context(args: dict[str, Any]) -> dict[str, Any]:
    path = Path(args["path"])
    content = path.read_text(encoding="utf-8")
    return {
        "path": str(path),
        "characters": len(content),
        "content": content,
    }


def extract_rubric(args: dict[str, Any]) -> dict[str, Any]:
    content = args["content"]
    due = _line_value(content, "截止时间:")
    return {
        "deadline": due,
        "deliverables": _bullets_after_heading(content, "## 交付物"),
        "evaluation": _bullets_after_heading(content, "## 评分项"),
        "reflection_requirement": _paragraph_after_heading(
            content, "## 反思要求"
        ),
    }


def plan_report(args: dict[str, Any]) -> dict[str, Any]:
    rubric = args["rubric"]
    return {
        "page_limit": "不超过 5 页",
        "sections": [
            {
                "title": "Agent 代码仓库",
                "purpose": "提供 GitHub 仓库，并说明 prompt、context、tool 和 Agent 逻辑的位置。",
            },
            {
                "title": "Agent 设计说明",
                "purpose": "用不超过 500 字说明主要功能、已注册 tool 和 context 集成方式。",
            },
            {
                "title": "Agent 运行说明",
                "purpose": "展示 3 到 4 张真实运行截图，并说明每一步证明了什么。",
            },
            {
                "title": "AI 辅助开发反思",
                "purpose": "描述一个具体 AI 技术困难，以及对应的工程化解决方法。",
            },
        ],
        "rubric_alignment": {
            "system_mechanics": rubric["evaluation"][0],
            "execution": rubric["evaluation"][1],
            "reflection": rubric["evaluation"][2],
        },
    }


def draft_reflection(args: dict[str, Any]) -> dict[str, Any]:
    hurdle = args["hurdle"]
    fix = args["fix"]
    return {
        "hurdle": hurdle,
        "fix": fix,
        "text": (
            "在完成实验时，AI 最明显的问题不是不会写代码，而是会把工具调用协议想得过于自由。"
            f"具体表现是：{hurdle}。我没有直接相信第一次输出，而是把需求拆成可验证的小步骤，"
            f"先查看项目结构和模板，再固定工具输入格式，最后用 demo 输出和文档渲染结果反复检查。"
            f"解决办法是：{fix}。这个过程让我意识到，AI 更适合做候选方案和初稿，最终质量仍然需要"
            "通过明确约束、可复现执行和人工验收来保证。"
        ),
    }


def validate_repository(args: dict[str, Any]) -> dict[str, Any]:
    root = Path(args["root"])
    expected_paths = [
        "README.md",
        "prompts/system_prompt.md",
        "context/experiment2_rubric.md",
        "src/agent_experiment/agent.py",
        "src/agent_experiment/tools.py",
        "scripts/run_demo.py",
        "scripts/render_execution_screens.py",
        "tests/test_agent.py",
    ]
    checks = [
        {"path": item, "exists": (root / item).exists()} for item in expected_paths
    ]
    return {
        "root": str(root),
        "checks": checks,
        "complete": all(item["exists"] for item in checks),
    }


def default_tools() -> dict[str, ToolDefinition]:
    tools = [
        ToolDefinition(
            name="read_context",
            description="读取本地实验 context 文件。",
            input_schema={"path": "UTF-8 markdown context 文件路径。"},
            handler=read_context,
        ),
        ToolDefinition(
            name="extract_rubric",
            description="提取截止时间、交付物、评分项和反思要求。",
            input_schema={"content": "rubric 原始文本。"},
            handler=extract_rubric,
        ),
        ToolDefinition(
            name="plan_report",
            description="根据 rubric 规划简短实验报告。",
            input_schema={"rubric": "extract_rubric 返回的 rubric 对象。"},
            handler=plan_report,
        ),
        ToolDefinition(
            name="draft_reflection",
            description="围绕一个具体技术困难生成 AI 使用反思草稿。",
            input_schema={
                "hurdle": "具体 AI 失败点或能力限制。",
                "fix": "解决该问题的具体工程化措施。",
            },
            handler=draft_reflection,
        ),
        ToolDefinition(
            name="validate_repository",
            description="检查仓库中必需文件是否存在。",
            input_schema={"root": "仓库根目录路径。"},
            handler=validate_repository,
        ),
    ]
    return {tool.name: tool for tool in tools}


def _line_value(content: str, prefix: str) -> str:
    for line in content.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return ""


def _bullets_after_heading(content: str, heading: str) -> list[str]:
    lines = content.splitlines()
    start = lines.index(heading) + 1
    bullets: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def _paragraph_after_heading(content: str, heading: str) -> str:
    lines = content.splitlines()
    start = lines.index(heading) + 1
    parts: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.strip():
            parts.append(line.strip())
    return " ".join(parts)
