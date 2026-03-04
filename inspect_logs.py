#!/usr/bin/env python3
"""Quick local analysis for captured request logs."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, List


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _body_text_len(body: Dict[str, Any]) -> int:
    if body.get("encoding") == "utf-8":
        text = body.get("text", "")
        if isinstance(text, str):
            return len(text)
    if body.get("encoding") == "base64":
        b64 = body.get("base64", "")
        if isinstance(b64, str):
            return len(b64)
    return 0


def _extract_openai_input_chars(body_text: str) -> int:
    try:
        payload = json.loads(body_text)
    except Exception:
        return 0

    total = 0

    def walk(node: Any) -> None:
        nonlocal total
        if isinstance(node, str):
            total += len(node)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for _, value in node.items():
                walk(value)

    for key in ("input", "messages", "prompt"):
        if key in payload:
            walk(payload[key])

    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze LLM capture request logs")
    parser.add_argument("--log-dir", default="logs", help="Log directory root")
    parser.add_argument("--top", type=int, default=10, help="Top N requests to show")
    args = parser.parse_args()

    req_dir = pathlib.Path(args.log_dir) / "requests"
    if not req_dir.exists():
        raise SystemExit(f"No request directory: {req_dir}")

    rows: List[Dict[str, Any]] = []
    for path in req_dir.glob("*.json"):
        rec = _load_json(path)
        body = rec.get("body", {})
        body_len = _body_text_len(body)
        body_text = body.get("text", "") if isinstance(body, dict) else ""
        input_chars = _extract_openai_input_chars(body_text) if isinstance(body_text, str) else 0
        rows.append(
            {
                "file": str(path),
                "timestamp": rec.get("timestamp"),
                "method": rec.get("method"),
                "url": rec.get("url"),
                "body_chars": body_len,
                "input_chars_estimate": input_chars,
            }
        )

    rows.sort(key=lambda r: (r["input_chars_estimate"], r["body_chars"]), reverse=True)

    print(f"Total captured requests: {len(rows)}")
    print()
    for i, row in enumerate(rows[: args.top], start=1):
        print(f"[{i}] {row['timestamp']} {row['method']} {row['url']}")
        print(f"    input_chars_estimate={row['input_chars_estimate']} body_chars={row['body_chars']}")
        print(f"    file={row['file']}")


if __name__ == "__main__":
    main()
