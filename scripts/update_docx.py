import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import re
import sys

def style_table_gost(table, col_widths, col_aligns):
    # Set table borders and width
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
    
    # Set borders
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
            # remove shading
            shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
            if shd is not None:
                tcPr.remove(shd)
            # cell width
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
                        r.font.name = 'Times New Roman'
                        r.font.size = Pt(9.5)
                        r.font.bold = True
                else:
                    p.alignment = col_aligns[col_idx]
                    for r in p.runs:
                        r.font.name = 'Times New Roman'
                        r.font.size = Pt(9.0)

def main():
    doc = docx.Document('БСБД_Корецкий_ПС_ЛР1.docx')
    print(f"Loaded docx with {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables.")

    # 1. Update ER Diagram image in paragraph 18
    p18 = doc.paragraphs[18]
    # Find blip
    blips = re.findall(r'r:embed="([^"]+)"', p18._p.xml)
    if blips:
        rId = blips[0]
        part = doc.part.related_parts[rId]
        with open('images/er_diagram.png', 'rb') as img_f:
            new_img_bytes = img_f.read()
        part._blob = new_img_bytes
        print(f"Updated ER diagram image in part {part.partname} (size: {len(new_img_bytes)} bytes).")

    # 2. Iterate through all paragraphs: space_before = 0, space_after = 0
    for p in doc.paragraphs:
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        # Ensure keep_with_next on captions and images
        if p.text.startswith('Рисунок ') or p.text.startswith('Таблица '):
            p.paragraph_format.keep_with_next = True
        # Check if paragraph has images
        if 'w:drawing' in p._p.xml:
            p.paragraph_format.keep_with_next = True

    # 3. Specifically fix Figure 3 keep_with_next and pagebreak
    for i, p in enumerate(doc.paragraphs):
        if 'роль app_reader не может изменять данные (Рисунок 3)' in p.text:
            print(f"Found introductory text for Figure 3 at P{i}")
            p.paragraph_format.keep_with_next = True
            # Add page break before this paragraph so Figure 3 is never split
            pPr = p._p.get_or_add_pPr()
            pPr.append(parse_xml(r'<w:pageBreakBefore xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
            # And next paragraph is the image
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i+1].paragraph_format.keep_with_next = True

    # 4. Process all tables: remove shading, zero spacing, fix UQ, domains, positive integers
    domain_updates = {
        'Символ': "Латиница ('M', 'F')",
        'auth_factor_min': ('Целые положительные числа (1..4)', 'NOT NULL, CHECK (auth_factor_min BETWEEN 1 AND 4)'),
        'trust_tier': ('Целые положительные числа (1..5)', 'NOT NULL, CHECK (trust_tier BETWEEN 1 AND 5)'),
        'validity_years': ('Целые положительные числа (>0)', 'NOT NULL, CHECK (validity_years > 0)'),
        'client_port': ('Целые положительные числа (1..65535)', 'Допускается NULL, CHECK (client_port > 0 AND client_port <= 65535)'),
        'row_id': 'Натур. полож. числа / UUID',
    }

    for t_idx, t in enumerate(doc.tables):
        header_cells = [c.text.strip() for c in t.rows[0].cells]
        is_ddl_table = 'Атрибут' in header_cells and 'Домен' in header_cells

        for r_idx, row in enumerate(t.rows):
            # Cant split row
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
            if r_idx == 0:
                trPr.append(parse_xml(r'<w:tblHeader xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))

            # Check attribute name if ddl table
            attr_name = row.cells[0].text.strip() if is_ddl_table else ''

            for c_idx, cell in enumerate(row.cells):
                # Remove shading
                tcPr = cell._tc.get_or_add_tcPr()
                shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                if shd is not None:
                    tcPr.remove(shd)

                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)

                # DDL Table fixes
                if is_ddl_table and r_idx > 0:
                    col_name = header_cells[c_idx]

                    # Error 5: UQ is not a key!
                    if col_name == 'Ключ':
                        txt = cell.text.strip()
                        if 'UQ' in txt:
                            if 'FK' in txt:
                                cell.text = 'FK'
                            else:
                                cell.text = '–'
                            for p in cell.paragraphs:
                                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                for r in p.runs:
                                    r.font.name = 'Times New Roman'
                                    r.font.size = Pt(9.0)

                    # Ensure UNIQUE is in Ограничения
                    if col_name == 'Ограничения':
                        # If this row had UQ, ensure UNIQUE is listed
                        if attr_name in ['code', 'type_code', 'agency_code', 'inn', 'ogrn', 'snils', 'chip_uid', 'template_hash', 'token_hash']:
                            if 'UNIQUE' not in cell.text:
                                cell.text = 'NOT NULL, UNIQUE, ' + cell.text.replace('NOT NULL, ', '')
                        if attr_name == 'citizen_id' and 'digital_profiles' in doc.paragraphs[find_table_caption_p(doc, t_idx)].text:
                            if 'UNIQUE' not in cell.text:
                                cell.text = 'NOT NULL, UNIQUE, ' + cell.text.replace('NOT NULL, ', '')

                        # Specific constraint fixes
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
                                r.font.name = 'Times New Roman'
                                r.font.size = Pt(9.0)

                    # Error 6 & 7: Domain fixes
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
                        elif attr_name == 'row_id':
                            cell.text = 'Натур. полож. числа / UUID'

                        for p in cell.paragraphs:
                            for r in p.runs:
                                r.font.name = 'Times New Roman'
                                r.font.size = Pt(9.0)

    print("Finished updating DDL tables.")

    # 5. Add Table Population Section in Section 2 (Error 9)
    # Find paragraph before Section 3: "Роли и привилегии"
    sec3_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == 'Роли и привилегии':
            sec3_idx = i
            break

    print(f"Section 3 found at paragraph {sec3_idx}")

    # We will insert paragraphs and tables right before Section 3
    # In docx, inserting before a paragraph: p_target.insert_paragraph_before(...)
    p_sec3 = doc.paragraphs[sec3_idx]

    # Insert pagebreak before Section 3
    # But before that, insert the new section:
    p_heading = p_sec3.insert_paragraph_before('Наполнение таблиц тестовыми данными')
    p_heading.style = doc.styles['Normal']
    p_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_heading.paragraph_format.first_line_indent = Inches(0.49)
    p_heading.paragraph_format.space_before = Pt(0)
    p_heading.paragraph_format.space_after = Pt(0)
    p_heading.paragraph_format.line_spacing = 1.5
    for r in p_heading.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.font.bold = True

    p_intro = p_sec3.insert_paragraph_before(
        'В соответствии с требованиями лабораторной работы для всех таблиц домена базы данных было сгенерировано и загружено тестовое наполнение (не менее 10 строк в основных таблицах). Данные охватывают полный жизненный цикл цифровой идентификации: физических лиц, их подтвержденные цифровые профили, выданные электронные паспорта, биометрические векторы, юридические согласия и сессионные маркеры доступа. '
        'Фрагменты наполнения основных спроектированных таблиц приведены ниже (Таблица 30 – 35).'
    )
    p_intro.style = doc.styles['Normal']
    p_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_intro.paragraph_format.first_line_indent = Inches(0.49)
    p_intro.paragraph_format.space_before = Pt(0)
    p_intro.paragraph_format.space_after = Pt(0)
    p_intro.paragraph_format.line_spacing = 1.5
    for r in p_intro.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)

    # Function to create sample table before p_sec3
    def add_sample_table(caption_text, headers, rows_data, col_widths, col_aligns):
        p_cap = p_sec3.insert_paragraph_before(caption_text)
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.first_line_indent = Inches(0)
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(0)
        p_cap.paragraph_format.line_spacing = 1.5
        p_cap.paragraph_format.keep_with_next = True
        for r in p_cap.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(14)

        # Table
        tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        # Move table before p_sec3._p
        p_sec3._p.addprevious(tbl._tbl)

        for col_idx, h in enumerate(headers):
            tbl.cell(0, col_idx).text = h
        for row_idx, r_data in enumerate(rows_data):
            for col_idx, val in enumerate(r_data):
                tbl.cell(row_idx + 1, col_idx).text = str(val)

        style_table_gost(tbl, col_widths, col_aligns)

    # 1. ref.trust_levels
    add_sample_table(
        'Таблица 30 – Наполнение таблицы ref.trust_levels',
        ['ID', 'Код', 'Наименование', 'Мин. фак.', 'Описание', 'Активность'],
        [
            ['1', 'ANONYMOUS', 'Анонимный доступ', '1', 'Базовые открытые сервисы', 'true'],
            ['2', 'SIMPLIFIED', 'Упрощенный профиль', '1', 'Заполнение анкет без ПДн', 'true'],
            ['3', 'STANDARD', 'Стандартный профиль', '2', 'Доступ к базовым госуслугам', 'true'],
            ['4', 'CONFIRMED', 'Подтвержденный профиль', '2', 'Юридически значимые операции', 'true'],
            ['5', 'BIOMETRIC', 'Биометрический профиль', '3', 'Высокорисковые фин. сделки', 'true'],
        ],
        [0.6, 1.3, 1.4, 0.8, 1.3, 0.9],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # 2. ref.agencies
    add_sample_table(
        'Таблица 31 – Примеры наполнения таблицы ref.agencies (из 13 записей)',
        ['ID', 'Код ведомства', 'ИНН', 'ОГРН', 'Уровень', 'Наименование'],
        [
            ['1', 'MVD_MIGRATION', '7701123456', '1027700123456', '5', 'ГУВМ МВД России'],
            ['2', 'MINTSYFRA', '7710474375', '1047702026701', '5', 'Минцифры России'],
            ['3', 'FNS_RUSSIA', '7707329152', '1047707030505', '4', 'ФНС России'],
            ['4', 'SBERBANK_PJSC', '7707083893', '1027700132195', '4', 'ПАО Сбербанк'],
            ['5', 'VTB_BANK_PJSC', '7702070139', '1027739609391', '4', 'Банк ВТБ (ПАО)'],
        ],
        [0.6, 1.3, 1.1, 1.2, 0.8, 1.3],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    )

    # 3. app.citizens
    add_sample_table(
        'Таблица 32 – Примеры наполнения таблицы app.citizens (из 12 записей)',
        ['ID', 'Фамилия', 'Имя', 'Отчество', 'Дата рожд.', 'Пол', 'Место рождения'],
        [
            ['1', 'Иванов', 'Александр', 'Сергеевич', '1985-04-12', 'M', 'гор. Москва'],
            ['2', 'Смирнова', 'Елена', 'Владимировна', '1990-08-25', 'F', 'гор. Новосибирск'],
            ['3', 'Кузнецов', 'Дмитрий', 'Алексеевич', '1978-11-03', 'M', 'гор. Санкт-Петербург'],
            ['4', 'Попова', 'Анна', 'Игоревна', '1995-02-17', 'F', 'гор. Екатеринбург'],
            ['5', 'Васильев', 'Максим', 'Олегович', '2001-06-30', 'M', 'гор. Казань'],
        ],
        [0.5, 1.0, 1.0, 1.1, 0.9, 0.5, 1.3],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    )

    # 4. app.digital_profiles
    add_sample_table(
        'Таблица 33 – Примеры наполнения таблицы app.digital_profiles (из 12 записей)',
        ['ID', 'Гражд.', 'СНИЛС', 'ИНН', 'Уровень', 'Статус', 'Дата подтверждения'],
        [
            ['1', '1', '11223344556', '770112345678', '5', 'ACTIVE', '2023-01-15 10:00:00'],
            ['2', '2', '22334455667', '540198765432', '5', 'ACTIVE', '2023-02-20 11:30:00'],
            ['3', '3', '33445566778', '780145612378', '4', 'ACTIVE', '2023-03-10 14:15:00'],
            ['4', '4', '44556677889', '660167891234', '4', 'ACTIVE', '2023-04-05 09:45:00'],
            ['5', '5', '55667788990', '160123456789', '3', 'ACTIVE', '2023-05-12 16:20:00'],
        ],
        [0.5, 0.6, 1.1, 1.2, 0.7, 0.9, 1.3],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # 5. app.electronic_passports
    add_sample_table(
        'Таблица 34 – Примеры наполнения таблицы app.electronic_passports (из 24 записей)',
        ['ID', 'Гражд.', 'UID чипа', 'Серия', 'Номер', 'Выдан', 'Истекает', 'Код', 'Статус'],
        [
            ['1', '1', 'E0040100112233AA', '4515', '102030', '2020-05-10', '2030-05-10', '770-001', 'true'],
            ['2', '2', 'E0040100112233BB', '5016', '203040', '2021-06-15', '2031-06-15', '540-002', 'true'],
            ['3', '3', 'E0040100112233CC', '4017', '304050', '2019-09-20', '2029-09-20', '780-003', 'true'],
            ['4', '4', 'E0040100112233DD', '6518', '405060', '2022-01-12', '2027-01-12', '660-004', 'true'],
            ['5', '5', 'E0040100112233EE', '9219', '506070', '2021-08-22', '2031-08-22', '160-005', 'true'],
        ],
        [0.4, 0.5, 1.4, 0.6, 0.7, 0.8, 0.8, 0.6, 0.5],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # 6. audit.login_log
    add_sample_table(
        'Таблица 35 – Примеры журнала подключений audit.login_log (из 10 записей)',
        ['ID', 'Время входа', 'Пользователь', 'IP-клиента', 'Порт', 'Статус сессии'],
        [
            ['1', '2026-10-24 08:00:15', 'security_admin', '192.168.10.15', '54320', 'SUCCESS'],
            ['2', '2026-10-24 08:05:22', 'ddl_admin', '192.168.10.20', '54322', 'SUCCESS'],
            ['3', '2026-10-24 08:15:40', 'app_owner', '127.0.0.1', '54324', 'SUCCESS'],
            ['4', '2026-10-24 08:30:10', 'dml_admin', '192.168.10.25', '54326', 'SUCCESS'],
            ['5', '2026-10-24 09:00:05', 'app_writer', '10.0.5.12', '54328', 'SUCCESS'],
        ],
        [0.5, 1.4, 1.1, 1.1, 0.8, 1.4],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # Add pagebreak before Section 3 so Section 3 cleanly starts on a fresh page
    p_sec3_pr = p_sec3._p.get_or_add_pPr()
    p_sec3_pr.append(parse_xml(r'<w:pageBreakBefore xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))

    # Renumber Roles table caption from Таблица 30 to Таблица 36
    for p in doc.paragraphs:
        if 'Таблица 30 – Роли и привилегии' in p.text:
            p.text = p.text.replace('Таблица 30 – Роли и привилегии', 'Таблица 36 – Роли и привилегии')
            print("Renumbered Roles table to Таблица 36.")

    # Save to the Cyrillic files!
    # Cyrillic 'Р' = \u0420
    doc.save('БСБД_Корецкий_ПС_ЛР1.docx')
    doc.save('БСБД_КорецкийП.С._ЛР1.docx')
    doc.save('БСБД_Корецкий_П.С._ЛР1.docx')
    print("Saved all 3 standard docx files successfully.")

def find_table_caption_p(doc, t_idx):
    # Rough search of table caption paragraph
    target_text = f"Таблица {t_idx + 1}"
    for i, p in enumerate(doc.paragraphs):
        if target_text in p.text:
            return i
    return 0

if __name__ == '__main__':
    main()
