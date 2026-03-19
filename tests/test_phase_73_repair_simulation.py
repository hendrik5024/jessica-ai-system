from jessica.stability.self_repair_advisor import RepairRecommendation
from jessica.stability.repair_simulator import RepairSimulator


def test_repair_simulation_projects_stability():
    simulator = RepairSimulator()

    recs = [
        RepairRecommendation(
            issue_detected="drift",
            severity=0.5,
            recommended_action="reset",
            expected_stability_gain=0.3,
        )
    ]

    results = simulator.simulate(0.4, recs)

    assert len(results) == 1
    assert results[0].projected_stability_after > 0.4
