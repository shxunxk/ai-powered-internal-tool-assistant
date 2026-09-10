from dataclasses import dataclass, field
from llm.llmSetUp import LLM

llm = LLM()

@dataclass
class CodeCompromiseDetector:
    """
    A class to detect potential code compromise in a given text.
    """

    def __init__(self, text):
        global llm
        self.text = text
        self.llm = llm

    def detect_code_compromise(self) -> bool:
        """
        Detects potential code compromise in the provided text.
        Returns True if code compromise is detected, otherwise False.
        """
        check_prompt = f"Please analyze the following text for potential code compromise: {self.text}. If it contains code compromise, return 'yes'. If it does not, return 'no'."
        response = self.llm.generate(check_prompt)

        if "yes" in response.lower():
            return True
        else:
            return False