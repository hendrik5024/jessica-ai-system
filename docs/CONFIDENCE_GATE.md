# Confidence Gate — Know When to Hold Back

## Overview

The Confidence Gate prevents overconfident responses when the system is uncertain. If confidence falls below a threshold, the response is replaced with a clarification question, option selection, or a graceful deferral.

This reduces hallucinations and makes uncertainty explicit.

## Behavior

**If confidence < threshold:**
- Ask clarification
- Offer options
- Or defer gracefully

**If confidence ≥ threshold:**
- Respond normally

## Integration

The gate is applied in the main response pipeline and the fast path:

- [jessica/agent_loop.py](jessica/agent_loop.py)
- [jessica/meta/confidence_gate.py](jessica/meta/confidence_gate.py)

## Confidence Signal

Confidence uses the same heuristic as MetaObserver:
- Uncertain language lowers confidence
- Confident language raises confidence
- Very short responses reduce confidence
- Using memory gives a small boost

## Example

**User:** “Sort a list”

**Low-confidence response → gated:**

> I want to be accurate here. Which language/runtime should I target?
> Options: Python 3.x, JavaScript/Node, Java, C#, or something else.
> Also, any constraints (framework, OS, performance, format)?

## Tests

Run:
```
pytest test_confidence_gate.py -v
```
