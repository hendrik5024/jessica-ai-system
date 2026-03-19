from typing import Optional


class MultiHorizonConsistencyEngine:

    def evaluate(
        self,
        short_term: str,
        mid_term: str,
        long_term: str
    ) -> Optional[str]:

        if not short_term or not mid_term or not long_term:
            return None

        if short_term not in mid_term or mid_term not in long_term:
            return (
                "Warning: potential strategic inconsistency detected "
                "between short, mid, and long-term directions."
            )

        return None
