from typing import Dict, Optional
from datetime import datetime

from .knowledge_module_record import KnowledgeModuleRecord


class KnowledgeRegistry:
    def __init__(self):
        self._modules: Dict[str, KnowledgeModuleRecord] = {}

    def register_module(self, module_name: str, proposal_id: str):
        record = KnowledgeModuleRecord(
            module_name=module_name,
            installed_from_proposal=proposal_id,
            registered_at=datetime.utcnow(),
        )
        self._modules[module_name] = record
        return record

    def get_module(self, module_name: str) -> Optional[KnowledgeModuleRecord]:
        return self._modules.get(module_name)

    def list_modules(self):
        return list(self._modules.values())
