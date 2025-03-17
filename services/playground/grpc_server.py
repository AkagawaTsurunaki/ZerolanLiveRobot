from concurrent import futures

import grpc
from loguru import logger

from common.utils.img_util import save_bytes_as_image
from common.utils.web_util import get_local_ip
from event.event_data import SpeechEvent, ScreenCapturedEvent
from event.eventemitter import emitter
from services.playground.proto import bridge_pb2, bridge_pb2_grpc


def start_server(server, host, port):
    server.add_insecure_port(f'{host}:{port}')

    # 启动服务器
    logger.info("Starting gRPC server. Listening on port 11020.")
    server.start()
    server.wait_for_termination()


class GRPCServer(bridge_pb2_grpc.PlaygroundBridgeServicer):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def SendSpeechChunk(self, request, context):
        logger.info("Get speech data from client.")
        emitter.emit(SpeechEvent(speech=request.data,
                                 channels=request.channels,
                                 sample_rate=request.sample_rate))
        response = bridge_pb2.RPCResponse(message=f"OK", code=0)
        return response

    def SendCameraImage(self, request, context):
        logger.info("Get camera image from client.")
        img_path = save_bytes_as_image(request.data, request.image_type)
        emitter.emit(ScreenCapturedEvent(img_path=img_path, is_camera=True))
        response = bridge_pb2.RPCResponse(message=f"OK", code=0)
        return response

    def start(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        bridge_pb2_grpc.add_PlaygroundBridgeServicer_to_server(GRPCServer(self.host, self.port), server)

        start_server(server, self.host, self.port)
