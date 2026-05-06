from llm.llmSetUp import LLM

from rag.retriever import retriever

def search_code(query: str):
    """
    Search source code, APIs, functions, classes,
    and implementation logic.

    Use for:
    - debugging
    - architecture
    - implementation tracing
    - business logic analysis
    """

    return retriever(query, "code")


def search_records(query: str):
    """
    Search logs, runtime events, failures,
    incidents, and monitoring records.

    Use for:
    - production debugging
    - outages
    - crashes
    - latency investigations
    """

    return retriever(query, "logs")


def search_docs(query: str):
    """
    Search documentation, guides, setup instructions,
    policies, architecture docs, and onboarding material.

    Use for:
    - setup help
    - project explanation
    - technical documentation
    - workflows
    """

    return retriever(query, "docs")


def summarize(query):

    llm = LLM()

    prompt = """
    You are an summarizer

    Use ONLY the provided with data to generate summary of it.

    RULES:
    - Do not hallucinate
    - Be concise
    - If insufficient info exists, say so

    Data:
    {query}

    ANSWER:
    """

    return llm.generate(prompt)
