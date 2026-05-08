from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize

if __name__ == "__main__":

    state = {
    "user_query": None,
    "history": [],
    "tool_outputs": {},
    "selected_tool": None,
    "doc_type": None,
    "retrieved_data": None,
    "context": None,
    "final_answer": None,
    "history": []
}

    llm = LLM()

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
        state=state,
        task = """
            You are an intelligent tool-routing system.
            - Understand the user query
            - Select the SINGLE BEST tool
            - Generate the type of file it can be among code, docs, records.
            """
    )

    summary_agent = Agent(
        tools = summary_tools,
        state = state
    )
    
    user_query = input() or "Where is JWT validation implemented?"
    
    state["user_query"] = user_query

    state = retrieval_agent.run(state)

    print("\nRetrieved:\n",state["retrieval_result"])

    final_answer = summary_agent.run(state)

    print("\nFinal:\n",final_answer)