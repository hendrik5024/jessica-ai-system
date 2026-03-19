
def test_deploy_container():

    from generator import Deploy_containerSkill

    skill = Deploy_containerSkill()
    result = skill.execute("test")

    assert result is not None
