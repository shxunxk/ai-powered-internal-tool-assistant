from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize
from llmOps.prompts import prompt_registry
from router.agent_registery import AgentRegistery
from router.router_setup import Router
from Graph import Graph
import json    

if __name__ == "__main__":

# state initialization
    state = {
    "user_query": None,
    "history": [],
    "tool_outputs": {},
    "selected_tool": None,
    "context": None,
    "final_answer": None,
    "messages": [],
    "status": "routing"
    }

    #Instances

    llm = LLM()
    agent_registery = AgentRegistery()
    graph = Graph(agent_registery)


    # Tools for agnets
    docs_agent_tools = [
        Tool(search_docs),
    ]
    
    codebase_agent_tools = [
        Tool(search_code),
    ]

    records_agent_tools = [
        Tool(search_records),
    ]
    # summarize_agent_tools = [
    #     Tool(summarize)
    # ]
    # policy_agent_tools = [
    #     Tool(search_policy),
    #     Tool(summarize)
    # ]


    # Agent registery
    agent_registery.register(Agent(
        tools=docs_agent_tools,
        name = "docs_agent", 
        description="Retrieves and analyzes information from internal documents, policies, manuals, and knowledge bases.",
        llm=llm,
        prompt = prompt_registry.get_prompt("agent_reasoning"),
    ))

    agent_registery.register(Agent(
        tools=codebase_agent_tools,
        name = "codebase_agent",
        description = "Searches, analyzes, and explains source code, software architecture, implementations, dependencies, and code-related issues.",
        llm=llm,
        prompt = prompt_registry.get_prompt("agent_reasoning"),
        ))

    agent_registery.register(Agent(
        tools = records_agent_tools,
        name = "records_agent",
        description="Searches, analyzes, and explains incidents, events, logs and metrics.",
        llm = llm,
        prompt = prompt_registry.get_prompt("agent_reasoning"),
    ))

    # agent_registery.register(Agent(
    #     tools = summarize_agent_tools,
    #     name = "summarize_agent",
    #     description="Retrieves and summarizes structured records and data, including user, business, transactional, or system records.",
    #     prompt = prompt_registry.get_prompt("agent_summary"),
    # ))

    # policy_agent = Agent(
    #     tools = policy_agent_tools,
    #     prompt = prompt_registry.get_prompt("")
    # )



    # router = Router(
    #     agent_registery=agent_registery,
    #     llm=llm,
    #     prompt=prompt_registry.get_prompt("agent_router")
    #     )
    





    # Conditional function

    def retrievalCondition(state):
        conditinalFunctionPrompt = prompt_registry.get_prompt("agent_router")
        agent_description = agent_registery.description()
        formatted_prompt = conditinalFunctionPrompt.format(
        agent_description=json.dumps(
            agent_description,
            indent=2
        ),
        user_input = state["user_query"],
        user_history = state["history"]
        )
        result = llm.generate(formatted_prompt)

        if result not in agent_registery.agents:
            raise ValueError(
                f"Invalid agent selected: {result}"
            )

        state["status"] = "agent_execution"

        state["messages"].append({
            "role": "router",
            "selected_agent": result
        })

        return result



#graph
    graph.addNode("docs_agent")
    graph.addNode("codebase_agent")
    graph.addNode("records_agent")

    graph.addConditionalEdges("start", retrievalCondition)

    graph.addEdge("docs_agent", "end")
    graph.addEdge("codebase_agent", "end")
    graph.addEdge("records_agent", "end")
    # graph.addNode(agent_registery.get("summary_agent"))



#start

    user_query = "Where is JWT validation implemented?"
    state["user_query"] = user_query

    state = graph.start(state)

    print("\nRetrieved:\n",state["history"])

    print("\nFinal:\n", state["final_answer"])