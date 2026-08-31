from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

from Tool import Tool
from Agent import Agent
from llm.llmSetUp import LLM
from tools import search_code, search_docs, search_records, summarize
from llmOps.prompts import prompt_registry
from router.agent_registery import AgentRegistery
from Graph import Graph

app = FastAPI(title="AI Internal Tool Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    history: Optional[List[str]] = []


class QueryResponse(BaseModel):
    answer: str
    status: str
    selected_agent: Optional[str] = None


def build_graph():
    llm = LLM()
    agent_registery = AgentRegistery()
    graph = Graph(agent_registery)

    docs_agent_tools = [Tool(search_docs)]
    codebase_agent_tools = [Tool(search_code)]
    records_agent_tools = [Tool(search_records)]
    summarize_agent_tools = [Tool(summarize)]

    agent_registery.register(
        Agent(
            tools=docs_agent_tools,
            name="docs_agent",
            description="Retrieves and analyzes information from internal documents, policies, manuals, and knowledge bases.",
            llm=llm,
            prompt=prompt_registry.get_prompt("agent_reasoning"),
        )
    )

    agent_registery.register(
        Agent(
            tools=codebase_agent_tools,
            name="codebase_agent",
            description="Searches, analyzes, and explains source code, software architecture, implementations, dependencies, and code-related issues.",
            llm=llm,
            prompt=prompt_registry.get_prompt("agent_reasoning"),
        )
    )

    agent_registery.register(
        Agent(
            tools=records_agent_tools,
            name="records_agent",
            description="Searches, analyzes, and explains incidents, events, logs and metrics.",
            llm=llm,
            prompt=prompt_registry.get_prompt("agent_reasoning"),
        )
    )

    agent_registery.register(
        Agent(
            tools=summarize_agent_tools,
            name="summarize_agent",
            description="Retrieves and summarizes structured records and data, including user, business, transactional, or system records.",
            prompt=prompt_registry.get_prompt("agent_summary"),
        )
    )

    def retrievalCondition(state):
        conditional_prompt = prompt_registry.get_prompt("agent_router")
        agent_description = agent_registery.description()
        formatted_prompt = conditional_prompt.format(
            agent_description=json.dumps(agent_description, indent=2),
            user_input=state["user_query"],
            user_history=state["history"],
        )
        result = llm.generate(formatted_prompt)

        if result not in agent_registery.agents:
            raise ValueError(f"Invalid agent selected: {result}")

        state["status"] = "agent_execution"
        state["messages"].append({
            "role": "router",
            "selected_agent": result,
        })
        return result

    graph.addNode("docs_agent")
    graph.addNode("codebase_agent")
    graph.addNode("records_agent")
    graph.addNode("summarize_agent")

    graph.addConditionalEdges("start", retrievalCondition)
    graph.addEdge("docs_agent", "summarize_agent")
    graph.addEdge("codebase_agent", "summarize_agent")
    graph.addEdge("records_agent", "summarize_agent")
    graph.addEdge("summarize_agent", "end")

    return graph


def run_query(user_query: str):
    graph = build_graph()
    state = {
        "user_query": user_query,
        "history": [],
        "tool_outputs": {},
        "selected_tool": None,
        "context": None,
        "messages": [],
        "status": "routing",
    }

    final_state = graph.start(state)
    history = final_state.get("history", [])

    if history:
        last_item = history[-1]
        answer = last_item.get("result") or last_item.get("agent_output") or "No answer generated."
    else:
        answer = "No answer generated."

    selected_agent = None
    if final_state.get("messages"):
        selected_agent = final_state["messages"][-1].get("selected_agent")

    return QueryResponse(
        answer=str(answer),
        status=final_state.get("status", "completed"),
        selected_agent=selected_agent,
    )


@app.get("/")
def root():
    return {"message": "AI Internal Tool Assistant backend is running."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        return run_query(request.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(exc)}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
