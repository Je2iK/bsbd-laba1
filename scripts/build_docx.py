import re
import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_border(cell, **kwargs):
    """
    Set cell borders
    kwargs: top, bottom, left, right
    values: dict(sz=4, val='single', color='AAAAAA')
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_cell_shading(cell, color_hex="F0F0F0"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def add_page_number_to_section(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)
    
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_report_docx(output_path):
    doc = Document()
    
    # Page setup (A4: 210 x 297 mm, Left 30mm, Right 15mm, Top 20mm, Bottom 20mm)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.different_first_page_header_footer = True
    
    # Configure Normal style
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.5
    style_normal.paragraph_format.space_before = Pt(0)
    style_normal.paragraph_format.space_after = Pt(0)
    style_normal.paragraph_format.first_line_indent = Cm(1.25)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Add page number to body section (different_first_page ensures page 1 has no number)
    add_page_number_to_section(section)

    # =========================================================================
    # ТИТУЛЬНЫЙ ЛИСТ
    # =========================================================================
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n\n"
                  "ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ\n"
                  "ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ\n"
                  "ВЫСШЕГО ОБРАЗОВАНИЯ\n"
                  "«НОВОСИБИРСКИЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ»")
    r.font.size = Pt(11)

    # Line
    p_line = doc.add_paragraph()
    p_line.paragraph_format.first_line_indent = Cm(0)
    p_line.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(2)
    p_line.paragraph_format.space_after = Pt(4)
    r_line = p_line.add_run("―" * 58)
    r_line.font.size = Pt(10)
    r_line.font.color.rgb = RGBColor(120, 120, 120)

    # Кафедра ЗИ
    p_dep = doc.add_paragraph()
    p_dep.paragraph_format.first_line_indent = Cm(0)
    p_dep.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_dep = p_dep.add_run("Кафедра защиты информации")
    r_dep.font.size = Pt(13)

    # Логотип НГТУ
    if os.path.exists("images/nstu_logo.png"):
        p_logo = doc.add_paragraph()
        p_logo.paragraph_format.first_line_indent = Cm(0)
        p_logo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(14)
        p_logo.paragraph_format.space_after = Pt(14)
        r_logo = p_logo.add_run()
        r_logo.add_picture("images/nstu_logo.png", width=Cm(6.8))

    # Название работы
    p_title = doc.add_paragraph()
    p_title.paragraph_format.first_line_indent = Cm(0)
    p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("ЛАБОРАТОРНАЯ РАБОТА №1\n")
    r_title.bold = True
    r_title.font.size = Pt(16)
    
    r_sub = p_title.add_run("по дисциплине: ")
    r_sub.font.size = Pt(13)
    r_sub2 = p_title.add_run("«Безопасность систем баз данных»\n\n")
    r_sub2.bold = True
    r_sub2.italic = True
    r_sub2.font.size = Pt(13)

    r_var = p_title.add_run("Вариант: 12. Защита БД систем цифровой идентификации граждан – защита биометрических данных, электронных паспортов и единого цифрового профиля с контролем доступа по уровням доверия")
    r_var.bold = True
    r_var.font.size = Pt(13)

    # Блок подписей (таблица 1 строка, 2 колонки)
    table_sign = doc.add_table(rows=1, cols=2)
    table_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sign.autofit = False
    
    col_w = Cm(8.0)
    for row in table_sign.rows:
        row.cells[0].width = col_w
        row.cells[1].width = col_w

    cell_left = table_sign.cell(0, 0)
    p_l = cell_left.paragraphs[0]
    p_l.paragraph_format.first_line_indent = Cm(0)
    p_l.paragraph_format.line_spacing = 1.15
    r_l1 = p_l.add_run("Выполнил:\nСтудент гр. «АБ-420», «АВТФ»\n")
    r_l1.font.size = Pt(12)
    r_l2 = p_l.add_run("Корецкий П. С.\n")
    r_l2.font.size = Pt(12)
    r_l2.italic = True
    r_l3 = p_l.add_run("«___» ________ 2026г\n\n_____________________\n(подпись)")
    r_l3.font.size = Pt(10)

    cell_right = table_sign.cell(0, 1)
    p_r = cell_right.paragraphs[0]
    p_r.paragraph_format.first_line_indent = Cm(0)
    p_r.paragraph_format.line_spacing = 1.15
    r_r1 = p_r.add_run("Проверил:\nСтарший преподаватель ЗИ\n")
    r_r1.font.size = Pt(12)
    r_r2 = p_r.add_run("Питько Я. А.\n")
    r_r2.font.size = Pt(12)
    r_r2.italic = True
    r_r3 = p_r.add_run("«___» ________ 2026г\n\n_____________________\n(подпись)")
    r_r3.font.size = Pt(10)

    # Footer
    p_city = doc.add_paragraph()
    p_city.paragraph_format.first_line_indent = Cm(0)
    p_city.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_city.paragraph_format.space_before = Pt(45)
    r_city = p_city.add_run("Новосибирск 2026")
    r_city.font.size = Pt(12)

    # Page break to Section 1 (ВВЕДЕНИЕ)
    doc.add_page_break()

    # Read and parse report.typ
    with open("report.typ", "r", encoding="utf-8") as f:
        content = f.read()

    # Strip preamble up to ВВЕДЕНИЕ
    intro_start = content.find("#section-heading[ВВЕДЕНИЕ]")
    if intro_start != -1:
        body_content = content[intro_start:]
    else:
        body_content = content

    # Split by section headings
    section_pattern = re.compile(r'#section-heading\[([^\]]+)\]')
    parts = section_pattern.split(body_content)
    # parts[0] is empty, then parts[1] is title, parts[2] is section body, etc.
    
    sections = []
    for i in range(1, len(parts), 2):
        sec_title = parts[i].strip()
        sec_body = parts[i+1] if i+1 < len(parts) else ""
        sections.append((sec_title, sec_body))

    tbl_counter = 0
    fig_counter = 0

    for sec_idx, (sec_title, sec_body) in enumerate(sections):
        if sec_idx > 0:
            doc.add_page_break()

        # Add Section Heading (16pt, bold, center, no first line indent)
        h = doc.add_paragraph()
        h.paragraph_format.first_line_indent = Cm(0)
        h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(16)
        r_h = h.add_run(sec_title)
        r_h.bold = True
        r_h.font.size = Pt(16)

        # Process elements inside sec_body
        # We need to recognize:
        # 1. #cls-table([caption], ...)
        # 2. #ddl-table([caption], ...)
        # 3. #figure(table(...), caption: [...])
        # 4. #figure(image(...), caption: [...])
        # 5. Lists (1. ...)
        # 6. Paragraphs

        # Split sec_body into blocks by double newlines or typst macro boundaries
        raw_blocks = re.split(r'\n\s*\n', sec_body)

        for block in raw_blocks:
            block = block.strip()
            if not block or block.startswith("//"):
                continue

            # Remove #pagebreak()
            block = block.replace("#pagebreak()", "").strip()
            if not block:
                continue

            # Check if Figure with Image
            fig_match = re.search(r'#figure\(\s*image\("([^"]+)"[^)]*\),\s*caption:\s*\[([^\]]+)\]', block)
            if fig_match:
                img_path = fig_match.group(1).strip()
                caption_text = fig_match.group(2).strip()
                fig_counter += 1

                # If image is SVG, use PNG equivalent if available
                if img_path.endswith(".svg"):
                    png_candidate = img_path[:-4] + ".png"
                    if os.path.exists(png_candidate):
                        img_path = png_candidate

                if os.path.exists(img_path):
                    p_img = doc.add_paragraph()
                    p_img.paragraph_format.first_line_indent = Cm(0)
                    p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(10)
                    p_img.paragraph_format.space_after = Pt(4)
                    r_img = p_img.add_run()
                    # Scale based on width
                    r_img.add_picture(img_path, width=Cm(15.5))

                    p_cap = doc.add_paragraph()
                    p_cap.paragraph_format.first_line_indent = Cm(0)
                    p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_before = Pt(4)
                    p_cap.paragraph_format.space_after = Pt(18) # empty line after caption per GOST
                    r_cap = p_cap.add_run(f"Рисунок {fig_counter} – {caption_text}")
                    r_cap.font.size = Pt(14)
                continue

            # Check if cls-table
            cls_match = re.search(r'#cls-table\(\[([^\]]+)\],(.*?)\)$', block, re.DOTALL)
            if cls_match:
                tbl_counter += 1
                caption_text = cls_match.group(1).strip()
                body_tokens = re.findall(r'\[([^\]]*)\]', cls_match.group(2))
                
                # Table Caption above table, left aligned, no indent
                p_cap = doc.add_paragraph()
                p_cap.paragraph_format.first_line_indent = Cm(0)
                p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_cap.paragraph_format.space_before = Pt(10)
                p_cap.paragraph_format.space_after = Pt(4)
                r_cap = p_cap.add_run(f"Таблица {tbl_counter} – {caption_text}")
                r_cap.font.size = Pt(14)

                # Build 2-column table
                num_rows = 1 + (len(body_tokens) // 2)
                t = doc.add_table(rows=num_rows, cols=2)
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                t.autofit = False

                col_widths = (Cm(8.0), Cm(8.5))

                # Header
                t.cell(0, 0).text = "Поле"
                t.cell(0, 1).text = "Класс данных"
                for c_idx in range(2):
                    cell = t.cell(0, c_idx)
                    cell.width = col_widths[c_idx]
                    set_cell_shading(cell, "F0F0F0")
                    set_cell_border(cell)
                    p = cell.paragraphs[0]
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(10)
                        r.bold = True

                # Body rows
                for r_idx in range(len(body_tokens) // 2):
                    val_col0 = body_tokens[r_idx * 2].strip()
                    val_col1 = body_tokens[r_idx * 2 + 1].strip()
                    row_cells = t.rows[r_idx + 1].cells
                    row_cells[0].text = val_col0
                    row_cells[1].text = val_col1
                    for c_idx in range(2):
                        cell = row_cells[c_idx]
                        cell.width = col_widths[c_idx]
                        set_cell_border(cell)
                        p = cell.paragraphs[0]
                        p.paragraph_format.first_line_indent = Cm(0)
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
                        for r in p.runs:
                            r.font.name = "Times New Roman"
                            r.font.size = Pt(10)

                # Add space after table
                p_post = doc.add_paragraph()
                p_post.paragraph_format.first_line_indent = Cm(0)
                p_post.paragraph_format.space_before = Pt(0)
                p_post.paragraph_format.space_after = Pt(6)
                continue

            # Check if ddl-table
            ddl_match = re.search(r'#ddl-table\(\[([^\]]+)\],(.*?)\)$', block, re.DOTALL)
            if ddl_match:
                tbl_counter += 1
                caption_text = ddl_match.group(1).strip()
                body_tokens = re.findall(r'\[([^\]]*)\]', ddl_match.group(2))
                
                # Table Caption above table
                p_cap = doc.add_paragraph()
                p_cap.paragraph_format.first_line_indent = Cm(0)
                p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_cap.paragraph_format.space_before = Pt(10)
                p_cap.paragraph_format.space_after = Pt(4)
                r_cap = p_cap.add_run(f"Таблица {tbl_counter} – {caption_text}")
                r_cap.font.size = Pt(14)

                # 7 columns
                headers = ["Атрибут", "Название", "Тип", "Вид", "Домен", "Ключ", "Ограничения"]
                num_cols = 7
                col_widths = (Cm(2.3), Cm(2.7), Cm(1.6), Cm(2.2), Cm(2.2), Cm(1.1), Cm(4.4))

                num_rows = 1 + (len(body_tokens) // num_cols)
                t = doc.add_table(rows=num_rows, cols=num_cols)
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                t.autofit = False

                # Header
                for c_idx in range(num_cols):
                    cell = t.cell(0, c_idx)
                    cell.text = headers[c_idx]
                    cell.width = col_widths[c_idx]
                    set_cell_shading(cell, "F0F0F0")
                    set_cell_border(cell)
                    p = cell.paragraphs[0]
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(10)
                        r.bold = True

                # Body rows
                for r_idx in range(len(body_tokens) // num_cols):
                    row_cells = t.rows[r_idx + 1].cells
                    for c_idx in range(num_cols):
                        val = body_tokens[r_idx * num_cols + c_idx].strip()
                        cell = row_cells[c_idx]
                        cell.text = val
                        cell.width = col_widths[c_idx]
                        set_cell_border(cell)
                        p = cell.paragraphs[0]
                        p.paragraph_format.first_line_indent = Cm(0)
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in (2, 5) else WD_ALIGN_PARAGRAPH.LEFT
                        for r in p.runs:
                            r.font.name = "Times New Roman"
                            r.font.size = Pt(10)

                p_post = doc.add_paragraph()
                p_post.paragraph_format.first_line_indent = Cm(0)
                p_post.paragraph_format.space_before = Pt(0)
                p_post.paragraph_format.space_after = Pt(6)
                continue

            # Check if Table 15 (Соотношение схем к таблицам)
            if "table(" in block and "caption:" in block:
                cap_match = re.search(r'caption:\s*\[([^\]]+)\]', block)
                if cap_match:
                    tbl_counter += 1
                    caption_text = cap_match.group(1).strip()
                    p_cap = doc.add_paragraph()
                    p_cap.paragraph_format.first_line_indent = Cm(0)
                    p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p_cap.paragraph_format.space_before = Pt(10)
                    p_cap.paragraph_format.space_after = Pt(4)
                    r_cap = p_cap.add_run(f"Таблица {tbl_counter} – {caption_text}")
                    r_cap.font.size = Pt(14)

                    body_tokens = re.findall(r'\[([^\]]*)\]', block)
                    # Clean out strong markers if any
                    clean_tokens = [tok.replace("#strong", "").replace("[", "").replace("]", "").strip() for tok in body_tokens if tok != caption_text]
                    
                    t = doc.add_table(rows=len(clean_tokens)//2, cols=2)
                    t.alignment = WD_TABLE_ALIGNMENT.CENTER
                    t.autofit = False
                    col_widths = (Cm(5.5), Cm(11.0))

                    for r_idx in range(len(clean_tokens) // 2):
                        row_cells = t.rows[r_idx].cells
                        row_cells[0].text = clean_tokens[r_idx * 2]
                        row_cells[1].text = clean_tokens[r_idx * 2 + 1]
                        for c_idx in range(2):
                            cell = row_cells[c_idx]
                            cell.width = col_widths[c_idx]
                            set_cell_border(cell)
                            if r_idx == 0:
                                set_cell_shading(cell, "F0F0F0")
                            p = cell.paragraphs[0]
                            p.paragraph_format.first_line_indent = Cm(0)
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if r_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
                            for r in p.runs:
                                r.font.name = "Times New Roman"
                                r.font.size = Pt(10)
                                if r_idx == 0:
                                    r.bold = True

                    p_post = doc.add_paragraph()
                    p_post.paragraph_format.first_line_indent = Cm(0)
                    p_post.paragraph_format.space_before = Pt(0)
                    p_post.paragraph_format.space_after = Pt(6)
                    continue

            # Check if this block contains numbered list items
            # E.g. 1. Task... \n 2. Task...
            lines = block.split("\n")
            if any(re.match(r'^\d+\.\s+', l.strip()) for l in lines):
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    m_num = re.match(r'^(\d+\.\s+)(.*)$', line)
                    if m_num:
                        p_list = doc.add_paragraph()
                        p_list.paragraph_format.first_line_indent = Cm(1.25)
                        p_list.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        p_list.paragraph_format.line_spacing = 1.5
                        r_num = p_list.add_run(m_num.group(1))
                        r_num.font.name = "Times New Roman"
                        r_num.font.size = Pt(14)
                        
                        body_txt = m_num.group(2)
                        # Process inline formatting (*bold*)
                        subparts = re.split(r'(\*[^*]+\*)', body_txt)
                        for sp in subparts:
                            if sp.startswith("*") and sp.endswith("*"):
                                r = p_list.add_run(sp[1:-1])
                                r.bold = True
                            else:
                                r = p_list.add_run(sp)
                            r.font.name = "Times New Roman"
                            r.font.size = Pt(14)
                    else:
                        # Continuation line
                        p_cont = doc.add_paragraph()
                        p_cont.paragraph_format.first_line_indent = Cm(1.25)
                        p_cont.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        p_cont.paragraph_format.line_spacing = 1.5
                        r = p_cont.add_run(line)
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(14)
                continue

            # Standard text paragraph
            # Clean Typst escape sequences like \\[, \\], *, etc.
            clean_block = block.replace("\\[", "[").replace("\\]", "]")
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(1.25)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5

            subparts = re.split(r'(\*[^*]+\*)', clean_block)
            for sp in subparts:
                if sp.startswith("*") and sp.endswith("*"):
                    r = p.add_run(sp[1:-1])
                    r.bold = True
                else:
                    r = p.add_run(sp)
                r.font.name = "Times New Roman"
                r.font.size = Pt(14)

    doc.save(output_path)
    print(f"Successfully saved {output_path}")

if __name__ == "__main__":
    out_file = "БСБД_Корецкий_ПС_ЛР1.docx"
    create_report_docx(out_file)
