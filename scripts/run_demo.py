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

    print("实验交付助手 Agent")
    print("=" * 72)
    print(f"任务：{run.task}")
    print(f"系统 prompt：{run.system_prompt_path}")
    print()
    print("已注册 tools：")
    for spec in run.tool_specs:
        print(f"- {spec['name']}: {spec['description']}")
    print()
    print("执行 trace：")
    for item in run.trace:
        print(f"[{item.index}] {item.tool}")
        print(f"    参数：{json.dumps(item.arguments, ensure_ascii=False)}")
        compact_result = _compact(item.result)
        print(f"    结果：{json.dumps(compact_result, ensure_ascii=False)}")
    print()
    print("最终答复：")
    print(run.final_answer)
    print()
    print(f"trace 已保存：{output_path}")


def _compact(value):
    if isinstance(value, dict):
        return {key: _compact(item) for key, item in value.items() if key != "content"}
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


if __name__ == "__main__":
    main()
