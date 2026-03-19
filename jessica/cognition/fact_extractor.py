import re


class FactExtractor:

    def extract(self, user_input):

        text = user_input.lower()

        # Birthplace detection
        birthplace_match = re.search(r"born in ([a-zA-Z\s]+)", text)

        if birthplace_match:

            place = birthplace_match.group(1).strip().title()

            return ("birthplace", place)

        # Birth year detection
        year_match = re.search(r"\b(19|20)\d{2}\b", text)

        if "born" in text and year_match:

            return ("birth_year", year_match.group())

        return None
