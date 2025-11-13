"""
Documents RPC Client для Gateway
Подключение к ms-documents
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

try:
    from rpc_clients.generated import documents_pb2, documents_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    documents_pb2 = None
    documents_pb2_grpc = None

logger = logging.getLogger(__name__)


class DocumentsClient:
    """RPC клиент для ms-documents"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('MS_DOCUMENTS_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_DOCUMENTS_PORT', 50059))
        self.address = f'{self.host}:{self.port}'
        
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if documents_pb2_grpc:
            self.stub = documents_pb2_grpc.DocumentsServiceStub(self.channel)
            logger.info(f"DocumentsClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available")
    
    def request_document(self, document_type: str, purpose: str, requested_by: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Запросить документ"""
        if not self.stub:
            raise Exception("Documents service not available")
        
        request = documents_pb2.RequestDocumentRequest(
            document_type=document_type,
            purpose=purpose,
            requested_by=requested_by,
            notes=notes or ''
        )
        
        response = self.stub.RequestDocument(request, timeout=10)
        
        if not response.request.id:
            raise Exception(response.message or "Failed to request document")
        
        return {
            'id': response.request.id,
            'document_type': response.request.document_type,
            'purpose': response.request.purpose,
            'status': response.request.status,
            'requested_by': response.request.requested_by,
            'requested_by_name': response.request.requested_by_name,
            'requested_at': response.request.requested_at,
            'processed_at': response.request.processed_at,
            'file_path': response.request.file_path,
            'notes': response.request.notes
        }
    
    def list_requests(self, page: int = 1, page_size: int = 50,
                     requested_by: Optional[int] = None,
                     status: Optional[str] = None,
                     document_type: Optional[str] = None) -> Dict[str, Any]:
        """Список запросов"""
        if not self.stub:
            raise Exception("Documents service not available")
        
        request = documents_pb2.ListRequestsRequest(
            page=page,
            page_size=page_size,
            requested_by=requested_by or 0,
            status=status or '',
            document_type=document_type or ''
        )
        
        response = self.stub.ListRequests(request, timeout=10)
        
        requests = []
        for req in response.requests:
            requests.append({
                'id': req.id,
                'document_type': req.document_type,
                'purpose': req.purpose,
                'status': req.status,
                'requested_by': req.requested_by,
                'requested_by_name': req.requested_by_name,
                'requested_at': req.requested_at,
                'processed_at': req.processed_at,
                'file_path': req.file_path,
                'notes': req.notes
            })
        
        return {
            'requests': requests,
            'total_count': response.total_count
        }
    
    def get_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Получить запрос по ID"""
        if not self.stub:
            raise Exception("Documents service not available")
        
        request = documents_pb2.GetRequestRequest(id=request_id)
        response = self.stub.GetRequest(request, timeout=10)
        
        if not response.request.id:
            return None
        
        return {
            'id': response.request.id,
            'document_type': response.request.document_type,
            'purpose': response.request.purpose,
            'status': response.request.status,
            'requested_by': response.request.requested_by,
            'requested_by_name': response.request.requested_by_name,
            'requested_at': response.request.requested_at,
            'processed_at': response.request.processed_at,
            'file_path': response.request.file_path,
            'notes': response.request.notes
        }


_documents_client: Optional[DocumentsClient] = None


def get_documents_client() -> DocumentsClient:
    """Get singleton documents client"""
    global _documents_client
    if _documents_client is None:
        _documents_client = DocumentsClient()
    return _documents_client

