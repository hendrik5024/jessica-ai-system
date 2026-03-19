from enum import Enum
from dataclasses import dataclass
from typing import Dict


class OperationalMode(Enum):
    ASSISTANT = "assistant"
    COLLABORATOR = "collaborator"
    STRATEGIST = "strategist"
    SANDBOXED_AUTONOMOUS = "sandboxed_autonomous"


@dataclass
class ModeCapabilities:
    can_execute: bool
    can_propose_goals: bool
    can_long_horizon_plan: bool
    can_self_improve: bool
    initiative_level: int  # 0 = reactive, 1 = suggestive, 2 = analytical, 3 = proactive


class ModeController:
    def __init__(self):
        self._mode = OperationalMode.ASSISTANT
        self._capability_map = self._initialize_capabilities()

    def _initialize_capabilities(self) -> Dict[OperationalMode, ModeCapabilities]:
        return {
            OperationalMode.ASSISTANT: ModeCapabilities(
                can_execute=True,
                can_propose_goals=False,
                can_long_horizon_plan=False,
                can_self_improve=False,
                initiative_level=0,
            ),
            OperationalMode.COLLABORATOR: ModeCapabilities(
                can_execute=True,
                can_propose_goals=True,
                can_long_horizon_plan=False,
                can_self_improve=False,
                initiative_level=1,
            ),
            OperationalMode.STRATEGIST: ModeCapabilities(
                can_execute=True,
                can_propose_goals=True,
                can_long_horizon_plan=True,
                can_self_improve=False,
                initiative_level=2,
            ),
            OperationalMode.SANDBOXED_AUTONOMOUS: ModeCapabilities(
                can_execute=True,
                can_propose_goals=True,
                can_long_horizon_plan=True,
                can_self_improve=True,
                initiative_level=3,
            ),
        }

    def set_mode(self, mode: OperationalMode):
        self._mode = mode

    def get_mode(self) -> OperationalMode:
        return self._mode

    def get_capabilities(self) -> ModeCapabilities:
        return self._capability_map[self._mode]
