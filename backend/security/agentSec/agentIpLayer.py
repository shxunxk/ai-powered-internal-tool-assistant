from llmOps.guardrails.propmtInjectionAndJailbreakDetector import PromptInjectionAndJailbreakDetector
from llmOps.guardrails.personalIdentifiableInformation import PIIDetector
from llmOps.guardrails.codeCompriseDetector import CodeCompromiseDetector

def detect_ip_security_issues(text):
    """
    Detects potential security issues in the provided text.
    Returns a dictionary indicating the presence of PII, code compromise, and prompt injection/jailbreak attempts.
    """
    pii_detector = PIIDetector(text)
    code_compromise_detector = CodeCompromiseDetector(text)
    prompt_injection_detector = PromptInjectionAndJailbreakDetector(text)

    return {
        "contains_pii": pii_detector.detect_pii(),
        "contains_code_compromise": code_compromise_detector.detect_code_compromise(),
        "contains_prompt_injection_or_jailbreak": prompt_injection_detector.detect_prompt_injection_or_jailbreak()
    }