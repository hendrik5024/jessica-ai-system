
def test_test_install():

    from generator import Test_installSkill

    skill = Test_installSkill()
    result = skill.execute("test")

    assert result is not None
