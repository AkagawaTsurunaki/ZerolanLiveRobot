# 导入必要的模块
from concurrent import futures

import grpc

from bridge.proto import helloworld_pb2, helloworld_pb2_grpc


# 实现 Greeter 服务
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        # 根据请求生成响应
        response = helloworld_pb2.HelloReply(message=f"Hello, {request.name}!")
        return response


def start_server(server):
    server.add_insecure_port('0.0.0.0:11020')

    # 启动服务器
    print("Starting server. Listening on port 50051.")
    server.start()
    server.wait_for_termination()


# 启动服务
def test_greeter():
    # 创建 gRPC 服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    start_server(server)


from bridge.proto import microphone_pb2, microphone_pb2_grpc
from loguru import logger


class MicrophoneManagerServer(microphone_pb2_grpc.MicrophoneManagerServicer):
    def SendSpeechChunk(self, request, context):
        logger.info("Get speech data from remote microphone")
        print(len(request.data))
        response = microphone_pb2.RPCResponse(message=f"OK", code=0)
        return response


# 启动服务
def test_microphone_manager():
    # 创建 gRPC 服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    microphone_pb2_grpc.add_MicrophoneManagerServicer_to_server(MicrophoneManagerServer(), server)

    start_server(server)
