from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KnowledgeModuleRecord:
    module_name: str
    installed_from_proposal: str
    registered_at: datetime
