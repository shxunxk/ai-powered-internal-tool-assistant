from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize
from llmOps.prompts import prompt_registry
from router.agent_registery import AgentRegistery
from router.router_setup import Router

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

    llm = LLM()


    result = llm.generate("Say hello in one sentence.")

    print(result)

    agent_registery = AgentRegistery()

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
# Focus areas: Python Systems Engineering, Agentic & LLMs Architecture, Production Ownership, Secure Engineering
    # agent_registery.register(Agent(
    #     tools = summarize_agent_tools,
    #     name = "summarize_agent",
    #     description="Retrieves and summarizes structured records and data, including user, business, transactional, or system records.",
    #     prompt = prompt_registry.get_prompt("agent_summary"),
    # ))

    router = Router(
        agent_registery=agent_registery,
        llm=llm,
        prompt=prompt_registry.get_prompt("agent_router")
        )


    # policy_agent = Agent(
    #     tools = policy_agent_tools,
    #     prompt = prompt_registry.get_prompt("")
    # )
    
    user_query = "Where is JWT validation implemented?"
    
    state["user_query"] = user_query

    result = router.route(
    "Where is JWT validation implemented?"
    )

    # state = retrieval_agent.run(state)

    print("\nRetrieved:\n",state["history"])

    print("\nFinal:\n", result["final_answer"])