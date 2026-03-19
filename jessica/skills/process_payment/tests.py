
def test_process_payment():

    from generator import Process_paymentSkill

    skill = Process_paymentSkill()
    result = skill.execute("test")

    assert result is not None
