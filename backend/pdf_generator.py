import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_invoice_pdf(bill_data, output_path):
    """
    Generates a professional PDF invoice using ReportLab.
    bill_data: dict with keys:
      - invoice_number
      - customer_name
      - customer_email
      - customer_phone
      - customer_address
      - items: list of dicts with 'name', 'qty', 'unit_price', 'total'
      - subtotal
      - tax_rate
      - tax_amount
      - grand_total
      - notes
      - created_at
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E3A8A'),  # Deep Navy
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563')  # Slate Gray
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1F2937')
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1F2937'),
        fontName='Helvetica-Bold'
    )

    story = []

    # Header section: Company Info & Invoice Meta
    header_data = [
        [
            Paragraph("<b>YOUR BUSINESS NAME</b><br/>123 Enterprise Way, Suite 400<br/>City, State 12345<br/>contact@business.com", subtitle_style),
            Paragraph(f"<font size=22 color='#1E3A8A'><b>INVOICE</b></font><br/><b>Invoice #:</b> {bill_data.get('invoice_number', 'N/A')}<br/><b>Date:</b> {bill_data.get('created_at', 'N/A')}", ParagraphStyle('RightMeta', parent=normal_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Divider line
    divider = Table([['']], colWidths=[7.2*inch])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, colors.HexColor('#2563EB')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # Bill To Section
    customer_info = f"""
    <b>{bill_data.get('customer_name', '')}</b><br/>
    {bill_data.get('customer_address', '') + '<br/>' if bill_data.get('customer_address') else ''}
    {('Email: ' + bill_data.get('customer_email') + '<br/>') if bill_data.get('customer_email') else ''}
    {('Phone: ' + bill_data.get('customer_phone')) if bill_data.get('customer_phone') else ''}
    """
    
    bill_to_data = [
        [
            Paragraph("<b>BILL TO:</b>", section_heading),
            Paragraph("<b>PAYMENT STATUS:</b>", section_heading)
        ],
        [
            Paragraph(customer_info.strip(), normal_style),
            Paragraph("<font color='#059669'><b>PAID / PROCESSED</b></font><br/>Payment Method: Standard<br/>Thank you for your business!", normal_style)
        ]
    ]
    bill_to_table = Table(bill_to_data, colWidths=[4.2*inch, 3.0*inch])
    bill_to_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(bill_to_table)
    story.append(Spacer(1, 20))

    # Items Table
    # Headers
    table_data = [[
        Paragraph("<b>#</b>", bold_style),
        Paragraph("<b>Item Description</b>", bold_style),
        Paragraph("<b>Qty</b>", bold_style),
        Paragraph("<b>Unit Price ($)</b>", bold_style),
        Paragraph("<b>Total ($)</b>", bold_style)
    ]]

    items = bill_data.get('items', [])
    for idx, item in enumerate(items, start=1):
        name = item.get('name', 'Item')
        qty = item.get('qty', 1)
        unit_price = float(item.get('unit_price', 0.0))
        total = float(item.get('total', qty * unit_price))
        table_data.append([
            Paragraph(str(idx), normal_style),
            Paragraph(name, normal_style),
            Paragraph(str(qty), normal_style),
            Paragraph(f"{unit_price:.2f}", normal_style),
            Paragraph(f"{total:.2f}", normal_style)
        ])

    items_table = Table(table_data, colWidths=[0.5*inch, 3.7*inch, 0.8*inch, 1.1*inch, 1.1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))

    # Summary Totals Section
    subtotal = float(bill_data.get('subtotal', 0.0))
    tax_rate = float(bill_data.get('tax_rate', 0.0))
    tax_amount = float(bill_data.get('tax_amount', 0.0))
    grand_total = float(bill_data.get('grand_total', 0.0))

    summary_data = [
        [Paragraph("<b>Subtotal:</b>", normal_style), Paragraph(f"${subtotal:.2f}", normal_style)],
        [Paragraph(f"<b>Tax ({tax_rate}%):</b>", normal_style), Paragraph(f"${tax_amount:.2f}", normal_style)],
        [Paragraph("<b>Grand Total:</b>", bold_style), Paragraph(f"<b>${grand_total:.2f}</b>", bold_style)],
    ]
    summary_table = Table(summary_data, colWidths=[1.8*inch, 1.2*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#1E3A8A')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#EFF6FF')),
    ]))

    # Wrap summary with left alignment spacer
    summary_wrapper = Table([[Paragraph("", normal_style), summary_table]], colWidths=[4.2*inch, 3.0*inch])
    summary_wrapper.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(summary_wrapper)
    story.append(Spacer(1, 25))

    # Notes / Terms
    notes = bill_data.get('notes')
    if notes:
        story.append(Paragraph("<b>Notes / Terms:</b>", section_heading))
        story.append(Spacer(1, 4))
        story.append(Paragraph(notes, normal_style))
        story.append(Spacer(1, 15))

    # Footer
    footer_text = "<font color='#9CA3AF'>This is a computer-generated invoice. For inquiries, contact support@business.com</font>"
    story.append(Paragraph(footer_text, ParagraphStyle('FooterStyle', parent=normal_style, alignment=1)))

    doc.build(story)
    return output_path
