from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph
from langgraph.graph import END, START
from langgraph.prebuilt import ToolNode, tools_condition

from tools import sql_read, extract_data, calculator, fig_inter, get_date
from prompts import PROMPT

load_dotenv()

model = ChatOpenAI(
    model="qwen3-32b",
    api_key=os.environ["QWEN_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

tools = [calculator, sql_read, extract_data, fig_inter, get_date]
tool_node = ToolNode(tools)

model_with_tools = model.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def call_model(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}
    
graph_workflow = StateGraph(State)

graph_workflow.add_node("tools", tool_node)
graph_workflow.add_node("agent", call_model)

graph_workflow.add_edge(START, "agent")
graph_workflow.add_edge("tools", "agent")
graph_workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        END: END
    }
)

graph = graph_workflow.compile()
