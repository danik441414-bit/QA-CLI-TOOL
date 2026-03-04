from __future__ import annotations

import os
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def enhance_bug_report(bug_path: Path) -> None:
    

    if not bug_path.exists():
        print(f"[AI] Bug file not found: {bug_path}")
        return

    if OpenAI is None:
        print("[AI] openai package not installed. Skipping enhancement.")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[AI] OPENAI_API_KEY not set. Skipping enhancement.")
        return

    try:
        print("[AI] Enhancing bug report with OpenAI...")

        client = OpenAI(api_key=api_key)

        original_text = bug_path.read_text(encoding="utf-8")

        prompt = f"""
You are a Senior QA Engineer.

Rewrite and improve the following bug draft into a professional bug report.

Structure:
- Title
- Environment
- Steps to Reproduce
- Expected Result
- Actual Result
- Additional Notes

Bug draft:
----------------
{original_text}
----------------
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an experienced QA engineer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        improved_text = response.choices[0].message.content

        new_path = bug_path.with_name(bug_path.stem + "_ai.md")
        new_path.write_text(improved_text, encoding="utf-8")

        print(f"[AI] Enhanced bug report saved to: {new_path}")

    except Exception as e:
   
        print(f"[AI] Enhancement failed: {e}")