from __future__ import annotations

import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated

from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

load_dotenv()

# ---------- Azure clients ----------

_openai = AzureOpenAI(
    azure_endpoint="https://waitemiles-3441-resource.services.ai.azure.com",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

_blob = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))

_search = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="risk-docs",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

_llm = AzureChatOpenAI(
    azure_endpoint="https://waitemiles-3441-resource.services.ai.azure.com",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment="gpt-4o",
    api_version="2024-02-01",
    temperature=0
)

# ---------- Load positions ----------

_positions_path = Path(__file__).parent.parent / "data" / "positions.csv"
_df = pd.read_csv(_positions_path)

# ---------- Tools ----------

@tool
def get_positions(trader: str = None, desk: str = None, commodity: str = None) -> str:
    """Get trading positions. Filter by trader name, desk, or commodity. Leave blank for all positions."""
    df = _df.copy()
    if trader:
        df = df[df["trader"].str.contains(trader, case=False)]
    if desk:
        df = df[df["desk"].str.contains(desk, case=False)]
    if commodity:
        df = df[df["commodity"].str.contains(commodity, case=False)]
    return df.to_json(orient="records", indent=2)


@tool
def calculate_portfolio_var(trader: str = None, desk: str = None, confidence: str = "95") -> str:
    """Calculate portfolio VaR. Aggregates across positions. Confidence level: 95 or 99."""
    df = _df.copy()
    if trader:
        df = df[df["trader"].str.contains(trader, case=False)]
    if desk:
        df = df[df["desk"].str.contains(desk, case=False)]

    col = "var_95_1d" if confidence == "95" else "var_99_1d"
    total_var = df[col].sum()
    total_notional = df["notional_usd"].sum()
    var_pct = (total_var / total_notional) * 100

    return json.dumps({
        "positions_count": int(len(df)),
        "total_notional_usd": int(total_notional),
        f"portfolio_var_{confidence}_1d_usd": int(total_var),
        "var_as_pct_notional": round(float(var_pct), 3),
        "largest_var_position": str(df.loc[df[col].idxmax(), "position_id"]),
        "confidence_level": f"{confidence}%"
    }, indent=2)


@tool
def get_risk_methodology(query: str) -> str:
    """Retrieve risk methodology documentation. Use for questions about VaR methods, Monte Carlo, trading controls."""
    embedding = _openai.embeddings.create(
        model="text-embedding-3-small", input=query
    ).data[0].embedding
    vq = VectorizedQuery(vector=embedding, k_nearest_neighbors=2, fields="embedding")
    results = _search.search(search_text=None, vector_queries=[vq], select=["content", "filename"])
    docs = [r["content"] for r in results]
    return "\n\n---\n\n".join(docs) if docs else "No relevant documentation found."


# ---------- Agent graph ----------

class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [get_positions, calculate_portfolio_var, get_risk_methodology]
tool_node = ToolNode(tools)
llm_with_tools = _llm.bind_tools(tools)

SYSTEM_PROMPT = """You are a risk analyst assistant for an energy trading desk.
You have access to live trading position data and risk methodology documentation.
When asked about risk, always retrieve the relevant positions first, calculate VaR, and explain the results clearly.
Quote specific position IDs and dollar amounts. Be precise and concise."""


def agent_node(state: State):
    messages = state["messages"]
    if not any(hasattr(m, "role") and m.role == "system" for m in messages):
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: State):
    last = state["messages"][-1]
    return "tools" if hasattr(last, "tool_calls") and last.tool_calls else END


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
app = graph.compile()


def query(question: str) -> str:
    result = app.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    questions = [
        "What is the total portfolio VaR at 95% confidence?",
        "Which trader has the highest risk exposure?",
        "Explain the VaR methodology used and how it applies to our crude oil positions.",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {query(q)}\n{'='*60}")
