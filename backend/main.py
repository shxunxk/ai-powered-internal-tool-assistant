from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize
import json
from llmOps.prompts import prompt_registry
from router.agent_registery import agent_registry

if __name__ == "__main__":

# state initialization
    state = {
    "user_query": None,
    "history": [],
    "tool_outputs": {},
    "selected_tool": None,
    "context": None,
    "final_answer": None,
    }

    llm = LLM()

    docs_agent_tools = [
        Tool(search_docs),
    ]

    codebase_agent_tools = [
        Tool(search_code),
    ]

    records_agent_tools = [
        Tool(search_records),
    ]

    summarize_agent_tools = [
        Tool(summarize)
    ]



    # policy_agent_tools = [
    #     Tool(search_policy),
    #     Tool(summarize)
    # ]


    agent_registry.register(Agent(
        tools=docs_agent_tools,
        llm=llm,
        prompt = prompt_registry.get_prompt("agent_reasoning"),
        name = "docs_agent", 
        description="Retrieves and analyzes information from internal documents, policies, manuals, and knowledge bases."
    ))

    agent_registry.register(Agent(
        tools=codebase_agent_tools,
        llm=llm,
        prompt = prompt_registry.get_prompt("agent_reasoning"),
        name = "codebase_agent",
        description = "Searches, analyzes, and explains source code, software architecture, implementations, dependencies, and code-related issues."
        ))

    agent_registry.register(Agent(
        tools = records_agent_tools,
        prompt = prompt_registry.get_prompt("agent_summary"),
        name = "records_agent",
        description="Retrieves and summarizes structured records and data, including user, business, transactional, or system records."
    ))



    

    # policy_agent = Agent(
    #     tools = policy_agent_tools,
    #     prompt = prompt_registry.get_prompt("")
    # )
    
    user_query = "Where is JWT validation implemented?"
    
    state["user_query"] = user_query

    

    # state = retrieval_agent.run(state)

    print("\nRetrieved:\n",state["history"])

    print("\nFinal:\n",final_answer["final_answer"])