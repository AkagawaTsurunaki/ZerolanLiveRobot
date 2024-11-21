import json
from enum import Enum
from typing import Annotated

from langchain_core.messages import ToolMessage
from langgraph.constants import END, START
from langgraph.graph import add_messages, StateGraph
from loguru import logger
from typing_extensions import TypedDict

from agent.baidu import BaiduBaikeTool
from agent.tool_agent import ToolAgent
from common.config import get_config

tools = [BaiduBaikeTool()]


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

config = get_config()
llm = ToolAgent(config.pipeline.llm)
llm.bind_tools(tools)


class NodeEnum(str, Enum):
    CHATBOT = "chatbot"
    TOOLS = "tools"


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result, ensure_ascii=False),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


def route_tools(state: State, ):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return NodeEnum.TOOLS.value
    return END


graph_builder.add_node(NodeEnum.CHATBOT.value, chatbot)
tool_node = BasicToolNode(tools=tools)
graph_builder.add_node(NodeEnum.TOOLS.value, tool_node)
graph_builder.add_conditional_edges(
    NodeEnum.CHATBOT.value,
    route_tools,
    {NodeEnum.TOOLS.value: NodeEnum.TOOLS.value, END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge(NodeEnum.TOOLS.value, NodeEnum.CHATBOT.value)
graph_builder.add_edge(START, NodeEnum.CHATBOT.value)
graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    inoput = {"messages": [llm.system_prompt, ("user", user_input)]}
    for event in graph.stream(inoput):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


try:
    user_input = "搜索绫地宁宁，找到内容后就可以退出了"
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")

    stream_graph_updates(user_input)
except Exception as e:
    # fallback if input() is not available
    logger.exception(e)
