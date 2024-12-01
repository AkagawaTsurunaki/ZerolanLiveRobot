from typing import Dict

from langchain_core.messages import HumanMessage
from loguru import logger

from agent.tool_agent import Tool, ToolAgent
from common.config import GameBridgeConfig
from common.enumerator import EventEnum, SystemSoundEnum
from event.eventemitter import emitter
from event.websocket import OldWebSocketServer
from services.device.speaker import Speaker
from services.game.minecraft.data import KonekoProtocol
from services.game.minecraft.instrcution.input import generate_model_from_args, FieldMetadata
from services.game.minecraft.instrcution.tool import KonekoInstructionTool


class KonekoMinecraftAIAgent:

    def __init__(self, config: GameBridgeConfig, tool_agent: ToolAgent):
        super().__init__()
        self.ws = OldWebSocketServer(host=config.host, port=config.port)
        self._instruction_tools: Dict[str, KonekoInstructionTool] = dict()
        self._tool_agent = tool_agent

    def _init(self):
        @emitter.on(EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS)
        def tools_register(tools: list[Tool]):
            result = []
            for i, tool in enumerate(tools):
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
            logger.info(f"{len(self._instruction_tools)} Instruction tools are bound.")

        @emitter.on(EventEnum.KONEKO_SERVER_CALL_INSTRUCTION)
        async def send_message(protocol_obj: KonekoProtocol):
            await self.ws.send_json(protocol_obj.model_dump())

        @emitter.on(EventEnum.KONEKO_CLIENT_HELLO)
        async def fetch_instructions():
            protocol_obj = KonekoProtocol(event=EventEnum.KONEKO_SERVER_FETCH_INSTRUCTIONS)
            await self.ws.send_json(protocol_obj.model_dump())

        @self.ws.on(EventEnum.WEBSOCKET_RECV_JSON)
        async def event_emitter(data: any):
            protocol_obj = self.valid_protocol(data)
            if protocol_obj.event == EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS:
                tools = [Tool.model_validate(tool) for tool in protocol_obj.data]
                await emitter.emit(EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS, tools)
            elif protocol_obj.event == EventEnum.KONEKO_CLIENT_HELLO:
                await emitter.emit(EventEnum.KONEKO_CLIENT_HELLO)

    @staticmethod
    def valid_protocol(data: any) -> KonekoProtocol | None:
        protocol_obj = KonekoProtocol.model_validate(data)
        if protocol_obj.protocol != "Koneko Protocol":
            logger.error(f"Unsupported protocol: {protocol_obj.protocol}")
            return None
        if protocol_obj.version != "0.2":
            logger.error(f"Unsupported version: {protocol_obj.version}")
            return None
        return protocol_obj

    def start(self):
        self._init()
        self.ws.start()

    async def exec_instruction(self, query: str):
        if len(self._instruction_tools) == 0:
            Speaker.play_system_sound(SystemSoundEnum.warn)
            logger.warning("No instruction to execute. Are your sure that KonekoMinecraftBot has started?")
            return

        messages = [self._tool_agent.system_prompt, HumanMessage(query)]
        ai_msg = self._tool_agent.invoke(messages)
        messages.append(ai_msg)
        assert hasattr(ai_msg, "tool_calls")
        for tool_call in ai_msg.tool_calls:
            selected_tool = self._instruction_tools[tool_call["name"]]
            logger.info(f"Ready tool call: {tool_call}")
            tool_msg = await selected_tool.ainvoke(tool_call)
            messages.append(tool_msg)
        logger.debug(messages)
        # tool.invoke(ToolCall(id="asdsad", args={"content": "Ciallo"}, name="chat"))

    def stop(self):
        self.ws.stop()