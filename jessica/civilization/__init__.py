"""Internal Civilization: Society of Specialized Minds

Jessica is not a single intelligence with tools.
She is a governed society of persistent specialized intelligences.

Each mind has:
- Independent viewpoint & judgment
- Right to object & escalate
- Voice in institutional memory
- Standing in council arbitration
"""

from jessica.civilization.civilization_core import (
    Mind,
    Viewpoint,
    Objection,
    CouncilSession,
    InstitutionalMemory,
)
from jessica.civilization.internal_council import InternalCourt

__all__ = [
    "Mind",
    "Viewpoint",
    "Objection",
    "CouncilSession",
    "InstitutionalMemory",
    "InternalCourt",
]
