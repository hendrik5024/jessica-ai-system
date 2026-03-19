from typing import List, Optional

from .capability_descriptor import CapabilityDescriptor
from .capability_registry import CapabilityRegistry


class CapabilityOrchestrator:

    def __init__(self, registry: CapabilityRegistry):
        self._registry = registry

    def resolve_capability(self, name: str) -> Optional[CapabilityDescriptor]:
        for descriptor in self._registry.list_capabilities():
            if descriptor.name == name:
                return descriptor
        return None

    def list_available_capabilities(self) -> List[CapabilityDescriptor]:
        return self._registry.list_capabilities()

    def provide_capability_metadata(self) -> List[CapabilityDescriptor]:
        return self._registry.registry_snapshot()
