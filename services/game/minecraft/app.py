import asyncio
import json
from typing import Type

from loguru import logger
from websockets import ConnectionClosedError
from websockets.asyncio.server import serve, ServerConnection

from agent.tool_agent import Tool
from common.enumerator import EventEnum
from common.eventemitter import emitter, EventEmitter
from services.game.minecraft.data import KonekoProtocol
from services.game.minecraft.instrcution.input import generate_model_from_args, FieldMetadata
from services.game.minecraft.instrcution.tool import KonekoInstructionTool


class WebSocketServer(EventEmitter):

    def __init__(self, host: str = "127.0.0.1", port: int = 10098):
        super().__init__()
        self._host = host
        self._port = port
        self._ws: ServerConnection
        self._stop_flag = False

    def start(self):
        asyncio.ensure_future(self._run())

    async def _run(self):
        stop = asyncio.get_running_loop().create_future()

        async with serve(self._handler, self._host, self._port):
            await stop

    async def _handler(self, websocket: ServerConnection):
        self._ws = websocket
        while not self._stop_flag:
            msg = await websocket.recv()
            data = json.loads(msg)
            await self.emit(EventEnum.WEBSOCKET_RECV_JSON, data)
            logger.info("Web Socket server received: " + data)

    async def send_json(self, msg: any):
        msg = json.dumps(msg, ensure_ascii=False, indent=4)
        if self._ws is None:
            logger.warning("No client connected to your Websocket server. Send message makes no effort.")
            return
        try:
            await self._ws.send(msg)
        except ConnectionClosedError as e:
            logger.exception(e)
            logger.warning("A client disconnected from Web Socket server.")
        except Exception as e:
            logger.exception(e)

    def stop(self):
        super().stop()
        self._stop_flag = True


class KonekoMinecraftAIAgent:

    # @inject
    def __init__(self, ws: WebSocketServer):
        super().__init__()
        self.ws = ws
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
            tool = KonekoInstructionTool(name=tool_name, description=tool_desc, args_schema=Type[model])
            result.append(tool)
        self._instructions = result

    @emitter.on(EventEnum.KONEKO_CLIENT_HELLO)
    async def fetch_instructions(self):
        protocol_obj = KonekoProtocol(event=EventEnum.KONEKO_SERVER_FETCH_INSTRUCTIONS)
        await self.send_message(protocol_obj)

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
        @self.ws.on(EventEnum.WEBSOCKET_RECV_JSON)
        def event_emitter(data: any):
            protocol_obj = self.valid_protocol(data)
            if protocol_obj.event == EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS:
                tools = [Tool.model_validate(tool) for tool in protocol_obj.data]
                emitter.emit(EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS, tools)
            elif protocol_obj.event == EventEnum.KONEKO_CLIENT_HELLO:
                emitter.emit(EventEnum.KONEKO_CLIENT_HELLO)

    @emitter.on(EventEnum.KONEKO_SERVER_CALL_INSTRUCTION)
    async def send_message(self, protocol_obj: KonekoProtocol):
        await self.ws.send_json(protocol_obj)
