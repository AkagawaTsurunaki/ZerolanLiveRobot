import os
import subprocess


# python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. bridge/proto/*.proto
def compile_proto_files(proto_dir):
    # 获取指定目录下的所有文件
    files = os.listdir(proto_dir)

    # 筛选出所有以.proto结尾的文件
    proto_files = [f for f in files if f.endswith('.proto')]

    if not proto_files:
        print(f"No .proto files found in {proto_dir}.")
        return

    # 构造命令
    command = [
        "python", "-m", "grpc_tools.protoc",
        "-I.",  # 指定包含目录
        "--python_out=.",  # 指定Python输出目录
        "--grpc_python_out=."  # 指定gRPC Python输出目录
    ]

    # 将所有.proto文件添加到命令中
    command.extend([os.path.join(proto_dir, f) for f in proto_files])

    # 执行命令
    print("Executing command:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    print("Compiling protoc...")
    proto_dirs = ["services/playground/proto", "tests/common/ws/proto"]  # 指定.proto文件所在的目录

    for proto_dir in proto_dirs:
        compile_proto_files(proto_dir)
    print("Done.")
