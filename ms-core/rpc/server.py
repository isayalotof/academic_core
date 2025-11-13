"""
gRPC server for ms-core
"""
import logging
from concurrent import futures
import grpc
from grpc_reflection.v1alpha import reflection

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
        from proto.generated import core_pb2, core_pb2_grpc
        from rpc.core_service import CoreServicer
    except ImportError as e:
        logger.error(f"Cannot start server: proto files not generated: {e}")
        logger.error("Run: bash scripts/generate_proto_core.sh")
        return
    
    # Create server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.GRPC_MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MB
        ]
    )
    
    # Add servicer
    core_pb2_grpc.add_CoreServiceServicer_to_server(CoreServicer(), server)
    logger.info("✓ CoreServicer registered")
    
    # Enable reflection for grpc_cli
    SERVICE_NAMES = (
        core_pb2.DESCRIPTOR.services_by_name['CoreService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    logger.info("✓ gRPC reflection enabled")
    
    # Bind port
    server_address = f'[::]:{config.GRPC_PORT}'
    server.add_insecure_port(server_address)
    
    # Start server
    server.start()
    logger.info(f"✓ gRPC server started on {server_address}")
    logger.info(f"✓ Max workers: {config.GRPC_MAX_WORKERS}")
    logger.info("✓ Ready to accept requests")
    
    # Wait for termination
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(grace=5)

