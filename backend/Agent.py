import json

class Agent:

    def __init__(self, tools, llm=None, task="Perform task demanded by the user"):

        self.llm = llm
        self.task = task
        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def run(self, state):

        if self.llm:
            return self._run_reAct(state)

        return self._run_sequential(state)


    def _run_reAct(self, state):

        MAX_STEPS = 5

        for step in range(MAX_STEPS):

            tool_metadata = []

            for tool in self.tools.values():

                tool_metadata.append({
                    "name": tool.name,
                    "description": tool.description
                })

            prompt = f"""
            You are a ReAct retrieval agent.

            TASK:
            {self.task}

            CURRENT STATE:
            {json.dumps(state, indent=2)}

            AVAILABLE TOOLS:
            {json.dumps(tool_metadata, indent=2)}

            RULES:
            - Return ONLY valid JSON
            - No markdown
            - No explanations
            - No text before JSON
            - No text after JSON
            - Your FIRST character MUST be {{
            - Your LAST character MUST be }}

            VALID doc_type VALUES:
            - code
            - docs
            - records

            OUTPUT FORMAT IF RETRIEVAL IS NEEDED:

            {{
                "thought": "...",

                "action": {{
                    "tool": "<tool_name>",
                    "doc_type": "code|docs|records"
                }}
            }}

            OUTPUT FORMAT IF ENOUGH INFORMATION EXISTS:

            {{
                "thought": "...",
                "action": null
            }}
            """

            response = self.llm.generate(prompt)
            
            firstOcc = response.find("{")
            lastOcc = response.rfind("}")

            response = response[firstOcc:lastOcc+1]
            
            print(response)
            parsed = json.loads(response)

            state["history"].append({
                "type": "thought",
                "content": parsed["thought"]
            })
            # STOP CONDITION
            if parsed.get("action") is None:
                return state
            state["doc_type"] = parsed["action"]["doc_type"]
            tool_name = parsed["action"]["tool"]
            tool = self.tools[tool_name]
            state = tool.func(state)

            state["history"].append({
                "type": "observation",
                "tool": tool_name,
                "result": state["tool_outputs"].get(tool_name)
            })

        return state

    def _run_sequential(self, state):

        for _, tool in self.tools.items():

            state = tool.func(state)

        return state