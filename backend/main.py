from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize
import json
from llmOps.prompts import prompt_registry

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

    # """ 
    # multi-agent orchestration LLM-based system 

    # prompt = You have following agents available to you:
    # ''
    # ''
    # ''
    # """

    # router_agent = Agent(
    # task="Identify if this is an incident question, code question, or docs question"
    # )

    retirieval_tools = [
        Tool(search_code),
        Tool(search_records),
        Tool(search_docs)
    ]

    summary_tools = [
        Tool(summarize)
    ]


    retrieval_agent = Agent(
        tools=retirieval_tools,
        llm=llm,
        prompt = prompt_registry.get_prompt("agent_reasoning")
    )

    summary_agent = Agent(
        tools = summary_tools,
        prompt = prompt_registry.get_prompt("agent_summary")
    )
    
    user_query = "Where is JWT validation implemented?"
    
    state["user_query"] = user_query

    state = retrieval_agent.run(state)

    print("\nRetrieved:\n",state["history"])

    final_answer = summary_agent.run(state)

    print("\nFinal:\n",final_answer["final_answer"])