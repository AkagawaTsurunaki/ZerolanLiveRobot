from typing import Dict, List

from langchain_core.messages import HumanMessage
from loguru import logger
from zerolan.data.protocol.protocol import ZerolanProtocol

from agent.tool_agent import Tool, ToolAgent
from common.web.zrl_ws import ZerolanProtocolWsServer
from event.registry import EventKeyRegistry
from services.game.config import GameBridgeConfig
from services.game.minecraft.instrcution.input import generate_model_from_args, FieldMetadata
from services.game.minecraft.instrcution.tool import KonekoInstructionTool


class KonekoMinecraftAIAgent(ZerolanProtocolWsServer):

    def on_disconnect(self, ws_id: str):
        logger.warning("Koneko disconnected from ZerolanLiveRobot.")

    def __init__(self, config: GameBridgeConfig, tool_agent: ToolAgent):
        super().__init__(config.host, config.port)
        self._instruction_tools: Dict[str, KonekoInstructionTool] = dict()
        self._tool_agent = tool_agent

    def on_protocol(self, protocol: ZerolanProtocol):
        if protocol.action == EventKeyRegistry.Koneko.Client.PUSH_INSTRUCTIONS:
            self._on_push_instructions(protocol.data)
        elif protocol.action == EventKeyRegistry.Koneko.Client.HELLO:
            self._fetch_instructions()

    def _on_push_instructions(self, tools: List[Tool]):
        result = []
        for i, tool in enumerate(tools):
            tool = Tool.model_validate(tool)
            assert tool.type == "function"
            tool_name = tool.function.name
            tool_desc = tool.function.description
            required_props = set(tool.function.parameters.required)
            params_type = tool.function.parameters.type
            properties = tool.function.parameters.properties

            arg_list: list[FieldMetadata] = []
            for prop_name, prop in properties.items():
                metadata = FieldMetadata(name=prop_name, type=prop.type, description=prop.description,
                                         required=prop_name in required_props)
                arg_list.append(metadata)

            model = generate_model_from_args(class_name=params_type, args_list=arg_list)
            tool = KonekoInstructionTool(name=tool_name, description=tool_desc, args_schema=model)
            result.append(tool)
        self._tool_agent.bind_tools(result)
        self._instruction_tools = dict()
        for tool in result:
            self._instruction_tools[tool.name] = tool
        logger.info(f"{len(self._instruction_tools)} instruction tools are bound.")

    def _fetch_instructions(self):
        self.send(action=EventKeyRegistry.Koneko.Server.FETCH_INSTRUCTIONS, data=None)

    def exec_instruction(self, query: str):
        if len(self._instruction_tools) == 0:
            logger.warning("No instruction to execute. Are your sure that KonekoMinecraftBot has started?")
            return

        messages = [self._tool_agent.system_prompt, HumanMessage(query)]
        ai_msg = self._tool_agent.invoke(messages)
        messages.append(ai_msg)
        assert hasattr(ai_msg, "tool_calls")
        for tool_call in ai_msg.tool_calls:
            selected_tool = self._instruction_tools[tool_call["name"]]
            logger.info(f"Ready tool call: {tool_call}")
            tool_msg = selected_tool.invoke(tool_call)
            messages.append(tool_msg)
        logger.debug(messages)
