import json

class Router:

    def __init__(self, agent_registery, llm, prompt):
        self.agent_registery = agent_registery
        self.llm = llm
        self.prompt = prompt


    def route(self, user_input):

        agent_description = self.agent_registery.description()

        formatted_prompt = self.prompt.format(
            agent_description=agent_description,
            user_input=user_input
        )

        result = self.llm.generate(formatted_prompt)

        structured_result = result.json()

        agent_result = structured_result.agent.run()

        return agent_result