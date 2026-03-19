from datetime import datetime


class TimeReasoner:
    def __init__(self, belief_store):
        self.beliefs = belief_store

    def get_current_year(self):
        return datetime.now().year

    def calculate_age(self):
        facts = self.beliefs.get_all_facts()

        birth_year = facts.get("birth_year")
        birth_month = facts.get("birth_month")
        birth_day = facts.get("birth_day")

        if not birth_year:
            return None

        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day

        age = current_year - int(birth_year)

        # adjust if birthday hasn't happened yet
        if birth_month and birth_day:
            if (current_month, current_day) < (int(birth_month), int(birth_day)):
                age -= 1
        elif birth_month:
            if current_month < int(birth_month):
                age -= 1

        return age
