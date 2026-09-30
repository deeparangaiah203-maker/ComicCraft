import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from app.config import settings

def generate_image(prompt: str, panel_number: int = 1, title: str = "", art_style: str = "Comic Book", output_filename: str = None) -> str:
    """
    Generates a stylized comic panel image.
    Saves image into the static directory so the browser can serve it.
    """
    panels_dir = settings.static_dir / "panels"
    panels_dir.mkdir(parents=True, exist_ok=True)

    if not output_filename:
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
        safe_title = safe_title.replace(" ", "_")[:20] or f"panel_{panel_number}"
        output_filename = f"panel_{panel_number}_{safe_title}.png"

    output_path = panels_dir / output_filename

    # Panel dimensions (16:9 or 4:3 comic panel)
    width, height = 700, 480
    
    # Palette based on panel number to give visual variety
    color_schemes = [
        {"bg_top": (25, 30, 60), "bg_bot": (45, 60, 110), "border": (255, 215, 0), "badge": (230, 60, 80)},
        {"bg_top": (40, 20, 50), "bg_bot": (80, 40, 95), "border": (0, 210, 255), "badge": (255, 140, 0)},
        {"bg_top": (20, 45, 35), "bg_bot": (40, 85, 65), "border": (255, 230, 80), "badge": (180, 50, 200)},
        {"bg_top": (55, 25, 25), "bg_bot": (110, 50, 45), "border": (255, 165, 0), "badge": (50, 150, 250)},
        {"bg_top": (20, 25, 45), "bg_bot": (50, 40, 90), "border": (120, 255, 150), "badge": (240, 70, 70)},
    ]
    scheme = color_schemes[(panel_number - 1) % len(color_schemes)]

    # Create gradient background
    img = Image.new("RGB", (width, height), scheme["bg_top"])
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(scheme["bg_top"][0] * (1 - ratio) + scheme["bg_bot"][0] * ratio)
        g = int(scheme["bg_top"][1] * (1 - ratio) + scheme["bg_bot"][1] * ratio)
        b = int(scheme["bg_top"][2] * (1 - ratio) + scheme["bg_bot"][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Comic border (thick border)
    border_width = 8
    draw.rectangle([border_width, border_width, width - border_width, height - border_width], outline=scheme["border"], width=4)
    draw.rectangle([border_width + 4, border_width + 4, width - border_width - 4, height - border_width - 4], outline=(255, 255, 255), width=1)

    # Panel Badge
    badge_w, badge_h = 130, 40
    draw.rectangle([border_width + 10, border_width + 10, border_width + 10 + badge_w, border_width + 10 + badge_h], fill=scheme["badge"], outline=(255, 255, 255), width=2)
    draw.text((border_width + 22, border_width + 18), f"PANEL {panel_number}", fill=(255, 255, 255))

    # Art Style pill
    style_text = f"Style: {art_style}"
    draw.rectangle([width - border_width - 180, border_width + 10, width - border_width - 10, border_width + 42], fill=(20, 20, 30), outline=scheme["border"], width=1)
    draw.text((width - border_width - 165, border_width + 18), style_text, fill=(240, 240, 240))

    # Center Visual Mock Box / Comic Art simulation
    art_rect = [border_width + 30, border_width + 65, width - border_width - 30, height - border_width - 70]
    draw.rectangle(art_rect, fill=(15, 18, 32), outline=(100, 100, 140), width=2)

    # Decorative comic stars or accents
    cx = (art_rect[0] + art_rect[2]) // 2
    cy = (art_rect[1] + art_rect[3]) // 2
    
    # Draw comic scene placeholder text
    if title:
        draw.text((cx - len(title) * 4, cy - 60), f"★ {title.upper()} ★", fill=(255, 230, 100))
    
    # Wrap and display visual prompt summary
    words = prompt.split()
    lines = []
    curr_line = []
    for w in words:
        curr_line.append(w)
        if len(" ".join(curr_line)) > 55:
            lines.append(" ".join(curr_line))
            curr_line = []
    if curr_line:
        lines.append(" ".join(curr_line))

    display_lines = lines[:4]
    start_y = cy - 10
    for line in display_lines:
        draw.text((cx - len(line) * 3, start_y), line, fill=(200, 215, 240))
        start_y += 22

    # Bottom caption banner
    caption_box = [border_width + 20, height - border_width - 55, width - border_width - 20, height - border_width - 10]
    draw.rectangle(caption_box, fill=(255, 255, 235), outline=(0, 0, 0), width=2)
    draw.text((caption_box[0] + 15, caption_box[1] + 12), f"Scene: {title or 'Act ' + str(panel_number)}", fill=(20, 20, 20))

    img.save(str(output_path), "PNG")
    return f"/static/panels/{output_filename}"

def create_comic_pdf(title: str, panels: list, filename: str = None) -> str:
    """
    Creates a multi-panel comic PDF using fpdf2.
    """
    if not filename:
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
        safe_title = safe_title.replace(" ", "_")[:25] or "comic_story"
        filename = f"{safe_title}.pdf"

    pdf_path = settings.exports_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    margin = 15
    pdf.set_margins(margin, margin, margin)
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Cover / Header & First Panels
    pdf.add_page()
    
    # Header
    pdf.set_fill_color(108, 61, 244)
    pdf.rect(0, 0, 210, 32, "F")
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_y(8)
    clean_title = title.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 8, clean_title, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Generated by ComicCraft", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(38)

    for i, panel in enumerate(panels):
        # 2 panels per page
        if i > 0 and i % 2 == 0:
            pdf.add_page()
            pdf.set_y(15)

        p_num = panel.get("panel_number", i + 1)
        p_title = panel.get("title", f"Panel {p_num}")
        p_desc = panel.get("description", "")
        p_caption = panel.get("caption", "")

        clean_p_title = f"Panel {p_num}: {p_title}".encode("latin-1", "replace").decode("latin-1")
        clean_p_desc = p_desc.encode("latin-1", "replace").decode("latin-1")
        clean_p_caption = p_caption.encode("latin-1", "replace").decode("latin-1")

        pdf.set_x(margin)
        pdf.set_text_color(108, 61, 244)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 6, clean_p_title, new_x="LMARGIN", new_y="NEXT")

        # Panel Image if exists
        img_rel_url = panel.get("image_url", "")
        if img_rel_url and img_rel_url.startswith("/static/"):
            local_img_path = settings.base_dir / img_rel_url.lstrip("/")
            if local_img_path.exists():
                curr_y = pdf.get_y()
                pdf.image(str(local_img_path), x=margin, y=curr_y, w=180, h=75)
                pdf.set_y(curr_y + 78)

        pdf.set_x(margin)
        if clean_p_desc:
            pdf.set_text_color(60, 60, 60)
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(180, 4.5, f"Scene: {clean_p_desc}")
            pdf.set_x(margin)

        if clean_p_caption:
            pdf.set_text_color(20, 20, 20)
            pdf.set_font("Helvetica", "I", 9.5)
            pdf.multi_cell(180, 4.5, f'"{clean_p_caption}"')
            pdf.set_x(margin)

        pdf.ln(4)

    pdf.output(str(pdf_path))
    return f"/download/{filename}"