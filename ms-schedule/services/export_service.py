"""
Export service for schedule
Сервис для экспорта расписания в различные форматы
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

from exporters.excel_exporter import excel_exporter
from exporters.pdf_exporter import pdf_exporter
from exporters.ical_exporter import ical_exporter
from services.view_service import view_service
from utils.metrics import track_export

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting schedules"""
    
    @track_export('excel')
    def export_group_to_excel(
        self,
        group_id: int,
        group_name: str,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str]:
        """
        Export group schedule to Excel
        
        Returns:
            Tuple of (file_bytes, filename)
        """
        logger.info(f"Exporting group {group_id} schedule to Excel")
        
        # Get lessons
        lessons = view_service.get_group_schedule(
            group_id=group_id,
            semester=semester,
            academic_year=academic_year,
            only_active=True
        )
        
        if not lessons:
            raise ValueError(f"No lessons found for group {group_id}")
        
        # Export to Excel
        file_bytes = excel_exporter.export_group_schedule(
            lessons=lessons,
            group_name=group_name,
            semester=semester,
            academic_year=academic_year
        )
        
        # Generate filename
        filename = f"schedule_group_{group_name}_{semester}_{academic_year}.xlsx"
        filename = filename.replace('/', '_').replace(' ', '_')
        
        logger.info(f"Excel export completed: {len(file_bytes)} bytes")
        return file_bytes, filename
    
    @track_export('excel')
    def export_teacher_to_excel(
        self,
        teacher_id: int,
        teacher_name: str,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str]:
        """Export teacher schedule to Excel"""
        logger.info(f"Exporting teacher {teacher_id} schedule to Excel")
        
        lessons = view_service.get_teacher_schedule(
            teacher_id=teacher_id,
            semester=semester,
            academic_year=academic_year,
            only_active=True
        )
        
        if not lessons:
            raise ValueError(f"No lessons found for teacher {teacher_id}")
        
        file_bytes = excel_exporter.export_teacher_schedule(
            lessons=lessons,
            teacher_name=teacher_name,
            semester=semester,
            academic_year=academic_year
        )
        
        filename = f"schedule_teacher_{teacher_name}_{semester}_{academic_year}.xlsx"
        filename = filename.replace('/', '_').replace(' ', '_')
        
        return file_bytes, filename
    
    @track_export('pdf')
    def export_group_to_pdf(
        self,
        group_id: int,
        group_name: str,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str]:
        """Export group schedule to PDF"""
        logger.info(f"Exporting group {group_id} schedule to PDF")
        
        lessons = view_service.get_group_schedule(
            group_id=group_id,
            semester=semester,
            academic_year=academic_year,
            only_active=True
        )
        
        if not lessons:
            raise ValueError(f"No lessons found for group {group_id}")
        
        file_bytes = pdf_exporter.export_group_schedule(
            lessons=lessons,
            group_name=group_name,
            semester=semester,
            academic_year=academic_year
        )
        
        filename = f"schedule_group_{group_name}_{semester}_{academic_year}.pdf"
        filename = filename.replace('/', '_').replace(' ', '_')
        
        return file_bytes, filename
    
    @track_export('pdf')
    def export_teacher_to_pdf(
        self,
        teacher_id: int,
        teacher_name: str,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str]:
        """Export teacher schedule to PDF"""
        logger.info(f"Exporting teacher {teacher_id} schedule to PDF")
        
        lessons = view_service.get_teacher_schedule(
            teacher_id=teacher_id,
            semester=semester,
            academic_year=academic_year,
            only_active=True
        )
        
        if not lessons:
            raise ValueError(f"No lessons found for teacher {teacher_id}")
        
        file_bytes = pdf_exporter.export_teacher_schedule(
            lessons=lessons,
            teacher_name=teacher_name,
            semester=semester,
            academic_year=academic_year
        )
        
        filename = f"schedule_teacher_{teacher_name}_{semester}_{academic_year}.pdf"
        filename = filename.replace('/', '_').replace(' ', '_')
        
        return file_bytes, filename
    
    @track_export('ical')
    def export_to_ical(
        self,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        semester: int,
        academic_year: str,
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[bytes, str]:
        """
        Export schedule to iCal format
        
        Args:
            entity_type: 'group', 'teacher', or 'classroom'
            entity_id: Entity ID
            entity_name: Entity name
            semester: Semester number
            academic_year: Academic year
            start_date: Start of semester
            end_date: End of semester
        """
        logger.info(f"Exporting {entity_type} {entity_id} schedule to iCal")
        
        # Get lessons based on entity type
        if entity_type == 'group':
            lessons = view_service.get_group_schedule(
                group_id=entity_id,
                semester=semester,
                academic_year=academic_year,
                only_active=True
            )
        elif entity_type == 'teacher':
            lessons = view_service.get_teacher_schedule(
                teacher_id=entity_id,
                semester=semester,
                academic_year=academic_year,
                only_active=True
            )
        elif entity_type == 'classroom':
            lessons = view_service.get_classroom_schedule(
                classroom_id=entity_id,
                semester=semester,
                academic_year=academic_year,
                only_active=True
            )
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        
        if not lessons:
            raise ValueError(f"No lessons found for {entity_type} {entity_id}")
        
        # Export to iCal
        file_bytes = ical_exporter.export_schedule(
            lessons=lessons,
            start_date=start_date,
            end_date=end_date,
            entity_type=entity_type,
            entity_name=entity_name,
            semester=semester,
            academic_year=academic_year
        )
        
        filename = f"schedule_{entity_type}_{entity_name}_{semester}_{academic_year}.ics"
        filename = filename.replace('/', '_').replace(' ', '_')
        
        return file_bytes, filename


# Global instance
export_service = ExportService()

