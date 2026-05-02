from openai.types.responses.response_reasoning_item import Summary
from agents.retrievalAgent import RetrievalAgent
from rag.retriever import retriever
from rag.llm.llmSetUp import RouterLLM, SummaryLLM

user_query = "Where is JWT validation implemented?"

retrievedResult = RetrievalAgent(retriever, RouterLLM, SummaryLLM).run(user_query)

print(retrievedResult)