import json

class Agent:

    def __init__(self, tools, llm=None):

        self.llm = llm

        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def run(self, query):

        if self.llm:
            return self._run_tool_router(query)

        return self._run_sequential(query)


    def _run_tool_router(self, query):

        tool_metadata = []

        for tool in self.tools.values():

            tool_metadata.append({
                "name": tool.name,
                "description": tool.description,
                "args": tool.schema
            })

        prompt = f"""
            You are an intelligent tool-routing system.

            Your task:
            - Understand the user query
            - Select the SINGLE BEST tool
            - Generate ALL required arguments

            USER QUERY:
            {query}

            AVAILABLE TOOLS:
            {json.dumps(tool_metadata, indent=2)}

            RULES:
            - Return ONLY valid JSON
            - Do NOT explain anything
            - Choose ONLY ONE tool

            OUTPUT FORMAT:

            {{
                "tool": "<tool_name>",
                "args": {{
                    "<arg_name>": "<value>"
                }}
            }}
            """

        response = self.llm.generate(prompt)

        print("\n========== RAW LLM RESPONSE ==========")
        print(response)

        parsed = json.loads(response)

        tool_name = parsed["tool"]

        args = parsed["args"]

        selected_tool = self.tools[tool_name]

        result = selected_tool.func(**args)

        return {
            "selected_tool": tool_name,
            "tool_args": args,
            "result": result
        }

    def _run_sequential(self, query):

        results = {}

        for name, tool in self.tools.items():

            results[name] = tool.func(query=query)

        return results