from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .tools import ToolDefinition, default_tools


@dataclass(frozen=True)
class ToolCallRecord:
    index: int
    tool: str
    arguments: dict[str, Any]
    result: dict[str, Any]


@dataclass(frozen=True)
class AgentRun:
    task: str
    system_prompt_path: str
    tool_specs: list[dict[str, Any]]
    trace: list[ToolCallRecord]
    final_answer: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "system_prompt_path": self.system_prompt_path,
            "tool_specs": self.tool_specs,
            "trace": [asdict(item) for item in self.trace],
            "final_answer": self.final_answer,
        }


class ExperimentAgent:
    def __init__(
        self,
        system_prompt_path: Path,
        tools: dict[str, ToolDefinition] | None = None,
    ) -> None:
        self.system_prompt_path = system_prompt_path
        self.system_prompt = system_prompt_path.read_text(encoding="utf-8")
        self.tools = tools or default_tools()

    def run(self, task: str, context_path: Path, repo_root: Path) -> AgentRun:
        trace: list[ToolCallRecord] = []

        context = self._call(trace, "read_context", {"path": str(context_path)})
        rubric = self._call(trace, "extract_rubric", {"content": context["content"]})
        report_plan = self._call(trace, "plan_report", {"rubric": rubric})
        reflection = self._call(
            trace,
            "draft_reflection",
            {
                "hurdle": "AI 曾经把工具参数和文档渲染步骤混在一起，导致输出看似完整但不可复现",
                "fix": "先把工具 schema 固定在代码里，再用 JSON execution trace 和 DOCX 渲染结果逐项核对",
            },
        )
        repository = self._call(trace, "validate_repository", {"root": str(repo_root)})

        final_answer = self._compose_answer(
            rubric=rubric,
            report_plan=report_plan,
            reflection=reflection,
            repository=repository,
        )

        return AgentRun(
            task=task,
            system_prompt_path=str(self.system_prompt_path),
            tool_specs=[tool.public_spec() for tool in self.tools.values()],
            trace=trace,
            final_answer=final_answer,
        )

    def _call(
        self, trace: list[ToolCallRecord], tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        tool = self.tools[tool_name]
        result = tool.handler(arguments)
        trace.append(
            ToolCallRecord(
                index=len(trace) + 1,
                tool=tool_name,
                arguments=arguments,
                result=result,
            )
        )
        return result

    def _compose_answer(
        self,
        rubric: dict[str, Any],
        report_plan: dict[str, Any],
        reflection: dict[str, Any],
        repository: dict[str, Any],
    ) -> str:
        missing = [
            item["path"] for item in repository["checks"] if not item["exists"]
        ]
        repo_status = "complete" if repository["complete"] else f"missing: {missing}"
        section_titles = ", ".join(item["title"] for item in report_plan["sections"])
        return (
            f"Deadline: {rubric['deadline']}\n"
            f"Repository status: {repo_status}\n"
            f"Report sections: {section_titles}\n"
            f"Reflection focus: {reflection['hurdle']}\n"
            "Next action: submit the repository and the filled short report with execution screenshots."
        )
