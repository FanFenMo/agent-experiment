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
    parser = argparse.ArgumentParser(description="把 demo trace 渲染成报告截图。")
    parser.add_argument("trace", help="experiment2_run.json 的路径。")
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
            "截图 1：Agent 启动与 tool 注册",
            _startup_lines(data),
        ),
        (
            "截图 2：rubric 提取与报告规划",
            _trace_lines(data, ["read_context", "extract_rubric", "plan_report"]),
        ),
        (
            "截图 3：反思草稿与仓库检查",
            _trace_lines(data, ["draft_reflection", "validate_repository"])
            + ["", "最终答复：", *_final_answer_lines(data)],
        ),
    ]

    for index, (title, lines) in enumerate(pages, start=1):
        image = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((36, 34, WIDTH - 36, HEIGHT - 34), radius=18, fill=PANEL)
        draw.text((72, 70), title, fill=ACCENT, font=font_title)
        draw.text((72, 122), "agent-experiment demo 运行记录", fill=MUTED, font=font_small)
        y = 175
        for line in lines:
            for wrapped in _wrap(line):
                draw.text((82, y), wrapped, fill=TEXT, font=font_body)
                y += 29
            if line == "":
                y += 6
        output_path = output_dir / f"execution_{index}.png"
        image.save(output_path)
        print(output_path)


def _startup_lines(data: dict) -> list[str]:
    lines = [
        "实验交付助手 Agent",
        f"任务：{data['task']}",
        f"系统 prompt：{data['system_prompt_path']}",
        "",
        "已注册 tools：",
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
        lines.append(f"[{item['index']}] tool：{item['tool']}")
        lines.append("参数：")
        lines.extend(_dict_lines(_argument_summary(item)))
        lines.append("结果：")
        lines.extend(_dict_lines(_result_summary(item)))
        lines.append("")
    return lines


def _argument_summary(item: dict) -> dict:
    arguments = item["arguments"].copy()
    if "content" in arguments:
        arguments["content"] = "<rubric markdown 文本>"
    if "rubric" in arguments:
        arguments["rubric"] = "<已解析的 rubric 对象>"
    return arguments


def _result_summary(item: dict) -> dict:
    tool = item["tool"]
    result = item["result"]
    if tool == "read_context":
        return {"路径": result["path"], "字符数": result["characters"]}
    if tool == "extract_rubric":
        return {
            "截止时间": result["deadline"],
            "交付物数量": len(result["deliverables"]),
            "评分项数量": len(result["evaluation"]),
        }
    if tool == "plan_report":
        return {
            "页数限制": result["page_limit"],
            "报告章节": [section["title"] for section in result["sections"]],
        }
    if tool == "draft_reflection":
        return {"困难": result["hurdle"], "解决方式": result["fix"]}
    if tool == "validate_repository":
        return {
            "是否完整": result["complete"],
            "已检查文件数": len(result["checks"]),
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
            line.startswith("报告结构：")
            or line.startswith("反思重点：")
            or line.startswith("下一步：")
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
    return textwrap.wrap(line, width=78, replace_whitespace=False) or [line]


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
        ImageFont.truetype(str(font_path), 23),
        ImageFont.truetype(str(font_path), 20),
    )


if __name__ == "__main__":
    main()
