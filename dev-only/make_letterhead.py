import os
import re
import shutil
import tempfile
import zipfile

from PIL import Image, ImageDraw
from docx import Document
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.text.run import Run
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Mm, Pt, RGBColor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "SunshineHealthcareLogo.png")
WATERMARK_PATH = os.path.join(BASE_DIR, "medical image.png")
OUTPUT_PATH = os.path.join(BASE_DIR, "SunshineHealthCare_Letterhead.docx")

TMP_DIR = os.path.join(tempfile.gettempdir(), "opencode", "sunshine_letterhead")
os.makedirs(TMP_DIR, exist_ok=True)
CIRCULAR_LOGO = os.path.join(TMP_DIR, "logo_circle.png")
FADED_WATERMARK = os.path.join(TMP_DIR, "watermark_faded.png")
SUN_DOT = os.path.join(TMP_DIR, "sun_dot.png")

NAVY = RGBColor(0x07, 0x3B, 0x5C)
NAVY_HEX = "073B5C"
TURQUOISE = RGBColor(0x19, 0xB7, 0xC5)
TURQUOISE_HEX = "19B7C5"
TURQUOISE_DARK = RGBColor(0x07, 0x8D, 0x9B)
SKY_HEX = "DFF7FC"
YELLOW_HEX = "FFD166"
GRAY = RGBColor(0x60, 0x72, 0x7D)
LINK_BLUE = RGBColor(0x05, 0x63, 0xC1)

FONT_BODY = "Nunito"
FONT_SCRIPT = "Dancing Script"
FONT_FALLBACK = "Segoe UI"

WATERMARK_WIDTH = Inches(4.0)
LOGO_WIDTH = Inches(1.1)
YELLOW_DOT_SIZE = Pt(4)


def make_assets():
    if not os.path.exists(LOGO_PATH):
        raise SystemExit(f"Logo not found: {LOGO_PATH}")
    if not os.path.exists(WATERMARK_PATH):
        raise SystemExit(f"Watermark image not found: {WATERMARK_PATH}")

    logo = Image.open(LOGO_PATH).convert("RGBA")
    size = min(logo.size)
    logo = logo.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size - 1, size - 1], fill=255)
    circle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circle.paste(logo, (0, 0), mask)
    circle.save(CIRCULAR_LOGO)

    wm = Image.open(WATERMARK_PATH).convert("RGB")
    white = Image.new("RGB", wm.size, (255, 255, 255))
    faded = Image.blend(white, wm, 0.16)
    faded.save(FADED_WATERMARK)

    dot = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(dot).ellipse([6, 6, 58, 58], fill=(255, 209, 102, 255))
    dot.save(SUN_DOT)


def set_run(run, text=None, font=FONT_BODY, size=10, color=NAVY, bold=False, italic=False, underline=False):
    if text is not None:
        run.text = text
    run.font.name = font
    run.font.size = size
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.underline = underline
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:cs"), font)


def add_hyperlink(paragraph, url, text, size=Pt(8.5), color=LINK_BLUE, underline=True):
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    run = Run(OxmlElement("w:r"), paragraph)
    set_run(run, text=text, font=FONT_BODY, size=size, color=color, underline=underline)
    hyperlink.append(run._element)
    paragraph._p.append(hyperlink)
    return hyperlink


def shade_paragraph(p, fill):
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def border_paragraph(p, side="bottom", color=TURQUOISE_HEX, sz="16", space="3"):
    ppr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    edge = OxmlElement("w:" + side)
    edge.set(qn("w:val"), "single")
    edge.set(qn("w:sz"), sz)
    edge.set(qn("w:space"), space)
    edge.set(qn("w:color"), color)
    pbdr.append(edge)
    ppr.append(pbdr)


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def remove_table_borders(table):
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for side in ("val", "left", "right", "top", "bottom", "insideH", "insideV"):
        borders.set(qn("w:" + side), "none")
    tblpr.append(borders)


