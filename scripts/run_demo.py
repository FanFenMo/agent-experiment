from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_experiment import ExperimentAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="运行实验交付助手 Agent demo。")
    parser.add_argument(
        "--output",
        default="demo_outputs/experiment2_run.json",
        help="JSON execution trace 输出路径。",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="在终端显示完整 tool 参数和结果。",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    agent = ExperimentAgent(repo_root / "prompts" / "system_prompt.md")
    run = agent.run(
        task="根据实验二 rubric 准备代码仓库和实验报告交付物。",
        context_path=repo_root / "context" / "experiment2_rubric.md",
        repo_root=repo_root,
    )

    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(run.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    _print_summary(run, output_path)
    if args.verbose:
        _print_verbose_trace(run)


def _print_summary(run, output_path: Path) -> None:
    rubric = _result_for(run, "extract_rubric")
    plan = _result_for(run, "plan_report")
    repository = _result_for(run, "validate_repository")
    reflection = _result_for(run, "draft_reflection")
    passed = sum(1 for item in repository["checks"] if item["exists"])
    total = len(repository["checks"])
    status = "完成" if repository["complete"] else "需要补充"

    print("实验交付助手 Agent")
    print("=" * 56)
    print(f"运行结果：{status}")
    print(f"截止时间：{rubric['deadline']}")
    print(f"仓库检查：{passed}/{total} 个必需文件已就绪")
    print()
    print("报告结构：")
    for index, section in enumerate(plan["sections"], start=1):
        print(f"  {index}. {section['title']}")
    print()
    print("执行流程：")
    flow_labels = {
        "read_context": "读取实验要求 context",
        "extract_rubric": "提取截止时间、交付物和评分项",
        "plan_report": "规划报告结构",
        "draft_reflection": "生成 AI 使用反思草稿",
        "validate_repository": "检查仓库必需文件",
    }
    for item in run.trace:
        print(f"  [OK] {item.tool}：{flow_labels.get(item.tool, '已执行')}")
    print()
    print("交付物：")
    print("  - 代码仓库：https://github.com/FanFenMo/agent-experiment")
    print("  - 实验报告：reports/综合实践（阶段1）-实验2-实验报告-中文版.docx")
    print("  - 运行截图：reports/assets/execution_1.png ~ execution_3.png")
    print()
    print(f"反思重点：{reflection['hurdle']}")
    print(f"完整 trace：{output_path}")
    print("查看详细 tool 参数：python .\\scripts\\run_demo.py --verbose")


def _print_verbose_trace(run) -> None:
    print()
    print("详细 execution trace")
    print("-" * 56)
    print(f"任务：{run.task}")
    print(f"系统 prompt：{run.system_prompt_path}")
    print()
    print("已注册 tools：")
    for spec in run.tool_specs:
        print(f"- {spec['name']}: {spec['description']}")
    print()
    for item in run.trace:
        print(f"[{item.index}] {item.tool}")
        print(f"    参数：{json.dumps(item.arguments, ensure_ascii=False)}")
        compact_result = _compact(item.result)
        print(f"    结果：{json.dumps(compact_result, ensure_ascii=False)}")


def _result_for(run, tool_name: str) -> dict:
    for item in run.trace:
        if item.tool == tool_name:
            return item.result
    raise ValueError(f"没有找到 tool 结果：{tool_name}")


def _compact(value):
    if isinstance(value, dict):
        return {key: _compact(item) for key, item in value.items() if key != "content"}
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


if __name__ == "__main__":
    main()
