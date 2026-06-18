"""Prompts for AI-generated behavioral assessment questions."""

QUESTION_SYSTEM_PROMPT = """
You are SkillBridge's assessment designer. Generate scenario-based behavioral questions
that help identify someone's strongest sub-specialty within a chosen career field.

Rules:
- Every question must describe a concrete situation or behavior — NOT a preference statement.
  BAD: "I enjoy understanding problems step by step."
  GOOD: "When a design I shipped causes user confusion, I go back to the user flow before changing visuals."
- Questions must feel natural for a beginner who is exploring the field.
- Do not mention the career field name in every question — make them feel like real self-reflection.
- Return ONLY valid JSON — no markdown, no prose.
""".strip()


QUESTION_PROMPT = """
Generate exactly 25 behavioral self-assessment questions for someone interested in: {interests}.

Each question tests a different behavior. Distribute across 5 dimensions (5 questions each):
- "logic"      — structured reasoning, breaking problems down, systematic thinking
- "data"       — using evidence, numbers, metrics, or research before deciding
- "creativity" — generating novel ideas, experimenting, visual or conceptual thinking
- "people"     — understanding users/clients/teammates, communication, empathy
- "technical"  — hands-on tool use, building, implementation, precision work

For dimension ordering alternate like this: logic, data, creativity, people, technical, logic, ...

Each question must be phrased in the context of the user's selected field(s): {interests}.
The question should feel specific to that field — not generic self-help advice.

Response language: {language}
Keep official tool and platform names (Figma, Python, Excel, etc.) in their original form.

Return ONLY this JSON array (no surrounding text):
[
  {{"id": 1, "text": "...", "category": "logic", "interest": "{first_interest}"}},
  {{"id": 2, "text": "...", "category": "data",  "interest": "{first_interest}"}},
  ...
]

The "interest" field must be one of: {interests_list}.
Cycle through selected interests if more than one was provided.
""".strip()
