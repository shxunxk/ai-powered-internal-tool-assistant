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
    You are a ReAct AI agent.

    TASK:
    {self.task}

    CURRENT STATE:
    {json.dumps(state, indent=2)}

    AVAILABLE TOOLS:
    {json.dumps(tool_metadata, indent=2)}

    You can:
    - think step-by-step
    - use tools
    - observe results
    - continue reasoning

    Return ONLY valid JSON.

    IF MORE INFORMATION IS NEEDED:

    {{
        "thought": "...",

        "action": {{
            "tool": "<tool_name>",
            "doc_type": "<document_type>"
        }},

        "final_answer": null
    }}

    IF ENOUGH INFORMATION EXISTS:

    {{
        "thought": "...",

        "action": null,

        "final_answer": "..."
    }}
    """

            response = self.llm.generate(prompt)

            parsed = json.loads(response)

            state["history"].append({
                "type": "thought",
                "content": parsed["thought"]
            })

            # STOP CONDITION
            if parsed["final_answer"]:
                state["final_answer"] = parsed["final_answer"]
                return state

            tool_name = parsed["action"]["tool"]

            tool = self.tools[tool_name]

            state = tool.func(state)

            state["history"].append({
                "type": "observation",
                "tool": tool_name,
                "result": state["tool_outputs"].get(tool_name)
            })

        state["final_answer"] = "Max steps exceeded"

        return state

    def _run_sequential(self, state):

        for _, tool in self.tools.items():

            state = tool.func(state)

        return state