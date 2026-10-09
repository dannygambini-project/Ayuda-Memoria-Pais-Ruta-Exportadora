import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numeración precisa 'Página X de Y' y membrete"""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        width, height = letter

        # Banda superior institucional PROMPERÚ
        self.setFillColor(colors.HexColor('#C8102E'))
        self.rect(0, height - 6, width, 6, fill=True, stroke=False)

        # Pie de página institucional
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#6B7280'))
        
        # Línea divisoria pie de página
        self.setStrokeColor(colors.HexColor('#E5E7EB'))
        self.setLineWidth(0.75)
        self.line(36, 30, width - 36, 30)

        # Textos de pie de página
        self.drawString(36, 18, "PROMPERÚ — Dirección de Promoción de las Exportaciones | DPPM 2026")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(width - 36, 18, page_str)
        self.restoreState()

def generate_pdf(report_data: dict) -> io.BytesIO:
    """
    Genera un informe PDF ejecutivo de alta calidad institucional
    utilizando ReportLab Platypus y la paleta de PROMPERÚ.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Estilos tipográficos
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#C8102E'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor('#1F2937'),
        alignment=TA_JUSTIFY,
        spaceAfter=9
    )

    heading_style = ParagraphStyle(
        'DocSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#111827'),
        spaceBefore=8,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1F2937'),
        alignment=TA_LEFT
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=TA_CENTER
    )

    kpi_title_style = ParagraphStyle(
        'KPITitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#6B7280'),
        alignment=TA_CENTER
    )

    kpi_value_style = ParagraphStyle(
        'KPIValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        textColor=colors.HexColor('#C8102E'),
        alignment=TA_CENTER
    )

    kpi_sub_style = ParagraphStyle(
        'KPISub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#4B5563'),
        alignment=TA_CENTER
    )

    elements = []

    # 1. ENCABEZADO
    elements.append(Paragraph(report_data.get('title', 'Ayuda memoria'), title_style))
    elements.append(Paragraph(report_data.get('subtitle', ''), subtitle_style))
    
    fecha_emision = datetime.now().strftime("%d/%m/%Y")
    meta_text = f"Generado el: {fecha_emision} | Base Ruta Exportadora (RUTEX) y Exportaciones Oficiales | PROMPERÚ"
    elements.append(Paragraph(meta_text, meta_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB'), spaceBefore=2, spaceAfter=10))

    # 2. TARJETAS KPI
    m = report_data.get('metrics', {})
    var_sign = "+" if m.get('is_positive') else ""
    var_color = "#16A34A" if m.get('is_positive') else "#DC2626"

    kpi_data = [
        [
            Paragraph("EMPRESAS RUTEX", kpi_title_style),
            Paragraph("PARTIDAS ÚNICAS", kpi_title_style),
            Paragraph("EXPORTACIONES 2025", kpi_title_style),
            Paragraph("EXPORTACIONES 2024", kpi_title_style),
            Paragraph("VARIACIÓN INTERANUAL", kpi_title_style),
        ],
        [
            Paragraph(f"{m.get('cant_empresas_rutex', 0)}", kpi_value_style),
            Paragraph(f"{m.get('cant_productos_rutex', 0)}", kpi_value_style),
            Paragraph(f"USD {m.get('fob_2025_millones', 0.0):.1f}M", kpi_value_style),
            Paragraph(f"USD {m.get('fob_2024_millones', 0.0):.1f}M", kpi_value_style),
            Paragraph(f"<font color='{var_color}'><b>{var_sign}{m.get('var_pct', 0.0):.2f}%</b></font>", kpi_value_style),
        ],
        [
            Paragraph("Atendidas en 2026", kpi_sub_style),
            Paragraph("Productos exportados", kpi_sub_style),
            Paragraph("Enero - Diciembre", kpi_sub_style),
            Paragraph("Enero - Diciembre", kpi_sub_style),
            Paragraph(f"{m.get('tipo_var', '').capitalize()}", kpi_sub_style),
        ]
    ]

    col_w = (doc.width) / 5.0
    kpi_table = Table(kpi_data, colWidths=[col_w]*5)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 14))

    # 3. TEXTOS OFICIALES
    paragraphs = report_data.get('paragraphs', {})
    elements.append(Paragraph(paragraphs.get('p1', ''), body_style))
    elements.append(Paragraph(paragraphs.get('p2', ''), body_style))
    elements.append(Spacer(1, 6))

    # 4. TABLA TOP 15 EVENTOS
    elements.append(Paragraph(paragraphs.get('events_heading', 'Los principales programas en donde participaron las empresas fueron:'), heading_style))

    top_eventos = report_data.get('top_eventos', [])
    if top_eventos:
        table_rows = [
            [
                Paragraph("<b>#</b>", table_header_style),
                Paragraph("<b>PROGRAMA / EVENTO DE RUTA EXPORTADORA</b>", table_header_style),
                Paragraph("<b>EMPRESAS PARTICIPANTES</b>", ParagraphStyle('THC', parent=table_header_style, alignment=TA_CENTER))
            ]
        ]
        
        for ev in top_eventos:
            rank = ev.get('rank', 1)
            nom = ev.get('evento', '')
            emp = ev.get('empresas', 0)
            emp_txt = f"<b>{emp}</b> empresa" if emp == 1 else f"<b>{emp}</b> empresas"

            table_rows.append([
                Paragraph(f"<b>{rank}</b>", table_cell_center),
                Paragraph(nom, table_cell_style),
                Paragraph(emp_txt, table_cell_center)
            ])

        # Ancho de columnas: rank (28), evento (restante), empresas (95)
        w_rank = 28
        w_emp = 95
        w_ev = doc.width - w_rank - w_emp

        ev_table = Table(table_rows, colWidths=[w_rank, w_ev, w_emp])
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C8102E')),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ]

        # Colores alternos
        for r_idx in range(1, len(table_rows)):
            bg = colors.HexColor('#FFFFFF') if r_idx % 2 != 0 else colors.HexColor('#F8FAFC')
            t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg))

        ev_table.setStyle(TableStyle(t_style))
        elements.append(ev_table)
    else:
        elements.append(Paragraph("No se registraron eventos o programas para las empresas exportadoras a este destino.", body_style))

    # Construir PDF con el NumberedCanvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
