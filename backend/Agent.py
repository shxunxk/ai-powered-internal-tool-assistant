import json

class Agent:

    def __init__(self, tools, llm=None, task="Perform task demanded by the user"):

        self.llm = llm

        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def run(self, state):

        if self.llm:
            return self._run_reAct(state)

        return self._run_sequential(state)


    def _run_reAct(self, state):

        tool_metadata = []

        for tool in self.tools.values():

            tool_metadata.append({
                "name": tool.name,
                "description": tool.description,
                "args": list(tool.schema.keys())
            })

        prompt = f"""

            Your task:
            {self.task}

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
                "doc_type": "<doc_type>"
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
        doc_type = parsed["doc_type"]

        print("Tool name and Doc type:", tool_name, doc_type)

        selected_tool = self.tools[tool_name]

        state = selected_tool.func(state)

        return state

    def _run_sequential(self, state):

        for _, tool in self.tools.items():

            state = tool.func(state)

        return state