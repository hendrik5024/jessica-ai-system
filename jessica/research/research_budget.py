class ResearchBudgetController:
    """Compute governor for autonomous research loops."""

    def __init__(self, max_experiments: int = 50, max_failures: int = 20) -> None:
        self.max_experiments = max_experiments
        self.max_failures = max_failures

        self.experiment_count = 0
        self.failure_count = 0

    def allow_experiment(self) -> bool:

        if self.experiment_count >= self.max_experiments:
            return False

        if self.failure_count >= self.max_failures:
            return False

        return True

    def record_result(self, success: bool) -> None:

        self.experiment_count += 1

        if not success:
            self.failure_count += 1
