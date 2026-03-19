from datetime import datetime, timedelta
from jessica.self_improvement import ImprovementScheduler


def test_improvement_schedule():
    scheduler = ImprovementScheduler()

    record = scheduler.schedule(
        proposal_id="proposal_100",
        when=datetime.utcnow() + timedelta(days=1),
    )

    assert record.proposal_id == "proposal_100"
    assert len(scheduler.list_schedule()) == 1
