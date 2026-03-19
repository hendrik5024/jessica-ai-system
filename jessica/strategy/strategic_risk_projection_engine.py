from typing import Optional


class StrategicRiskProjectionEngine:

    def project_risk(
        self,
        drift_level: float
    ) -> Optional[str]:

        if drift_level is None:
            return None

        if drift_level >= 0.7:
            return "High long-term strategic risk if trajectory continues."

        if drift_level >= 0.4:
            return "Moderate strategic risk emerging."

        return None
