"""
Generador de PDFs para certificados y documentos
"""
from io import BytesIO
from datetime import datetime
from typing import Optional
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas


class CertificadoHabilitacionPDF:
    """Generador de certificados de habilitación"""
    
    def __init__(self):
        self.pagesize = A4
        self.width, self.height = self.pagesize
        
    def generar(
        self,
        codigo_habilitacion: str,
        conductor_nombre: str,
        conductor_apellidos: str,
        conductor_dni: str,
        licencia_numero: str,
        licencia_categoria: str,
        empresa_razon_social: str,
        empresa_ruc: str,
        fecha_habilitacion: datetime,
        vigencia_hasta: datetime,
        habilitado_por: str
    ) -> bytes:
        """
        Generar certificado de habilitación en PDF
        
        Args:
            codigo_habilitacion: Código único de habilitación
            conductor_nombre: Nombres del conductor
            conductor_apellidos: Apellidos del conductor
            conductor_dni: DNI del conductor
            licencia_numero: Número de licencia
            licencia_categoria: Categoría de licencia
            empresa_razon_social: Razón social de la empresa
            empresa_ruc: RUC de la empresa
            fecha_habilitacion: Fecha de habilitación
            vigencia_hasta: Fecha de vencimiento
            habilitado_por: Nombre del funcionario que habilitó
            
        Returns:
            Bytes del PDF generado
        """
        buffer = BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenedor de elementos
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulo
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Estilo para texto centrado
        center_style = ParagraphStyle(
            'CustomCenter',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Encabezado
        elements.append(Paragraph(
            "DIRECCIÓN REGIONAL DE TRANSPORTES Y COMUNICACIONES",
            title_style
        ))
        elements.append(Paragraph("PUNO", subtitle_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Título del certificado
        elements.append(Paragraph(
            "<b>CERTIFICADO DE HABILITACIÓN DE CONDUCTOR</b>",
            subtitle_style
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        # Código de habilitación
        elements.append(Paragraph(
            f"<b>Código de Habilitación:</b> {codigo_habilitacion}",
            center_style
        ))
        elements.append(Spacer(1, 0.5*cm))
        
        # Datos del conductor
        conductor_data = [
            ["<b>DATOS DEL CONDUCTOR</b>", ""],
            ["Apellidos y Nombres:", f"{conductor_apellidos}, {conductor_nombre}"],
            ["DNI:", conductor_dni],
            ["Licencia de Conducir:", licencia_numero],
            ["Categoría:", licencia_categoria],
        ]
        
        conductor_table = Table(conductor_data, colWidths=[5*cm, 10*cm])
        conductor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ]))
        
        elements.append(conductor_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Datos de la empresa
        empresa_data = [
            ["<b>DATOS DE LA EMPRESA</b>", ""],
            ["Razón Social:", empresa_razon_social],
            ["RUC:", empresa_ruc],
        ]
        
        empresa_table = Table(empresa_data, colWidths=[5*cm, 10*cm])
        empresa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ]))
        
        elements.append(empresa_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Datos de la habilitación
        habilitacion_data = [
            ["<b>DATOS DE LA HABILITACIÓN</b>", ""],
            ["Fecha de Habilitación:", fecha_habilitacion.strftime("%d/%m/%Y")],
            ["Vigencia Hasta:", vigencia_hasta.strftime("%d/%m/%Y")],
            ["Habilitado Por:", habilitado_por],
        ]
        
        habilitacion_table = Table(habilitacion_data, colWidths=[5*cm, 10*cm])
        habilitacion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ]))
        
        elements.append(habilitacion_table)
        elements.append(Spacer(1, 0.8*cm))
        
        # Generar código QR
        qr_img = self._generar_qr(codigo_habilitacion)
        if qr_img:
            elements.append(Paragraph(
                "<b>Código de Verificación:</b>",
                center_style
            ))
            elements.append(Spacer(1, 0.2*cm))
            elements.append(qr_img)
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph(
                f"<font size=8>Escanee el código QR para verificar la autenticidad del certificado</font>",
                center_style
            ))
        
        elements.append(Spacer(1, 1*cm))
        
        # Nota legal
        nota_style = ParagraphStyle(
            'Nota',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER,
            leading=10
        )
        
        elements.append(Paragraph(
            "Este certificado es válido únicamente para el conductor y empresa especificados. "
            "Cualquier alteración o falsificación será sancionada conforme a ley.",
            nota_style
        ))
        
        # Construir PDF
        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        # Obtener bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _generar_qr(self, codigo: str) -> Optional[Image]:
        """
        Generar código QR con el código de habilitación
        
        Args:
            codigo: Código de habilitación
            
        Returns:
            Imagen del código QR o None si falla
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(codigo)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar en buffer
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Crear imagen para ReportLab
            qr_image = Image(img_buffer, width=4*cm, height=4*cm)
            qr_image.hAlign = 'CENTER'
            
            return qr_image
        except Exception as e:
            print(f"Error generando QR: {e}")
            return None
    
    def _add_footer(self, canvas_obj, doc):
        """
        Agregar pie de página
        
        Args:
            canvas_obj: Canvas de ReportLab
            doc: Documento
        """
        canvas_obj.saveState()
        
        # Línea separadora
        canvas_obj.setStrokeColor(colors.HexColor('#cbd5e0'))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(2*cm, 2*cm, self.width - 2*cm, 2*cm)
        
        # Texto del pie de página
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#718096'))
        
        footer_text = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        canvas_obj.drawString(2*cm, 1.5*cm, footer_text)
        
        # Número de página
        page_num = f"Página {doc.page}"
        canvas_obj.drawRightString(self.width - 2*cm, 1.5*cm, page_num)
        
        canvas_obj.restoreState()
