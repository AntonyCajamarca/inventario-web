"""
Renderizador generico de reportes: recibe un titulo, lineas de datos generales
(meta_lines) y una tabla (encabezados + filas), y produce los bytes de un PDF
o de una imagen PNG. Todos los reportes del sistema usan este mismo renderizador
para no duplicar la logica de dibujo.
"""

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def render_pdf(
    title: str,
    meta_lines: list[str],
    headers: list[str],
    rows: list[list[str]],
    total_line: str | None = None,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()

    elements = [Paragraph(title, styles["Title"]), Spacer(1, 0.3 * cm)]
    for line in meta_lines:
        elements.append(Paragraph(line, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    if rows:
        data = [headers] + rows
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a3542")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f2f7")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(table)
    else:
        elements.append(Paragraph("No hay datos para mostrar en este reporte.", styles["Normal"]))

    if total_line:
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(total_line, styles["Heading3"]))

    doc.build(elements)
    return buffer.getvalue()


def _get_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def render_image(
    title: str,
    meta_lines: list[str],
    headers: list[str],
    rows: list[list[str]],
    total_line: str | None = None,
) -> bytes:
    font_title = _get_font(22)
    font_header = _get_font(14)
    font_body = _get_font(13)

    col_count = max(len(headers), 1)
    col_width = 220
    row_height = 32
    width = max(col_count * col_width + 40, 600)
    height = 140 + (len(rows) + 2) * row_height + (60 if total_line else 0)
    if not rows:
        height += 40

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    y = 20
    draw.text((20, y), title, font=font_title, fill="#2a3542")
    y += 40
    for line in meta_lines:
        draw.text((20, y), line, font=font_body, fill="#555555")
        y += 22

    y += 15
    table_top = y

    # Encabezados
    draw.rectangle([20, y, width - 20, y + row_height], fill="#2a3542")
    for i, header in enumerate(headers):
        draw.text((30 + i * col_width, y + 8), str(header), font=font_header, fill="white")
    y += row_height

    # Filas
    for idx, row in enumerate(rows):
        bg = "#f1f2f7" if idx % 2 == 0 else "white"
        draw.rectangle([20, y, width - 20, y + row_height], fill=bg)
        for i, value in enumerate(row):
            draw.text((30 + i * col_width, y + 8), str(value), font=font_body, fill="#333333")
        y += row_height

    if not rows:
        draw.text((30, y + 10), "No hay datos para mostrar en este reporte.", font=font_body, fill="#777777")
        y += row_height

    draw.rectangle([20, table_top, width - 20, y], outline="#cccccc", width=1)

    if total_line:
        y += 20
        draw.text((20, y), total_line, font=font_header, fill="#2a3542")

    output = BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()
