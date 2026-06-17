from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_experiment import ExperimentAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Experiment Delivery Agent demo.")
    parser.add_argument(
        "--output",
        default="demo_outputs/experiment2_run.json",
        help="Path for the JSON execution trace.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    agent = ExperimentAgent(repo_root / "prompts" / "system_prompt.md")
    run = agent.run(
        task="Use the Experiment 2 rubric to prepare code and report deliverables.",
        context_path=repo_root / "context" / "experiment2_rubric.md",
        repo_root=repo_root,
    )

    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(run.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Experiment Delivery Agent")
    print("=" * 72)
    print(f"Task: {run.task}")
    print(f"System prompt: {run.system_prompt_path}")
    print()
    print("Registered tools:")
    for spec in run.tool_specs:
        print(f"- {spec['name']}: {spec['description']}")
    print()
    print("Execution trace:")
    for item in run.trace:
        print(f"[{item.index}] {item.tool}")
        print(f"    arguments: {json.dumps(item.arguments, ensure_ascii=False)}")
        compact_result = _compact(item.result)
        print(f"    result: {json.dumps(compact_result, ensure_ascii=False)}")
    print()
    print("Final answer:")
    print(run.final_answer)
    print()
    print(f"Saved trace: {output_path}")


def _compact(value):
    if isinstance(value, dict):
        return {key: _compact(item) for key, item in value.items() if key != "content"}
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


if __name__ == "__main__":
    main()
