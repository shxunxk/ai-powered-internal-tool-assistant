from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize
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
    }

    llm = LLM()

    """ 
    multi-agent orchestration LLM-based system 

    prompt = You have following agents available to you:
    ''
    ''
    ''
    """

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
        task = """
            You have act as an intelligent tool-routing system.
            - Understand the user query
            - Select the SINGLE BEST tool
            """
    )

    summary_agent = Agent(
        tools = summary_tools,
    )
    
    user_query = "Where is JWT validation implemented?"
    
    state["user_query"] = user_query

    state = retrieval_agent.run(state)

    print("\nRetrieved:\n",state["history"])

    final_answer = summary_agent.run(state)

    print("\nFinal:\n",final_answer["final_answer"])