def float_behind(picture, section):
    inline = picture._inline
    drawing = inline.getparent()
    extent = inline.find(qn("wp:extent"))
    cx = extent.get("cx")
    cy = extent.get("cy")
    posv = (int(section.page_height) - int(cy)) // 2
    anchor_xml = (
        '<wp:anchor xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
        'distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="251658240" '
        'behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="page"><wp:align>center</wp:align></wp:positionH>'
        '<wp:positionV relativeFrom="page"><wp:posOffset>{posv}</wp:posOffset></wp:positionV>'
        '<wp:extent cx="{cx}" cy="{cy}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:wrapNone/>'
        "</wp:anchor>"
    ).format(posv=posv, cx=cx, cy=cy)
    anchor = parse_xml(anchor_xml)
    docpr = inline.find(qn("wp:docPr"))
    cnvfr = inline.find(qn("wp:cNvGraphicFramePr"))
    graphic = inline.find(qn("a:graphic"))
    if docpr is not None:
        anchor.append(docpr)
    if cnvfr is not None:
        anchor.append(cnvfr)
    if graphic is not None:
        anchor.append(graphic)
    drawing.replace(inline, anchor)


def add_watermark(doc, section):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    pic = p.add_run().add_picture(FADED_WATERMARK, width=WATERMARK_WIDTH)
    float_behind(pic, section)


def embed_dancing_script(docx_path):
    regular = os.path.join(TMP_DIR, "DancingScript_400.ttf")
    bold = os.path.join(TMP_DIR, "DancingScript_700.ttf")
    for f in (regular, bold):
        if not os.path.exists(f):
            print("Warning: Dancing Script static font missing, embedding skipped:", f)
            return
    rel_id_reg = "rIdEmbDancingReg"
    rel_id_bold = "rIdEmbDancingBold"
    part_reg = "word/fonts/DancingScript-Regular.ttf"
    part_bold = "word/fonts/DancingScript-Bold.ttf"
    rels_name = "word/_rels/fontTable.xml.rels"
    tmp_out = docx_path + ".tmp"
    reg_data = open(regular, "rb").read()
    bold_data = open(bold, "rb").read()
    with zipfile.ZipFile(docx_path, "r") as zin:
        names = zin.namelist()
        entries = {n: zin.read(n) for n in names}

    font_table = entries["word/fontTable.xml"].decode("utf-8")
    new_entry = (
        '<w:font w:name="Dancing Script">'
        '<w:embedRegular r:id="%s"/><w:embedBold r:id="%s"/></w:font></w:fonts>'
    ) % (rel_id_reg, rel_id_bold)
    font_table = font_table.replace("</w:fonts>", new_entry, 1)

    settings = entries["word/settings.xml"].decode("utf-8")
    settings = settings[:-len("</w:settings>")] + "<w:embedTrueTypeFonts/><w:saveSubsetFonts/></w:settings>"

    if rels_name in entries:
        font_rels = entries[rels_name].decode("utf-8")
    else:
        font_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            "</Relationships>"
        )
    rel_tpl = (
        '<Relationship Id="%s" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" '
        'Target="fonts/%s"/>'
    )
    font_rels = font_rels.replace(
        "</Relationships>",
        rel_tpl % (rel_id_reg, "DancingScript-Regular.ttf")
        + rel_tpl % (rel_id_bold, "DancingScript-Bold.ttf")
        + "</Relationships>",
        1,
    )

    content_types = entries["[Content_Types].xml"].decode("utf-8")
    if 'Extension="ttf"' not in content_types:
        content_types = content_types.replace(
            "</Types>", '<Default Extension="ttf" ContentType="application/x-font-ttf"/></Types>', 1
        )

    with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zout:
        written = set()
        for n in names:
            if n in written:
                continue
            written.add(n)
            if n == "word/fontTable.xml":
                zout.writestr(n, font_table)
            elif n == "word/settings.xml":
                zout.writestr(n, settings)
            elif n == rels_name:
                zout.writestr(n, font_rels)
            elif n == "[Content_Types].xml":
                zout.writestr(n, content_types)
            elif n in (part_reg, part_bold):
                continue
            else:
                zout.writestr(n, entries[n])
        if rels_name not in written:
            zout.writestr(rels_name, font_rels)
        zout.writestr(part_reg, reg_data)
        zout.writestr(part_bold, bold_data)

    shutil.move(tmp_out, docx_path)


