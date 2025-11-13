"""
gRPC Server Setup
Настройка и запуск gRPC сервера
"""

import grpc
from concurrent import futures
import logging
from prometheus_client import start_http_server

from rpc.classroom_service import ClassroomServicer
from config import config

logger = logging.getLogger(__name__)


def serve():
    """Запустить gRPC сервер"""
    
    # Add proto/generated to sys.path so Python can find pb2 modules
    import sys
    import os
    proto_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'proto', 'generated')
    if proto_path not in sys.path:
        sys.path.insert(0, proto_path)
    
    # Import proto files here (after entrypoint generates them)
    try:
        from proto.generated import classroom_pb2_grpc
    except ImportError as e:
        logger.error(
            f"Protobuf files not generated: {e}. Please run: "
            "python -m grpc_tools.protoc -I./proto "
            "--python_out=./proto/generated "
            "--grpc_python_out=./proto/generated "
            "--pyi_out=./proto/generated "
            "./proto/classroom.proto"
        )
        raise RuntimeError("Protobuf files not generated")
    
    # Create gRPC server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.GRPC_MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', config.GRPC_MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', config.GRPC_MAX_MESSAGE_LENGTH),
        ]
    )
    
    # Add servicer to server
    classroom_pb2_grpc.add_ClassroomServiceServicer_to_server(
        ClassroomServicer(),
        server
    )
    
    # Bind to port
    server.add_insecure_port(f'[::]:{config.GRPC_PORT}')
    
    logger.info(f"Starting gRPC server on port {config.GRPC_PORT}")
    logger.info(f"Max workers: {config.GRPC_MAX_WORKERS}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    
    # Start metrics server
    if config.ENABLE_METRICS:
        start_http_server(config.METRICS_PORT)
        logger.info(f"Metrics server started on port {config.METRICS_PORT}")
    
    # Start server
    server.start()
    logger.info("gRPC server started successfully")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(grace=5)
        logger.info("gRPC server stopped")


if __name__ == '__main__':
    serve()

