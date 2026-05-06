from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize

if __name__ == "__main__":

    state = {
        "user_quer":None,
        "curr_data":None,
        "prev_data":None
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
        llm=llm
        state=state
    )

    summary_agent = Agent(
        tools = summary_tools,
        state=state
    )
    
    user_query = "Where is JWT validation implemented?"
    state["user_query"] = user_query

    retrieval_result = retrieval_agent.run(state)

    print("\nRetrieved:\n",retrieval_result)

    final_answer = summary_agent.run(data=retrieval_result["result"], query = user_query)

    print("\nFinal:\n",final_answer)