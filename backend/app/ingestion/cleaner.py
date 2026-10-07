import re


class TextCleaner:

    def clean(self, text: str) -> str:

        text = re.sub(r"\n+", "\n", text)

        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()