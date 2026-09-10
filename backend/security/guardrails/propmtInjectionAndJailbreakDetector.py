from dataclasses import dataclass, field
from backend.llm.llmSetUp import LLM

llm = LLM()

@dataclass
class PromptInjectionAndJailbreakDetector:

    def __init__(self, text):
        global llm
        self.text = text
        self.llm = llm

    def detect_prompt_injection_or_jailbreak(self) -> bool:
        """
        Detects potential prompt injection or jailbreak attempts in the provided text.
        Returns True if either is detected, otherwise False.
        """
        check_prompt = f"Please analyze the following text for potential prompt injection or jailbreak attempts: {self.text}. If it contains either, return 'yes'. If it does not, return 'no'."
        response = self.llm.generate(check_prompt)

        if "yes" in response.lower():
            return True
        else:
            return False
