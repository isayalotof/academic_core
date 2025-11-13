"""
gRPC Server setup for ms-schedule
Настройка и запуск gRPC сервера
"""

import grpc
from concurrent import futures
import logging

# Import generated code (after proto generation)
# from proto.generated import schedule_pb2_grpc
from rpc.schedule_service import schedule_servicer
from config import config
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)


def serve():
    """
    Start gRPC server
    """
    # Create server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.GRPC_MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', config.GRPC_MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', config.GRPC_MAX_MESSAGE_LENGTH),
        ]
    )
    
    # Add servicer to server
    # After proto generation:
    # schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(
    #     schedule_servicer,
    #     server
    # )
    
    # Bind to port
    server.add_insecure_port(f'[::]:{config.GRPC_PORT}')
    
    # Start Prometheus metrics server
    try:
        start_http_server(9090)  # Metrics on port 9090
        logger.info("✅ Prometheus metrics server started on port 9090")
    except Exception as e:
        logger.warning(f"⚠️  Failed to start metrics server: {e}")
    
    # Start server
    server.start()
    logger.info(f"✅ gRPC server started on port {config.GRPC_PORT}")
    logger.info(f"   Service: {config.SERVICE_NAME} v{config.SERVICE_VERSION}")
    logger.info(f"   Workers: {config.GRPC_MAX_WORKERS}")
    logger.info(f"   Environment: {config.ENVIRONMENT}")
    
    # Wait for termination
    server.wait_for_termination()


if __name__ == '__main__':
    from utils.logger import logger
    serve()

