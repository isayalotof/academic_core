"""
gRPC server for ms-lms
"""
import logging
from concurrent import futures
import grpc
from grpc_reflection.v1alpha import reflection
import sys
import os

from config import config

logger = logging.getLogger(__name__)


def serve():
    """Start gRPC server"""
    
    proto_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'proto', 'generated')
    if proto_path not in sys.path:
        sys.path.insert(0, proto_path)
    
    try:
        from proto.generated import lms_pb2, lms_pb2_grpc
        from rpc.lms_service import LMSServicer
    except ImportError as e:
        logger.error(f"Cannot start server: proto files not generated: {e}")
        return
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.GRPC_MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ]
    )
    
    lms_pb2_grpc.add_LMSServiceServicer_to_server(LMSServicer(), server)
    logger.info("✓ LMSServicer registered")
    
    SERVICE_NAMES = (
        lms_pb2.DESCRIPTOR.services_by_name['LMSService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    logger.info("✓ gRPC reflection enabled")
    
    server_address = f'[::]:{config.GRPC_PORT}'
    server.add_insecure_port(server_address)
    server.start()
    logger.info(f"✓ gRPC server started on {server_address}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(grace=5)

