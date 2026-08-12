class AgentRegistry:

    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.name] = agent.description

    def get(self, name):
        return self.agents.get(name)

    def descriptions(self):
        return {
            name: agent.description()
            for name, agent in self.agents.items()
        }