def build_letterhead():
    make_assets()
    doc = Document()
    core = doc.core_properties
    core.title = "Sunshine Health Care Clinic Letterhead"
    core.subject = "Shoppe 37B, Gateway Mall, Carletonville"
    core.author = "Sunshine Health Care"

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(18)
    section.bottom_margin = Mm(24)
    section.left_margin = Mm(18)
    section.right_margin = Mm(18)
    section.footer_distance = Mm(6)

    default = doc.styles["Normal"]
    default.font.name = FONT_BODY
    default.font.size = Pt(10)
    default.font.color.rgb = NAVY

    add_watermark(doc, section)

    strip = doc.add_paragraph()
    strip.paragraph_format.space_before = Pt(0)
    strip.paragraph_format.space_after = Pt(2)
    strip.paragraph_format.line_spacing = Pt(5)
    shade_paragraph(strip, TURQUOISE_HEX)
    r = strip.add_run(" ")
    set_run(r, size=Pt(5))

    header = doc.add_table(rows=1, cols=2)
    header.alignment = WD_TABLE_ALIGNMENT.LEFT
    header.autofit = False
    remove_table_borders(header)
    left, right = header.rows[0].cells
    left.width = Inches(4.35)
    right.width = Inches(2.5)
    left.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    right.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    shade_cell(right, "FFFFFF")

    nested = left.add_table(rows=1, cols=2)
    nested.autofit = False
    remove_table_borders(nested)
    nl, nt = nested.rows[0].cells
    nl.width = Inches(1.3)
    nt.width = Inches(2.95)
    nl.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    nt.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    for p in (left.paragraphs[0], left.paragraphs[-1]):
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(2)

    lead = nl.paragraphs[0]
    lead._element.getparent().remove(lead._element)

    logo_p = nl.add_paragraph()
    logo_p.paragraph_format.space_before = Pt(0)
    logo_p.paragraph_format.space_after = Pt(0)
    logo_p.add_run().add_picture(CIRCULAR_LOGO, width=LOGO_WIDTH)

    brand_p = nt.paragraphs[0]
    brand_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    brand_p.paragraph_format.space_before = Pt(0)
    brand_p.paragraph_format.space_after = Pt(1)
    brand_p.paragraph_format.line_spacing = Pt(40)
    set_run(brand_p.add_run("Sunshine"), font=FONT_SCRIPT, size=Pt(34), color=NAVY, bold=True)

    tag_p = nt.add_paragraph()
    tag_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tag_p.paragraph_format.space_before = Pt(0)
    tag_p.paragraph_format.space_after = Pt(3)
    tag_p.paragraph_format.line_spacing = Pt(20)
    set_run(tag_p.add_run("Health Care"), font=FONT_SCRIPT, size=Pt(18), color=TURQUOISE_DARK)

    slogan_p = nt.add_paragraph()
    slogan_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    slogan_p.paragraph_format.space_before = Pt(0)
    slogan_p.paragraph_format.space_after = Pt(0)
    set_run(slogan_p.add_run("We strive for excellence"), font=FONT_BODY, size=Pt(9), color=NAVY, italic=True)

    def contact_line(text, color=NAVY, size=Pt(8.5), bold=False):
        cp = right.paragraphs[0] if text == "" else right.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        cp.paragraph_format.space_after = Pt(1)
        cp.paragraph_format.line_spacing = Pt(12.5)
        set_run(cp.add_run(text), size=size, color=color, bold=bold)

    def contact_link(label, url, size=Pt(8.5)):
        cp = right.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        cp.paragraph_format.space_after = Pt(1)
        cp.paragraph_format.line_spacing = Pt(12.5)
        add_hyperlink(cp, url, label, size=size)

    contact_line("", size=Pt(1))
    contact_line("VISIT US", color=TURQUOISE_DARK, size=Pt(7.5), bold=True)
    contact_line("Shop 37B, Gateway Mall")
    contact_line("inside Phelang Pharmacy")
    contact_line("2 Osmium Street")
    contact_line("Carletonville, 2499")
    contact_line("", size=Pt(1))
    contact_line("CONTACT", color=TURQUOISE_DARK, size=Pt(7.5), bold=True)
    contact_link("Tel +27 81 248 1247", "tel:+27812481247")
    contact_link("WhatsApp +27 79 213 1692", "https://wa.me/27792131692")
    contact_link("sunshinehealth21@gmail.com", "mailto:sunshinehealth21@gmail.com")
    contact_line("", size=Pt(1))
    contact_line("ONLINE", color=TURQUOISE_DARK, size=Pt(7.5), bold=True)
    contact_link("www.sunshinehealthcare.co.za", "https://www.sunshinehealthcare.co.za/")

    divider = doc.add_paragraph()
    divider.paragraph_format.space_before = Pt(8)
    divider.paragraph_format.space_after = Pt(2)
    divider.paragraph_format.line_spacing = Pt(10)
    border_paragraph(divider, "bottom", TURQUOISE_HEX, "16", "4")
    dot = divider.add_run().add_picture(SUN_DOT, height=YELLOW_DOT_SIZE, width=None)
    del dot

    date_p = doc.add_paragraph()
    date_p.paragraph_format.tab_stops.add_tab_stop(Inches(6.35), WD_TAB_ALIGNMENT.RIGHT)
    date_p.paragraph_format.space_before = Pt(12)
    date_p.paragraph_format.space_after = Pt(2)
    set_run(date_p.add_run("Date: "), size=Pt(11), color=NAVY, bold=True)
    set_run(date_p.add_run("_" * 62), size=Pt(11), color=GRAY)
    date_p.add_run("\t")

    ref_p = doc.add_paragraph()
    ref_p.paragraph_format.tab_stops.add_tab_stop(Inches(6.35), WD_TAB_ALIGNMENT.RIGHT)
    ref_p.paragraph_format.space_after = Pt(8)
    set_run(ref_p.add_run("Reference: "), size=Pt(11), color=NAVY, bold=True)
    set_run(ref_p.add_run("_" * 50), size=Pt(11), color=GRAY)
    ref_p.add_run("\t")

    greeting = doc.add_paragraph()
    greeting.paragraph_format.space_before = Pt(4)
    greeting.paragraph_format.space_after = Pt(6)
    set_run(greeting.add_run("Dear Sir / Madam,"), size=Pt(11), color=NAVY, bold=True)

    for _ in range(12):
        blank = doc.add_paragraph()
        blank.paragraph_format.space_before = Pt(0)
        blank.paragraph_format.space_after = Pt(13)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(2)
    fp.paragraph_format.space_after = Pt(4)
    border_paragraph(fp, "top", NAVY_HEX, "16", "6")
    set_run(fp.add_run("Sr Sylvia P Mngadi"), size=Pt(9.5), color=NAVY, bold=True)
    set_run(fp.add_run("  \u00b7  Private Nurse Practitioner  \u00b7  Practice No. 0881724  \u00b7  SANC 15208622  \u00b7  T/A Phelang Pharmacy Clinic"),
            size=Pt(9.5), color=NAVY)
    web = footer.add_paragraph()
    web.alignment = WD_ALIGN_PARAGRAPH.CENTER
    web.paragraph_format.space_before = Pt(1)
    web.paragraph_format.space_after = Pt(0)
    add_hyperlink(web, "https://www.sunshinehealthcare.co.za/", "www.sunshinehealthcare.co.za", size=Pt(8.5), color=NAVY, underline=False)
    set_run(web.add_run("  \u00b7  "), size=Pt(8.5), color=NAVY)
    add_hyperlink(web, "mailto:sunshinehealth21@gmail.com", "sunshinehealth21@gmail.com", size=Pt(8.5), color=NAVY, underline=False)
    set_run(web.add_run("  \u00b7  "), size=Pt(8.5), color=NAVY)
    add_hyperlink(web, "tel:+27812481247", "+27 81 248 1247", size=Pt(8.5), color=NAVY, underline=False)

    doc.save(OUTPUT_PATH)
    embed_dancing_script(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH} (Dancing Script embedded)")


if __name__ == "__main__":
    build_letterhead()