try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, HRFlowable
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_ai_pdf_report(image_model, output_path):
    """
    Generate a styled PDF AI Analysis Report for an image record using ReportLab.
    """
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not HAS_REPORTLAB:
        # Fallback text summary report if reportlab package is not installed
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"VisionBoard AI Analysis Report\n")
            f.write(f"Image ID: #{image_model.id} - {image_model.original_filename}\n")
            f.write(f"Quality Score: {image_model.quality_score}/100\n")
            f.write(f"Caption: {image_model.captions[0].generated_caption if image_model.captions else 'N/A'}\n")
            f.write(f"Objects: {[o.object_name for o in image_model.objects]}\n")
            f.write(f"Colors: {[c.hex_code for c in image_model.colors]}\n")
        return output_path

    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#00F2FE')
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#64748B')
    )

    heading2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B')
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Header
    story.append(Paragraph("VisionBoard AI — Image Analysis Report", title_style))
    story.append(Paragraph(f"Generated for Image ID #{image_model.id} • {image_model.original_filename}", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3B82F6'), spaceAfter=15))

    # General Information Table
    gen_data = [
        [Paragraph("<b>Original Filename:</b>", body_style), Paragraph(image_model.original_filename, body_style)],
        [Paragraph("<b>Dimensions:</b>", body_style), Paragraph(f"{image_model.image_width} x {image_model.image_height} px", body_style)],
        [Paragraph("<b>Quality Score:</b>", body_style), Paragraph(f"<b>{image_model.quality_score}/100</b>", body_style)],
        [Paragraph("<b>Status:</b>", body_style), Paragraph(image_model.processing_status.upper(), body_style)],
        [Paragraph("<b>Duplicate Alert:</b>", body_style), Paragraph("Yes (Near duplicate detected)" if image_model.is_duplicate else "No (Unique image)", body_style)]
    ]
    gen_table = Table(gen_data, colWidths=[140, 380])
    gen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(gen_table)
    story.append(Spacer(1, 15))

    # AI Caption Section
    story.append(Paragraph("1. AI Generated Caption (BLIP Model)", heading2_style))
    caption_text = image_model.captions[0].generated_caption if image_model.captions else "No caption available."
    story.append(Paragraph(f"<i>\"{caption_text}\"</i>", body_style))
    story.append(Spacer(1, 15))

    # Detected Objects Section
    story.append(Paragraph("2. Detected Objects (YOLOv8 Model)", heading2_style))
    obj_rows = [["Object Label", "Confidence", "Bounding Box Coordinates (X, Y, W, H)"]]
    if image_model.objects:
        for obj in image_model.objects:
            box_str = f"({obj.x:.2f}, {obj.y:.2f}, {obj.width:.2f}, {obj.height:.2f})"
            obj_rows.append([obj.object_name, f"{int(obj.confidence * 100)}%", box_str])
    else:
        obj_rows.append(["None Detected", "-", "-"])
    
    obj_table = Table(obj_rows, colWidths=[160, 100, 260])
    obj_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(obj_table)
    story.append(Spacer(1, 15))

    # Dominant Colors Palette
    story.append(Paragraph("3. Dominant Color Palette (K-Means Clustering)", heading2_style))
    color_rows = [["Hex Code", "RGB Format", "Coverage Percentage"]]
    if image_model.colors:
        for col in image_model.colors:
            color_rows.append([col.hex_code, col.rgb_value, f"{col.percentage}%"])
    else:
        color_rows.append(["-", "-", "-"])
    
    color_table = Table(color_rows, colWidths=[150, 200, 170])
    color_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(color_table)
    story.append(Spacer(1, 15))

    # OCR Extracted Text Section
    story.append(Paragraph("4. OCR Extracted Text (EasyOCR)", heading2_style))
    if image_model.texts:
        ocr_str = ", ".join([t.text for t in image_model.texts])
        story.append(Paragraph(f"<b>Extracted Text:</b> {ocr_str}", body_style))
    else:
        story.append(Paragraph("<i>No embedded text detected in image.</i>", body_style))
    story.append(Spacer(1, 15))

    # Auto Tags Section
    story.append(Paragraph("5. AI Auto-Generated Tags", heading2_style))
    tag_str = ", ".join([t.tag_name for t in image_model.tags]) if image_model.tags else "None"
    story.append(Paragraph(f"<b>Tags:</b> {tag_str}", body_style))

    doc.build(story)
    return output_path
