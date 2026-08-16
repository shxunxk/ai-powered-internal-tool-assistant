import json

from sentence_transformers.util import retrieval

class Agent:

    def __init__(self, tools, name, description, llm=None, prompt="Perform task demanded by the user"):

        self.name = name
        self.description = description
        self.llm = llm
        self.tools = {
            tool.name: tool
            for tool in tools
        }
        self.prompt = prompt
        self.retrieved = None

    def run(self, state):

        if self.llm:
            return self._run_reAct(state)

        return self._run_sequential(state)


    def _run_reAct(self, state):

        MAX_STEPS = 10

        for _ in range(MAX_STEPS):

            tool_metadata = [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in self.tools.values()
            ]

            formatted_prompt = self.prompt.format(
                state=json.dumps(state, indent=2),
                tool_metadata=json.dumps(tool_metadata, indent=2)
            )

            response = self.llm.generate(formatted_prompt).strip()

            print("\n========== RESPONSE ==========")
            print(response)

            first = response.find("{")
            last = response.rfind("}")

            if first == -1 or last == -1:
                print("In not found JSON")
                state["history"].append({
                    "type": "error",
                    "content": "LLM did not return JSON",
                    "raw_response": response
                })
                continue

            try:
                parsed = json.loads(
                    response[first:last + 1]
                )
            except json.JSONDecodeError:
                print("In not found JSON correct format")
                state["history"].append({
                    "type": "error",
                    "content": "Invalid JSON from LLM",
                    "raw_response": response
                })
                continue

            # THOUGHT
            thought = parsed.get("thought")

            if not thought:
                print("In not found thought")
                state["history"].append({
                    "type": "error",
                    "content": "Missing thought",
                    "response": parsed
                })
                continue

            state["history"].append({
                "type": "thought",
                "content": thought
            })

            # FINISH
            action = parsed.get("action")
            if action is None:
                print("In not found action")
                state["history"].append({
                    "type": "final",
                    "agent_output": self.retrieved
                })
                state["status"] = "completed"
                return state


            # TOOLS
            tool_name = action.get("tool")

            if not tool_name:
                print("In not found tool")
                state["history"].append({
                    "type": "error",
                    "content": "LLM returned empty tool name",
                    "response": parsed
                })

                continue

            if tool_name not in self.tools:
                print("In not found tool in tool set")
                state["history"].append({
                    "type": "error",
                    "content": f"Unknown tool: {tool_name}",
                    "available_tools": list(self.tools.keys())
                })

                continue

            state["selected_tool"] = tool_name
            state["status"] = "tool_execution"

            tool = self.tools[tool_name]

            self.retrieved = tool.func(state)

            state["history"].append({
                "type": "tool_observation",
                "tool": tool_name,
                "result": self.retrieved
            })
            state["status"] = "agent_execution"

        return state


    def _run_sequential(self, state):
        state["status"] = "agent_execution"

        for _, tool in self.tools.items():
            state["status"] = "tool_execution"
            self.retrieved = tool.func(state)
            state["history"].append({
                "type": "agent_output",
                "tool": tool.name,
                "result": self.retrieved
            })
            state["status"] = "completed"
        return state