
def test_analyze_code_quality():

    from generator import Analyze_code_qualitySkill

    skill = Analyze_code_qualitySkill()
    result = skill.execute("test")

    assert result is not None
