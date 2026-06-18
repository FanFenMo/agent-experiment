from __future__ import annotations

import unittest
from pathlib import Path

from agent_experiment import ExperimentAgent
from agent_experiment.tools import extract_rubric


ROOT = Path(__file__).resolve().parents[1]


class RubricToolTests(unittest.TestCase):
    def test_extract_rubric_reads_scoring_items(self) -> None:
        content = (ROOT / "context" / "experiment2_rubric.md").read_text(
            encoding="utf-8"
        )
        rubric = extract_rubric({"content": content})

        self.assertEqual(rubric["deadline"], "2026/06/20 23:59:59")
        self.assertEqual(len(rubric["deliverables"]), 2)
        self.assertEqual(len(rubric["evaluation"]), 3)
        self.assertIn("具体技术困难", rubric["reflection_requirement"])


class AgentRunTests(unittest.TestCase):
    def test_agent_records_tool_trace(self) -> None:
        agent = ExperimentAgent(ROOT / "prompts" / "system_prompt.md")
        run = agent.run(
            task="准备实验交付物。",
            context_path=ROOT / "context" / "experiment2_rubric.md",
            repo_root=ROOT,
        )

        self.assertEqual([item.tool for item in run.trace], [
            "read_context",
            "extract_rubric",
            "plan_report",
            "draft_reflection",
            "validate_repository",
        ])
        self.assertIn("截止时间：2026/06/20 23:59:59", run.final_answer)


if __name__ == "__main__":
    unittest.main()
