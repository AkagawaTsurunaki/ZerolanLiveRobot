import asyncio
from typing import Type

from loguru import logger
from websockets import ConnectionClosedError
from websockets.asyncio.server import serve, ServerConnection

from agent.tool_agent import Tool
from common.eventemitter import emitter, EventEnum
from services.game.minecraft.data import KonekoProtocol
from services.game.minecraft.instrcution.input import generate_model_from_args, FieldMetadata
from services.game.minecraft.instrcution.tool import KonekoInstructionTool


class KonekoMinecraftAIAgent:

    def __init__(self, host: str, port: int):
        super().__init__()
        self._host = host
        self._port = port
        self._ws: ServerConnection = None
        self._stop_flag = False
        self._instructions = []

    @emitter.on(EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS)
    def tools_register(self, tools: list[Tool]):
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
            tool = KonekoInstructionTool(name=tool_name, description=tool_desc, args_schema=Type[model], koneko=self)
            result.append(tool)
        self._instructions = result

    @emitter.on(EventEnum.KONEKO_CLIENT_HELLO)
    async def fetch_instructions(self):
        protocol_obj = KonekoProtocol(event=EventEnum.KONEKO_SERVER_FETCH_INSTRUCTIONS)
        await self.send_message(protocol_obj)

    @staticmethod
    def valid_protocol(msg: str) -> KonekoProtocol | None:
        protocol_obj: KonekoProtocol = KonekoProtocol.from_json(msg)
        if protocol_obj.protocol != "Koneko Protocol":
            logger.error(f"Unsupported protocol: {protocol_obj.protocol}")
            return None
        if protocol_obj.version != "0.2":
            logger.error(f"Unsupported version: {protocol_obj.version}")
            return None
        return protocol_obj

    async def event_emitter(self, protocol_obj: KonekoProtocol):
        if protocol_obj.event == EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS:
            tools = []
            for tool in protocol_obj.data:
                tools.append(Tool.model_validate(tool))
            emitter.emit(EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS, tools)
        elif protocol_obj.event == EventEnum.KONEKO_CLIENT_HELLO:
            emitter.emit(EventEnum.KONEKO_CLIENT_HELLO)

    async def _run(self):
        async def handler(websocket: ServerConnection):
            self._ws = websocket
            while not self._stop_flag:
                msg = await websocket.recv()
                # Get instructions register
                protocol_obj = self.valid_protocol(msg)
                if protocol_obj:
                    await self.event_emitter(protocol_obj)
                logger.info(msg)

        # set this future to exit the server
        stop = asyncio.get_running_loop().create_future()

        async with serve(handler, self._host, self._port):
            await stop

    def start(self):
        asyncio.run(self._run())

    async def send_message(self, msg: KonekoProtocol):
        msg = msg.to_json()
        if self._ws is None:
            logger.warning("No client connected to your Websocket server. Send message makes no effort.")
            return

        try:
            await self._ws.send(msg)
        except ConnectionClosedError as e:
            logger.error(e)
            logger.warning(
                "KonekoMinecraftBot should send close message to close this connection. Check your bot is still online?")
        except Exception as e:
            logger.exception(e)

    def stop(self):
        self._stop_flag = True
