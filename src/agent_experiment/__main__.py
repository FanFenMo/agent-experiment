from __future__ import annotations

from pathlib import Path

from .agent import ExperimentAgent


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    agent = ExperimentAgent(repo_root / "prompts" / "system_prompt.md")
    run = agent.run(
        task="Plan and verify Experiment 2 deliverables.",
        context_path=repo_root / "context" / "experiment2_rubric.md",
        repo_root=repo_root,
    )
    print(run.final_answer)


if __name__ == "__main__":
    main()
