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
    due = _line_value(content, "Due:")
    return {
        "deadline": due,
        "deliverables": _bullets_after_heading(content, "## Deliverables"),
        "evaluation": _bullets_after_heading(content, "## Evaluation"),
        "reflection_requirement": _paragraph_after_heading(
            content, "## Reflection Requirement"
        ),
    }


def plan_report(args: dict[str, Any]) -> dict[str, Any]:
    rubric = args["rubric"]
    return {
        "page_limit": "no more than 5 pages",
        "sections": [
            {
                "title": "Agent code repository",
                "purpose": "Provide the GitHub repo and point to prompts, context, tools, and agent logic.",
            },
            {
                "title": "Agent design",
                "purpose": "Explain the main function, registered tools, and context integration in under 500 words.",
            },
            {
                "title": "Agent execution",
                "purpose": "Show 3 to 4 screenshots from a real run and explain what each step proves.",
            },
            {
                "title": "AI-assisted development reflection",
                "purpose": "Describe one concrete AI hurdle and the exact engineering fix.",
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
            description="Read a local experiment context file.",
            input_schema={"path": "Path to a UTF-8 markdown context file."},
            handler=read_context,
        ),
        ToolDefinition(
            name="extract_rubric",
            description="Extract deadline, deliverables, evaluation, and reflection requirements.",
            input_schema={"content": "Raw rubric text."},
            handler=extract_rubric,
        ),
        ToolDefinition(
            name="plan_report",
            description="Plan a short report that aligns with the rubric.",
            input_schema={"rubric": "Rubric object returned by extract_rubric."},
            handler=plan_report,
        ),
        ToolDefinition(
            name="draft_reflection",
            description="Draft a concise AI-use reflection around a specific technical hurdle.",
            input_schema={
                "hurdle": "Specific AI failure or limitation.",
                "fix": "Exact engineering response used to resolve it.",
            },
            handler=draft_reflection,
        ),
        ToolDefinition(
            name="validate_repository",
            description="Check whether required repository files exist.",
            input_schema={"root": "Repository root path."},
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
