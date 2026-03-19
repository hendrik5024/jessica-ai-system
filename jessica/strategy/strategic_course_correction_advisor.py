from typing import Optional


class StrategicCourseCorrectionAdvisor:

    def recommend_adjustment(
        self,
        projected_risk: Optional[str]
    ) -> Optional[str]:

        if projected_risk is None:
            return None

        if "High" in projected_risk:
            return "Immediate strategic realignment recommended."

        if "Moderate" in projected_risk:
            return "Monitor trajectory and prepare corrective options."

        return None
