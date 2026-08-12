class AgentRegistery:

    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.name] = agent

    def get(self, name):
        return self.agents.get(name)

    def description(self):
        result = {}

        for agent in self.agents:
            print(agent)
            result[agent] = self.agents[agent].description

        return result