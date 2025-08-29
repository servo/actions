#!/usr/bin/env python3

import os
import subprocess
import json
import sys
import shlex
from typing import Any


def normalize_path(path: str) -> str:
    return path.removeprefix("./")


def parse_cargo_output(results: list[dict[str, Any]], with_annotation: bool) -> bool:
    total_count = 0
    limit = 10

    severenty_map = {
        "help": "notice",
        "note": "notice",
        "warning": "warning",
        "error": "error",
    }
    for item in results:
        if total_count >= limit:
            break

        message = item.get("message")
        if not message:
            continue

        spans = message.get("spans") or []
        primary_span = next((span for span in spans if span.get("is_primary")), None)
        if not primary_span:
            continue

        level = severenty_map.get(message.get("level"), "error")
        title = message.get("message", "")
        rendered_message = message.get("rendered", "")

        file_name = normalize_path(primary_span["file_name"])
        line_start = primary_span["line_start"]
        line_end = primary_span["line_end"]
        column_start = primary_span["column_start"]
        column_end = primary_span["column_end"]

        line_info = f"line={line_start},endLine={line_end},title={title}"

        column_info = ""
        if (
            line_start == line_end
            and column_end is not None
            and column_start is not None
        ):
            column_info = f"col={column_start},endColumn={column_end},"
        if with_annotation:
            print(
                f"::{level} file={file_name},{column_info}{line_info}::{rendered_message}"
            )
        total_count += 1

    return total_count > 0


def main():
    cmd = ["cargo"]

    cargo_command = os.getenv("INPUT_CARGO_COMMAND", "").strip()
    with_annotation = (
        os.getenv("INPUT_WITH_ANNOTATION", "true").strip().lower() == "true"
    )

    if cargo_command:
        args = shlex.split(cargo_command)
        cmd.extend(args)

    if "--message-format=json" not in cmd:
        cmd.append("--message-format=json")

    proc = subprocess.run(cmd, capture_output=True)
    clippy_results = [
        json.loads(line) for line in proc.stdout.splitlines() if line.strip()
    ]

    result = parse_cargo_output(clippy_results, with_annotation)
    sys.exit(int(result))


if __name__ == "__main__":
    main()
