RuleGame — interactive rule-based number transformer

A small, interactive Python CLI that lets you define and combine simple rules
to transform or replace numbers in a numeric range. Rules include swapping
values, replacing specific numbers with text, banning numbers (which ends the
game if triggered), and tagging numbers based on divisibility, odd/even, etc.

This repository contains a single executable script:

- `main.py` — the interactive RuleGame CLI.

Features
- Define rules from built-in patterns or create custom rules interactively.
- Conflict checking prevents logically contradictory or duplicate rules.
- Predefined examples: swap 6↔9, replace 1 → "ewww 1", ban 4, divisible-by-3 → "Fizz", mark odd numbers.
- Adjustable numeric range for each iteration.

Requirements
- Python 3.10 or newer (uses modern typing and dataclasses).

Quick start
1. Open a terminal in this folder.
2. Run:

```bash
python main.py
```

Basic usage
- On first run the game shows the current range (default 1–10) and runs the
  transformation iteration. From the second iteration onward you will be
  presented with a menu to: add a predefined rule, add a custom rule, remove a
  rule, change the range, or run the iteration again.
- Custom rules supported: `swap`, `replace`, `ban`, `divisible`, `odd`, and `even`.
- The game will detect conflicts such as duplicate rules or attempts to target
  banned numbers.

Design notes
- `RuleValue` is a simple value object that carries a number, any applied
  tags, and a banned flag; `render()` returns the textual output (and raises
  if the number is banned).
- `RuleEntry` pairs metadata (kind, params, description) with an executable
  function that mutates `RuleValue`.
- `ConflictChecker` performs lightweight static checks before a rule is added.

Extending
- Add new patterns to the `PATTERNS` mapping in `main.py` and implement a
  corresponding `Rules` factory method for the behavior.

License
- MIT — see LICENSE file if present.

Questions or changes
- If you'd like, I can (a) add a `requirements.txt`/`pyproject.toml`, (b)
  write a few unit tests for rule behaviors, or (c) convert the CLI to an
  argument-driven runner for non-interactive use. Which would you like next?
