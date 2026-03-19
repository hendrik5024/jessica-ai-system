from typing import Dict, List

from .capability_descriptor import CapabilityDescriptor


class CapabilityRegistry:

    def __init__(self):
        self._descriptors: Dict[str, CapabilityDescriptor] = {}
        self._order: List[str] = []

    def register_capability(self, descriptor: CapabilityDescriptor) -> None:
        if descriptor.capability_id in self._descriptors:
            return
        self._descriptors[descriptor.capability_id] = descriptor
        self._order.append(descriptor.capability_id)

    def get_capability(self, capability_id: str):
        return self._descriptors.get(capability_id)

    def list_capabilities(self) -> List[CapabilityDescriptor]:
        return [self._descriptors[cid] for cid in self._order]

    def capability_exists(self, capability_id: str) -> bool:
        return capability_id in self._descriptors

    def registry_snapshot(self) -> List[CapabilityDescriptor]:
        return list(self.list_capabilities())
