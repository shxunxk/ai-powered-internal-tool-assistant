from backed import Tool
from Agent import Agent
from rag.retriever import retriever
from rag.llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize

if __name__ == "__main__":

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
    )

    summary_agent = Agent(
        tools = summary_tools,
        llm = llm
    )

    user_query = "Where is JWT validation implemented?"

    retrieval_result = retrieval_agent.run(user_query)

    print(retrieval_result)

    final_answer = summary_agent.run(query=retrieval_result)

    print(final_answer)