class Agent:
    def __init__(self, llm = None, tools) -> None:
        self.llm = llm
        self.tools = tools