# Personality Inertia — Drift Control

## Overview

Personality Inertia prevents sudden cross-session shifts in Jessica’s personality state (beliefs, desires, intentions). Changes must appear consistently across multiple sessions before being accepted.

This makes evolution slow, explainable, and stable — a “psychological versioning” system.

## How It Works

- The current desire state is loaded from disk
- Inertia compares it to the last confirmed state
- If it differs, the change is staged as **pending**
- The same change must be seen **N times** (default: 3)
- Only then is it accepted and the **version** increments

## Key Properties

- **Multiple confirmations required** (default: 3)
- **Sudden shifts dampened** (pending changes do not affect behavior)
- **Explainable versioning** (each accepted change bumps a version number)

## Files

- [jessica/meta/personality_inertia.py](jessica/meta/personality_inertia.py)
- [jessica/personality.py](jessica/personality.py)

## Configuration

Threshold can be adjusted when constructing `PersonalityInertia`:

```python
PersonalityInertia(threshold=4)
```

## Status API

```python
status = personality.inertia_status()
# {
#   "version": 2,
#   "threshold": 3,
#   "pending_count": 1,
#   "pending_since": 1738540000,
#   "has_pending": True
# }
```

## Tests

Run:
```
pytest test_personality_inertia.py -v
```
