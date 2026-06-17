from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1400
HEIGHT = 880
BG = (18, 24, 33)
PANEL = (29, 38, 52)
TEXT = (232, 238, 247)
MUTED = (148, 163, 184)
ACCENT = (86, 204, 157)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render demo trace into report screenshots.")
    parser.add_argument("trace", help="Path to experiment2_run.json.")
    parser.add_argument("--output-dir", default="reports/assets")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    trace_path = (repo_root / args.trace).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(trace_path.read_text(encoding="utf-8"))
    font_title, font_body, font_small = _fonts()

    pages = [
        (
            "Screenshot 1 - Agent startup and registered tools",
            _startup_lines(data),
        ),
        (
            "Screenshot 2 - Rubric extraction and report planning",
            _trace_lines(data, ["read_context", "extract_rubric", "plan_report"]),
        ),
        (
            "Screenshot 3 - Reflection drafting and repository validation",
            _trace_lines(data, ["draft_reflection", "validate_repository"])
            + ["", "Final answer:", *_final_answer_lines(data)],
        ),
    ]

    for index, (title, lines) in enumerate(pages, start=1):
        image = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((36, 34, WIDTH - 36, HEIGHT - 34), radius=18, fill=PANEL)
        draw.text((72, 70), title, fill=ACCENT, font=font_title)
        draw.text((72, 122), "agent-experiment demo run", fill=MUTED, font=font_small)
        y = 175
        for line in lines:
            for wrapped in _wrap(line):
                draw.text((82, y), wrapped, fill=TEXT, font=font_body)
                y += 34
            if line == "":
                y += 10
        output_path = output_dir / f"execution_{index}.png"
        image.save(output_path)
        print(output_path)


def _startup_lines(data: dict) -> list[str]:
    lines = [
        "Experiment Delivery Agent",
        f"Task: {data['task']}",
        f"System prompt: {data['system_prompt_path']}",
        "",
        "Registered tools:",
    ]
    lines.extend(
        f"- {tool['name']}: {tool['description']}" for tool in data["tool_specs"]
    )
    return lines


def _trace_lines(data: dict, names: list[str]) -> list[str]:
    lines: list[str] = []
    for item in data["trace"]:
        if item["tool"] not in names:
            continue
        lines.append(f"[{item['index']}] tool: {item['tool']}")
        lines.append("arguments:")
        lines.extend(_dict_lines(_argument_summary(item)))
        lines.append("result:")
        lines.extend(_dict_lines(_result_summary(item)))
        lines.append("")
    return lines


def _argument_summary(item: dict) -> dict:
    arguments = item["arguments"].copy()
    if "content" in arguments:
        arguments["content"] = "<rubric markdown text>"
    if "rubric" in arguments:
        arguments["rubric"] = "<parsed rubric object>"
    return arguments


def _result_summary(item: dict) -> dict:
    tool = item["tool"]
    result = item["result"]
    if tool == "read_context":
        return {"path": result["path"], "characters": result["characters"]}
    if tool == "extract_rubric":
        return {
            "deadline": result["deadline"],
            "deliverables": len(result["deliverables"]),
            "evaluation_items": len(result["evaluation"]),
        }
    if tool == "plan_report":
        return {
            "page_limit": result["page_limit"],
            "sections": [section["title"] for section in result["sections"]],
        }
    if tool == "draft_reflection":
        return {"hurdle": result["hurdle"], "fix": result["fix"]}
    if tool == "validate_repository":
        return {
            "complete": result["complete"],
            "checked_files": len(result["checks"]),
        }
    return result


def _dict_lines(data: dict) -> list[str]:
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        lines.append(f"  {key}: {_clip(str(value))}")
    return lines


def _final_answer_lines(data: dict) -> list[str]:
    lines = []
    for line in data["final_answer"].splitlines():
        if (
            line.startswith("Report sections:")
            or line.startswith("Reflection focus:")
            or line.startswith("Next action:")
        ):
            continue
        lines.append(line)
    return lines


def _clip(value: str, limit: int = 42) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _wrap(line: str) -> list[str]:
    if not line:
        return [""]
    return textwrap.wrap(line, width=72, replace_whitespace=False) or [line]


def _fonts():
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/CascadiaMono.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    font_path = next(path for path in candidates if path.exists())
    return (
        ImageFont.truetype(str(font_path), 34),
        ImageFont.truetype(str(font_path), 25),
        ImageFont.truetype(str(font_path), 20),
    )


if __name__ == "__main__":
    main()
