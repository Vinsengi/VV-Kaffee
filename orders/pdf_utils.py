import io
import os
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image


def money(val: Decimal) -> str:
    return f"€{(val or Decimal('0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


def build_order_pdf(order, *, title="Order Summary", include_address=True, show_status=True):
    """
    Returns BytesIO with a nicely formatted PDF order summary.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    elements = []

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static/branding/logo.png")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=120, height=50))
    elements.append(Spacer(1, 16))

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    info_style = styles["Normal"]

    # Title
    elements.append(Paragraph(f"{title} — #{order.id}", title_style))
    elements.append(Spacer(1, 10))

    # Basic info
    cust = order.full_name or (order.user.get_full_name() if order.user else "") or (order.user.username if order.user else "")
    email = order.email or (order.user.email if order.user else "")
    elements.append(Paragraph(f"<b>Customer:</b> {cust or '—'}", info_style))
    elements.append(Paragraph(f"<b>Email:</b> {email or '—'}", info_style))
    if show_status:
        elements.append(Paragraph(f"<b>Status:</b> {order.get_status_display()}", info_style))
    elements.append(Paragraph(f"<b>Order date:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}", info_style))

    # Address block
    if include_address:
        addr_lines = [
            order.address_line1 or "",
            order.address_line2 or "",
            f"{order.postcode or ''} {order.city or ''}".strip(),
            order.country or "",
        ]
        formatted = "<br/>".join([l for l in addr_lines if l])
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("<b>Shipping address</b><br/>" + (formatted or "—"), info_style))

    elements.append(Spacer(1, 16))

    # Items table
    data = [["Product", "Grind", "Weight (g)", "Qty", "Unit", "Line total"]]
    for item in order.items.all():
        data.append([
            item.product_name_snapshot,
            item.grind or "—",
            str(item.weight_grams),
            str(item.quantity),
            money(item.unit_price),
            money(item.line_total),
        ])

    table = Table(data, colWidths=[180, 80, 70, 45, 60, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#6F4E37")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
    ]))
    elements.append(table)

    # Totals
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Order total:</b> {money(order.total)}", styles["Heading3"]))

    # Footer
    elements.append(Spacer(1, 18))
    elements.append(Paragraph(
        "Thank you for choosing Versöhnung und Vergebung Kaffee",
        styles["Italic"]
    ))

    doc.build(elements)
    buf.seek(0)
    return buf
