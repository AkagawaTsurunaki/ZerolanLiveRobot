from concurrent import futures

import grpc
from loguru import logger

from bridge.proto import microphone_pb2_grpc, microphone_pb2
from event.event_data import SpeechEvent
from event.eventemitter import emitter


def start_server(server):
    server.add_insecure_port('0.0.0.0:11020')

    # 启动服务器
    logger.info("Starting gRPC server. Listening on port 11020.")
    server.start()
    server
    server.wait_for_termination()


class GRPCServer(microphone_pb2_grpc.MicrophoneManagerServicer):
    def SendSpeechChunk(self, request, context):
        logger.info("Get speech data from remote microphone")
        emitter.emit(SpeechEvent(speech=request.data,
                                 channels=request.channels,
                                 sample_rate=request.sample_rate))
        response = microphone_pb2.RPCResponse(message=f"OK", code=0)
        return response

    def start(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        microphone_pb2_grpc.add_MicrophoneManagerServicer_to_server(GRPCServer(), server)

        start_server(server)
