
def test_test_skill():

    from generator import Test_skillSkill

    skill = Test_skillSkill()
    result = skill.execute("test")

    assert result is not None
