
def test_update_database():

    from generator import Update_databaseSkill

    skill = Update_databaseSkill()
    result = skill.execute("test")

    assert result is not None
