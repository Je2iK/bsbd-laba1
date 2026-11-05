import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
import re
import sys

def set_run_font(run, name='Times New Roman', size_pt=14, bold=None, italic=None):
    run.font.name = name
    run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    
    rPr = run._r.get_or_add_rPr()
    
    # Set rFonts
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)
    
    # Set sz (in half-points: 14pt = 28)
    half_pts = str(int(size_pt * 2))
    sz = rPr.find(qn('w:sz'))
    if sz is None:
        sz = OxmlElement('w:sz')
        rPr.append(sz)
    sz.set(qn('w:val'), half_pts)
    
    szCs = rPr.find(qn('w:szCs'))
    if szCs is None:
        szCs = OxmlElement('w:szCs')
        rPr.append(szCs)
    szCs.set(qn('w:val'), half_pts)

def style_table_gost(table, col_widths, col_aligns):
    tblPr = table._tbl.tblPr
    tblCellMar = parse_xml(r'''
        <w:tblCellMar xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:top w:w="80" w:type="dxa"/>
            <w:left w:w="100" w:type="dxa"/>
            <w:bottom w:w="80" w:type="dxa"/>
            <w:right w:w="100" w:type="dxa"/>
        </w:tblCellMar>
    ''')
    tblPr.append(tblCellMar)
    
    borders = parse_xml(r'''
        <w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

    for row_idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
        if row_idx == 0:
            trPr.append(parse_xml(r'<w:tblHeader xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
            
        for col_idx, cell in enumerate(row.cells):
            tcPr = cell._tc.get_or_add_tcPr()
            shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
            if shd is not None:
                tcPr.remove(shd)
            width_dxa = int(col_widths[col_idx] * 1440)
            tcW = parse_xml(f'<w:tcW xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:w="{width_dxa}" w:type="dxa"/>')
            tcPr.append(tcW)

            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                if row_idx == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        set_run_font(r, 'Times New Roman', 9.5, bold=True)
                else:
                    p.alignment = col_aligns[col_idx]
                    for r in p.runs:
                        set_run_font(r, 'Times New Roman', 9.0)

def main():
    doc = docx.Document('БСБД_Корецкий_ПС_ЛР1.docx')
    print(f"Loaded docx with {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables.")

    # 1. Update docDefaults to Times New Roman 14pt (sz=28)
    styles_elm = doc.styles.element
    doc_def = styles_elm.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}docDefaults')
    if doc_def is not None:
        styles_elm.remove(doc_def)

    new_doc_def = parse_xml(r'''
        <w:docDefaults xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:rPrDefault>
            <w:rPr>
              <w:rFonts w:ascii="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
              <w:sz w:val="28"/>
              <w:szCs w:val="28"/>
              <w:lang w:val="ru-RU" w:eastAsia="ru-RU" w:bidi="ar-SA"/>
            </w:rPr>
          </w:rPrDefault>
          <w:pPrDefault>
            <w:pPr>
              <w:spacing w:before="0" w:after="0" w:line="360" w:lineRule="auto"/>
            </w:pPr>
          </w:pPrDefault>
        </w:docDefaults>
    ''')
    styles_elm.insert(0, new_doc_def)
    print("Updated docDefaults to Times New Roman 14pt.")

    # 2. Update ER Diagram image in paragraph 18
    p18 = doc.paragraphs[18]
    blips = re.findall(r'r:embed="([^"]+)"', p18._p.xml)
    if blips:
        rId = blips[0]
        part = doc.part.related_parts[rId]
        with open('images/er_diagram.png', 'rb') as img_f:
            new_img_bytes = img_f.read()
        part._blob = new_img_bytes
        print(f"Updated ER diagram image in part {part.partname} (size: {len(new_img_bytes)} bytes).")

    headings_16 = [
        'ER-модель и классификация',
        'DDL и схемы',
        'Роли и привилегии',
        'Логирование подключений пользователей',
        'Выводы',
    ]

    # 3. Iterate through all paragraphs: strictly set 14pt for captions, 16pt bold for headings
    for idx, p in enumerate(doc.paragraphs):
        txt_stripped = p.text.strip()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.5

        # Check if Figure caption
        if txt_stripped.startswith('Рисунок '):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                set_run_font(r, name='Times New Roman', size_pt=14, bold=False)

        # Check if Table caption
        elif txt_stripped.startswith('Таблица '):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                set_run_font(r, name='Times New Roman', size_pt=14, bold=False)

        # Check if Section Heading
        elif txt_stripped in headings_16:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                set_run_font(r, name='Times New Roman', size_pt=16, bold=True)

        # Body paragraphs after title page (idx >= 13)
        elif idx >= 13 and not ('w:drawing' in p._p.xml):
            if txt_stripped != '':
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.first_line_indent = Inches(0.49)
                for r in p.runs:
                    # Keep run formatting (bold/italic) if any, but ensure Times New Roman 14pt
                    set_run_font(r, name='Times New Roman', size_pt=14)

        if 'w:drawing' in p._p.xml:
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 4. Check Figure 3 keep_with_next and pagebreak
    for i, p in enumerate(doc.paragraphs):
        if 'роль app_reader не может изменять данные (Рисунок 3)' in p.text:
            p.paragraph_format.keep_with_next = True
            pPr = p._p.get_or_add_pPr()
            if not pPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pageBreakBefore'):
                pPr.append(parse_xml(r'<w:pageBreakBefore xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i+1].paragraph_format.keep_with_next = True

    # 5. Process all tables: remove shading, zero spacing, fix UQ, domains, positive integers
    for t_idx, t in enumerate(doc.tables):
        header_cells = [c.text.strip() for c in t.rows[0].cells]
        is_ddl_table = 'Атрибут' in header_cells and 'Домен' in header_cells

        for r_idx, row in enumerate(t.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
            if r_idx == 0:
                trPr.append(parse_xml(r'<w:tblHeader xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))

            attr_name = row.cells[0].text.strip() if is_ddl_table else ''

            for c_idx, cell in enumerate(row.cells):
                tcPr = cell._tc.get_or_add_tcPr()
                shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                if shd is not None:
                    tcPr.remove(shd)

                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    for r in p.runs:
                        if r_idx == 0:
                            set_run_font(r, 'Times New Roman', 9.5, bold=True)
                        else:
                            set_run_font(r, 'Times New Roman', 9.0)

                # DDL Table fixes
                if is_ddl_table and r_idx > 0:
                    col_name = header_cells[c_idx]

                    if col_name == 'Ключ':
                        txt = cell.text.strip()
                        if 'UQ' in txt:
                            cell.text = 'FK' if 'FK' in txt else '–'
                            for p in cell.paragraphs:
                                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                for r in p.runs:
                                    set_run_font(r, 'Times New Roman', 9.0)

                    if col_name == 'Ограничения':
                        if attr_name in ['code', 'type_code', 'agency_code', 'inn', 'ogrn', 'snils', 'chip_uid', 'template_hash', 'token_hash']:
                            if 'UNIQUE' not in cell.text:
                                cell.text = 'NOT NULL, UNIQUE, ' + cell.text.replace('NOT NULL, ', '')
                        if attr_name == 'auth_factor_min':
                            cell.text = 'NOT NULL, CHECK (auth_factor_min BETWEEN 1 AND 4)'
                        elif attr_name == 'trust_tier':
                            cell.text = 'NOT NULL, CHECK (trust_tier BETWEEN 1 AND 5)'
                        elif attr_name == 'validity_years':
                            cell.text = 'NOT NULL, CHECK (validity_years > 0)'
                        elif attr_name == 'client_port':
                            cell.text = 'Допускается NULL, CHECK (client_port > 0 AND client_port <= 65535)'
                        
                        for p in cell.paragraphs:
                            for r in p.runs:
                                set_run_font(r, 'Times New Roman', 9.0)

                    if col_name == 'Домен':
                        if cell.text.strip() == 'Символ':
                            cell.text = "Латиница ('M', 'F')"
                        elif attr_name == 'auth_factor_min':
                            cell.text = 'Целые положительные числа (1..4)'
                        elif attr_name == 'trust_tier':
                            cell.text = 'Целые положительные числа (1..5)'
                        elif attr_name == 'validity_years':
                            cell.text = 'Целые положительные числа (>0)'
                        elif attr_name in ['trust_level_id', 'required_trust_level_id']:
                            cell.text = 'Натур. полож. числа'
                        elif attr_name == 'client_port':
                            cell.text = 'Целые положительные числа (1..65535)'
                        elif attr_name in ['far_limit', 'frr_limit', 'similarity_score']:
                            cell.text = 'Дробные положительные числа (0..1)'
                        elif attr_name == 'quality_score':
                            cell.text = 'Дробные положительные числа (0..100)'
                        elif attr_name == 'row_id':
                            cell.text = 'Натур. полож. числа / UUID'

                        for p in cell.paragraphs:
                            for r in p.runs:
                                set_run_font(r, 'Times New Roman', 9.0)

    # 6. Ensure empty line (пустая строка) after EVERY figure caption and after EVERY table!
    body = doc._body._element

    def create_empty_paragraph():
        return parse_xml(r'''
            <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                <w:pPr>
                    <w:spacing w:before="0" w:after="0" w:line="360" w:lineRule="auto"/>
                    <w:rPr>
                        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                        <w:sz w:val="28"/>
                        <w:szCs w:val="28"/>
                    </w:rPr>
                </w:pPr>
            </w:p>
        ''')

    # Add empty line after figure captions
    for child in list(body):
        if child.tag.endswith('p'):
            p = docx.text.paragraph.Paragraph(child, doc)
            txt = p.text.strip()
            if txt.startswith('Рисунок '):
                child_idx = list(body).index(child)
                next_elem = body[child_idx + 1] if child_idx + 1 < len(body) else None
                is_empty_p = False
                if next_elem is not None and next_elem.tag.endswith('p'):
                    next_p = docx.text.paragraph.Paragraph(next_elem, doc)
                    if next_p.text.strip() == '':
                        is_empty_p = True
                if not is_empty_p:
                    child.addnext(create_empty_paragraph())

    # Add empty line after tables
    for child in list(body):
        if child.tag.endswith('tbl'):
            child_idx = list(body).index(child)
            next_elem = body[child_idx + 1] if child_idx + 1 < len(body) else None
            is_empty_p = False
            if next_elem is not None and next_elem.tag.endswith('p'):
                next_p = docx.text.paragraph.Paragraph(next_elem, doc)
                if next_p.text.strip() == '':
                    is_empty_p = True
            if not is_empty_p:
                child.addnext(create_empty_paragraph())

    # Save to all 3 standard docx files!
    doc.save('БСБД_Корецкий_ПС_ЛР1.docx')
    doc.save('БСБД_КорецкийП.С._ЛР1.docx')
    doc.save('БСБД_Корецкий_П.С._ЛР1.docx')
    print("Successfully updated and saved all docx files with strict 14pt captions!")

if __name__ == '__main__':
    main()
