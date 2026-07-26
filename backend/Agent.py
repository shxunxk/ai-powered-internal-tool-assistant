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
        i = 0

        while i<MAX_STEPS:

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

            OUTPUT FORMAT IF RETRIEVAL IS NEEDED:

            {{
                "thought": "...",

                "action": {{
                    "tool": "<tool_name>",
                }}
            }}

            OUTPUT FORMAT IF ENOUGH INFORMATION EXISTS:

            {{
                "thought": "...",
                "action": null
            }}

            IMPORTANT:
            You must generate ONLY ONE reasoning step.
            ONLY ONE final JSON OBJECT with both 'thought' and 'action' arguments inside it. Do not generate multiple
            JSON objects. ALL ARGUMENTS MUST BE GENERATED. ONLY GENERATE A VALUE FOR THE ARGUMENTS NO EXTRA DATA OR 
            EXPLAINATION FOR IT IS TO BE GIVEN.

            Do NOT simulate future iterations.
            Do NOT generate multiple JSON objects.
            Do NOT continue reasoning after choosing one action.

            The Python runtime will call you again with updated state.
            """

            response = self.llm.generate(prompt)
            
            firstOcc = response.find("{")
            lastOcc = response.rfind("}")

            response = response[firstOcc:lastOcc+1]

            print(response)
            parsed = json.loads(response)

            if(parsed.get("thought") is None):
                continue

            state["history"].append({
                "type": "thought",
                "content": parsed["thought"]
            })
            # STOP CONDITION
            if parsed.get("action") is None:
                return state
            
            tool_name = parsed["action"]["tool"]
            tool = self.tools[tool_name]
            state = tool.func(state)

            state["history"].append({
                "type": "observation",
                "tool": tool_name,
                "result": state["tool_outputs"].get(tool_name)
            })

            i=i+1

        return state

    def _run_sequential(self, state):

        for _, tool in self.tools.items():

            state = tool.func(state)

        return state