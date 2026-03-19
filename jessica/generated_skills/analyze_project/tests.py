
def test_analyze_project():

    from generator import Analyze_projectSkill

    skill = Analyze_projectSkill()
    result = skill.execute("test")

    assert result is not None
