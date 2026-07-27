import json

class Agent:

    def __init__(self, tools, llm=None, prompt="Perform task demanded by the user"):

        self.llm = llm
        self.tools = {
            tool.name: tool
            for tool in tools
        }
        self.prompt = prompt

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

            try:
                formatted_prompt = self.prompt.format(
                    state=json.dumps(state, indent=2),
                    tool_metadata=json.dumps(tool_metadata, indent=2)
                )
            except KeyError:
                formatted_prompt = self.prompt

            response = self.llm.generate(formatted_prompt)
            
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