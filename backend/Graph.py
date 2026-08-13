class Graph:

    def __init__(self, agent_registery):
        self.nodes = {"start":"end", "end":None}
        self.agent_registery = agent_registery

    def addEdge(self, source, destination):
        if(source in self.nodes.keys()):
            self.nodes[source] = destination
        else:
            print("Error1")

    def addConditionalEdges(self, source, decision_function):
        if(source in self.nodes.keys()):
            self.nodes[source] = decision_function
        else:
            print("Error2")

    def addNode(self, node):
        self.nodes[node] = None
    
    def start(self, state):
        node = "start"
        while node != "end":
            next_node = self.nodes[node]

            if callable(next_node):
                node = next_node(state)
                continue
            
            state["status"] = "agent_execution"

            state["messages"].append({
                    "role": "router",
                    "selected_agent": node
                })

            agent = self.agent_registery.get(node)

            if agent is None:
                raise ValueError(f"Agent '{node}' not found")

            state = agent.run(state)
            if(node == "end" or node == None):
                state["status"] = "complete"
                break
            state["status"] = "routing"
            node = next_node
        return state