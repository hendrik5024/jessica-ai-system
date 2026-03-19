
def test_send_notification():

    from generator import Send_notificationSkill

    skill = Send_notificationSkill()
    result = skill.execute("test")

    assert result is not None
