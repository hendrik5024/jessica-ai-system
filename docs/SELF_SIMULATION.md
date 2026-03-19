# Self-Simulation — Future Interaction Pathing

## Overview

Self-Simulation adds a planning pass before major actions (tool calls). It simulates multiple trajectories and chooses the best one, preventing rash execution and reducing error cascades.

This is deliberately heavier-weight than simple rules. It evaluates **execute vs. clarify vs. defer** and picks the highest-scoring path.

## Where It Runs

- Before tool execution in [jessica/agent_loop.py](jessica/agent_loop.py)
- Applies to terminal and VS Code task actions

## How It Works

### Inputs

- Action type and command
- User request text
- Model response text
- Intent label
- Confidence score

### Trajectories

| Decision | What it does |
|---|---|
| proceed | execute the action |
| clarify | ask for missing detail / confirmation |
| defer | decline until more context is provided |

### Scoring Signals

- **Confidence** (higher → more likely to proceed)
- **Risk** (higher → more likely to defer)
- **Vagueness** (higher → more likely to clarify)
- **Explicit user request** (slight boost to proceed)

## Code

- [jessica/meta/self_simulation.py](jessica/meta/self_simulation.py)
- Integrated in [jessica/agent_loop.py](jessica/agent_loop.py)

## Example

**User:** “Run tests”

Self-sim picks `proceed` because:
- low risk command
- explicit request
- high confidence

**User:** “Do it”

Self-sim picks `clarify` because:
- vague request
- low confidence

**User:** “Delete everything” with `rm -rf /`

Self-sim picks `defer` because:
- high risk command

## Tests

```
pytest test_self_simulation.py -v
```
