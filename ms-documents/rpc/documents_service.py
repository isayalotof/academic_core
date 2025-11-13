"""
gRPC service implementation for ms-documents
"""
import logging
from datetime import datetime
import grpc
from proto.generated import documents_pb2, documents_pb2_grpc
from services.document_service import DocumentService

logger = logging.getLogger(__name__)


class DocumentsServicer(documents_pb2_grpc.DocumentsServiceServicer):
    def __init__(self):
        self.document_service = DocumentService()
    
    def HealthCheck(self, request, context):
        return documents_pb2.HealthCheckResponse(
            status='healthy', version='1.0.0',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def RequestDocument(self, request, context):
        try:
            doc_request = self.document_service.create_request(
                document_type=request.document_type,
                purpose=request.purpose,
                requested_by=request.requested_by,
                notes=request.notes if request.notes else None
            )
            return documents_pb2.DocumentRequestResponse(request=doc_request, message="Document request created successfully")
        except Exception as e:
            logger.error(f"RequestDocument error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return documents_pb2.DocumentRequestResponse()
    
    def ListRequests(self, request, context):
        try:
            requests, total = self.document_service.list_requests(
                page=request.page or 1, page_size=request.page_size or 50,
                requested_by=request.requested_by if request.requested_by else None,
                status=request.status if request.status else None,
                document_type=request.document_type if request.document_type else None
            )
            return documents_pb2.RequestsListResponse(requests=requests, total_count=total)
        except Exception as e:
            logger.error(f"ListRequests error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return documents_pb2.RequestsListResponse()
    
    def GetRequest(self, request, context):
        try:
            doc_request = self.document_service.get_request(request.id)
            if not doc_request:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Request {request.id} not found")
                return documents_pb2.DocumentRequestResponse()
            return documents_pb2.DocumentRequestResponse(request=doc_request)
        except Exception as e:
            logger.error(f"GetRequest error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return documents_pb2.DocumentRequestResponse()

