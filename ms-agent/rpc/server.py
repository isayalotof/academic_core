"""
gRPC Server Setup
"""

import grpc
from concurrent import futures
import logging

from rpc.agent_service import AgentServicer
from config import config

logger = logging.getLogger(__name__)


def serve():
    """Start gRPC server"""
    
    # Add proto/generated to sys.path so Python can find pb2 modules
    import sys
    import os
    proto_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'proto', 'generated')
    if proto_path not in sys.path:
        sys.path.insert(0, proto_path)
    
    # Import proto files here (after entrypoint generates them)
    try:
        from proto.generated import agent_pb2_grpc
    except ImportError as e:
        logger.error(f"Protobuf files not generated: {e}")
        raise RuntimeError("Protobuf files not generated")
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.GRPC_MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', config.GRPC_MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', config.GRPC_MAX_MESSAGE_LENGTH),
        ]
    )
    
    agent_pb2_grpc.add_AgentServiceServicer_to_server(
        AgentServicer(),
        server
    )
    
    server.add_insecure_port(f'[::]:{config.GRPC_PORT}')
    
    logger.info(f"Starting gRPC server on port {config.GRPC_PORT}")
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

