
def test_create_dashboard_widget():

    from generator import Create_dashboard_widgetSkill

    skill = Create_dashboard_widgetSkill()
    result = skill.execute("test")

    assert result is not None
