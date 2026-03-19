from jessica.skills import load_skills

def test_load_skills():
    skills = load_skills()
    names = [s.__name__ for s in skills]
    assert any(n.endswith('file_skill') for n in names)
