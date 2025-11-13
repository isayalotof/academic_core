"""
PDF exporter for schedule
Экспорт расписания в PDF формат
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import List, Dict
import io
import logging

logger = logging.getLogger(__name__)


class PDFExporter:
    """Экспорт расписания в PDF"""
    
    DAYS_RU = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота"
    }
    
    TIME_SLOTS = {
        1: "09:00 - 10:30",
        2: "10:45 - 12:15",
        3: "13:00 - 14:30",
        4: "14:45 - 16:15",
        5: "16:30 - 18:00",
        6: "18:15 - 19:45"
    }
    
    def export_group_schedule(
        self,
        lessons: List[Dict],
        group_name: str,
        semester: int,
        academic_year: str
    ) -> bytes:
        """
        Экспорт расписания группы в PDF
        
        Args:
            lessons: Список занятий
            group_name: Название группы
            semester: Номер семестра
            academic_year: Учебный год
            
        Returns:
            PDF file as bytes
        """
        logger.info(f"Exporting PDF for group {group_name}")
        
        buffer = io.BytesIO()
        
        # Создать документ в альбомной ориентации
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1*cm,
            title=f'Расписание группы {group_name}'
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1F4E78'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph(
            f'Расписание группы {group_name}<br/>{semester} семестр, {academic_year}',
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Подготовить данные для таблицы
        data = [['День', 'Время', 'Дисциплина', 'Преподаватель', 'Тип', 'Аудитория']]
        
        for lesson in sorted(lessons, key=lambda x: (x['day_of_week'], x['time_slot'])):
            # Обрезать длинные названия
            discipline = lesson['discipline_name'][:50]
            teacher = lesson['teacher_name'][:35]
            
            classroom = lesson.get('classroom_name', '-')
            building = lesson.get('building_name', '')
            location = f"{classroom}\n({building})" if building and classroom != '-' else classroom
            
            week_marker = ""
            week_type = lesson.get('week_type', 'both')
            if week_type == 'odd':
                week_marker = " [Ч]"
            elif week_type == 'even':
                week_marker = " [З]"
            
            data.append([
                self.DAYS_RU[lesson['day_of_week']],
                self.TIME_SLOTS.get(lesson['time_slot'], f"Пара {lesson['time_slot']}"),
                discipline + week_marker,
                teacher,
                lesson['lesson_type'],
                location
            ])
        
        # Создать таблицу
        col_widths = [2.8*cm, 2.8*cm, 7*cm, 5.5*cm, 2.5*cm, 3*cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Стилизация таблицы
        table.setStyle(TableStyle([
            # Заголовок
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Данные
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # День и время по центру
            ('ALIGN', (2, 1), (3, -1), 'LEFT'),    # Дисциплина и преподаватель влево
            ('ALIGN', (4, 1), (5, -1), 'CENTER'),  # Тип и аудитория по центру
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Границы
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            
            # Чередующийся фон
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        
        elements.append(table)
        
        # Легенда
        elements.append(Spacer(1, 0.5*cm))
        legend_style = ParagraphStyle(
            'Legend',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT
        )
        legend = Paragraph('[Ч] - числитель, [З] - знаменатель', legend_style)
        elements.append(legend)
        
        # Генерация PDF
        doc.build(elements)
        
        logger.info(f"PDF export completed: {len(lessons)} lessons")
        return buffer.getvalue()
    
    def export_teacher_schedule(
        self,
        lessons: List[Dict],
        teacher_name: str,
        semester: int,
        academic_year: str
    ) -> bytes:
        """Экспорт расписания преподавателя в PDF"""
        logger.info(f"Exporting PDF for teacher {teacher_name}")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1*cm,
            title=f'Расписание преподавателя {teacher_name}'
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#70AD47'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph(
            f'Расписание преподавателя {teacher_name}<br/>{semester} семестр, {academic_year}',
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Данные
        data = [['День', 'Время', 'Дисциплина', 'Группа', 'Тип', 'Аудитория']]
        
        for lesson in sorted(lessons, key=lambda x: (x['day_of_week'], x['time_slot'])):
            discipline = lesson['discipline_name'][:50]
            classroom = lesson.get('classroom_name', '-')
            
            data.append([
                self.DAYS_RU[lesson['day_of_week']],
                self.TIME_SLOTS.get(lesson['time_slot']),
                discipline,
                lesson['group_name'],
                lesson['lesson_type'],
                classroom
            ])
        
        # Таблица
        col_widths = [2.8*cm, 2.8*cm, 7.5*cm, 4*cm, 2.5*cm, 3*cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F5E9')])
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        return buffer.getvalue()


# Global instance
pdf_exporter = PDFExporter()

