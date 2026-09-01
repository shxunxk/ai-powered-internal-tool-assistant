from dataclasses import dataclass, field
from llm.llmSetUp import LLM

llm = LLM()

@dataclass

class PIIDetector:
    """
    A class to detect potential Personally Identifiable Information (PII) in a given text.
    """

    def __init__(self, text):
        global llm
        self.text = text
        self.llm = llm

    def detect_pii(self) -> bool:
        """
        Detects potential PII in the provided text.
        Returns True if PII is detected, otherwise False.
        """
        check_prompt = f"Please analyze the following text for potential Personally Identifiable Information (PII): {self.text}. If it contains PII, return 'yes'. If it does not, return 'no'."
        response = self.llm.generate(check_prompt)

        if "yes" in response.lower():
            return True
        else:
            return False