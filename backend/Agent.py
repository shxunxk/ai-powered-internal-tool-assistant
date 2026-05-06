import json

class Agent:

    def __init__(self, tools, llm=None):

        self.llm = llm

        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def run(self, state):

        if self.llm:
            return self._run_tool_router(state)

        return self._run_sequential(state)


    def _run_tool_router(self, state):

        tool_metadata = []

        for tool in self.tools.values():

            tool_metadata.append({
                "name": tool.name,
                "description": tool.description,
                "args": list(tool.schema.keys())
            })

        prompt = f"""
            You are an intelligent tool-routing system.

            Your task:
            - Understand the user query
            - Select the SINGLE BEST tool
            - Generate ALL required arguments

            CURRENT_STATE:{state}

            AVAILABLE TOOLS:
            {json.dumps(tool_metadata, indent=2)}

            RULES:
            - Return ONLY valid JSON
            - No markdown
            - No code fences
            - args MUST contain ONLY real values from query
            - DO NOT include schema types like <class 'str'>
            - If unsure, infer realistic string values

            OUTPUT FORMAT:

            {{
                "tool": "<tool_name>",
                "args": {{
                    "<arg_name>": "<value>"
                }}
            }}
            """

        response = self.llm.generate(prompt)
        
        if response.startswith("```"):
            response = response.replace("```json", "").replace("```", "").strip()

        print("\n========== RAW LLM RESPONSE ==========")
        print(response)

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            
            import re

            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise Exception(f"Invalid LLM output:\n{response}")

            parsed = json.loads(match.group())

        tool_name = parsed["tool"]

        print("Tool name:", tool_name)

        args = parsed["args"]
        print("Args:", args)

        selected_tool = self.tools[tool_name]

        result = selected_tool.func(**args)

        return {
            "selected_tool": tool_name,
            "tool_args": args,
            "result": result
        }

    def _run_sequential(self, state):

        results = {}

        for name, tool in self.tools.items():

            results[name] = tool.func(query=state.user_query, content=state.curr_data)

        return results