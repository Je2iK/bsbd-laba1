import os
import subprocess

def generate_perfect_er():
    tables = [
        # Col 1: REF (x = 50, w = 270)
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 50, 'y': 90, 'w': 270,
            'cols': [
                ('trust_level_id', 'INT', 'PK'),
                ('code', 'VARCHAR(30)', 'UQ'),
                ('name', 'VARCHAR(100)', ''),
                ('auth_factor_min', 'INT', ''),
                ('description', 'TEXT', ''),
                ('is_active', 'BOOLEAN', '')
            ]
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 50, 'y': 280, 'w': 270,
            'cols': [
                ('doc_type_id', 'INT', 'PK'),
                ('type_code', 'VARCHAR(30)', 'UQ'),
                ('type_name', 'VARCHAR(150)', ''),
                ('has_rfid_chip', 'BOOLEAN', ''),
                ('validity_years', 'INT', '')
            ]
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 50, 'y': 470, 'w': 270,
            'cols': [
                ('modality_id', 'INT', 'PK'),
                ('code', 'VARCHAR(30)', 'UQ'),
                ('name', 'VARCHAR(100)', ''),
                ('iso_standard', 'VARCHAR(100)', ''),
                ('far_limit', 'NUMERIC(8,6)', ''),
                ('frr_limit', 'NUMERIC(8,6)', '')
            ]
        },
        {
            'schema': 'ref', 'name': 'agencies', 'x': 50, 'y': 680, 'w': 270,
            'cols': [
                ('agency_id', 'INT', 'PK'),
                ('agency_code', 'VARCHAR(50)', 'UQ'),
                ('agency_name', 'VARCHAR(255)', ''),
                ('inn', 'VARCHAR(12)', 'UQ'),
                ('ogrn', 'VARCHAR(15)', 'UQ'),
                ('trust_tier', 'INT', ''),
                ('is_active', 'BOOLEAN', '')
            ]
        },

        # Col 2: APP CORE (x = 440, w = 280)
        {
            'schema': 'app', 'name': 'citizens', 'x': 440, 'y': 90, 'w': 280,
            'cols': [
                ('citizen_id', 'BIGINT', 'PK'),
                ('first_name', 'VARCHAR(100)', ''),
                ('last_name', 'VARCHAR(100)', ''),
                ('middle_name', 'VARCHAR(100)', ''),
                ('birth_date', 'DATE', ''),
                ('birth_place', 'VARCHAR(255)', ''),
                ('gender', 'CHAR(1)', ''),
                ('created_at', 'TIMESTAMPTZ', '')
            ]
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 440, 'y': 320, 'w': 280,
            'cols': [
                ('profile_id', 'BIGINT', 'PK'),
                ('citizen_id', 'BIGINT', 'FK UQ'),
                ('snils', 'CHAR(11)', 'UQ'),
                ('inn', 'VARCHAR(12)', 'UQ'),
                ('trust_level_id', 'INT', 'FK'),
                ('profile_status', 'VARCHAR(30)', ''),
                ('verified_at', 'TIMESTAMPTZ', ''),
                ('created_at', 'TIMESTAMPTZ', '')
            ]
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 440, 'y': 560, 'w': 280,
            'cols': [
                ('passport_id', 'BIGINT', 'PK'),
                ('citizen_id', 'BIGINT', 'FK'),
                ('doc_type_id', 'INT', 'FK'),
                ('chip_uid', 'VARCHAR(64)', 'UQ'),
                ('series', 'CHAR(4)', ''),
                ('number', 'CHAR(6)', ''),
                ('issue_date', 'DATE', ''),
                ('expiry_date', 'DATE', ''),
                ('issuing_authority_code', 'VARCHAR(10)', ''),
                ('encrypted_chip_payload', 'BYTEA', ''),
                ('is_active', 'BOOLEAN', '')
            ]
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 440, 'y': 860, 'w': 280,
            'cols': [
                ('biometric_id', 'BIGINT', 'PK'),
                ('citizen_id', 'BIGINT', 'FK'),
                ('modality_id', 'INT', 'FK'),
                ('template_hash', 'CHAR(64)', 'UQ'),
                ('encrypted_template', 'BYTEA', ''),
                ('quality_score', 'NUMERIC(5,2)', ''),
                ('capture_device_id', 'VARCHAR(100)', ''),
                ('registered_at', 'TIMESTAMPTZ', ''),
                ('status', 'VARCHAR(30)', '')
            ]
        },

        # Col 3: APP ACCESS & AUDIT VERIF (x = 850, w = 280)
        {
            'schema': 'app', 'name': 'access_consents', 'x': 850, 'y': 170, 'w': 280,
            'cols': [
                ('consent_id', 'BIGINT', 'PK'),
                ('profile_id', 'BIGINT', 'FK'),
                ('agency_id', 'INT', 'FK'),
                ('scope', 'VARCHAR(100)', ''),
                ('granted_at', 'TIMESTAMPTZ', ''),
                ('valid_until', 'TIMESTAMPTZ', ''),
                ('is_revoked', 'BOOLEAN', ''),
                ('consent_signature', 'TEXT', '')
            ]
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 850, 'y': 420, 'w': 280,
            'cols': [
                ('token_id', 'BIGINT', 'PK'),
                ('profile_id', 'BIGINT', 'FK'),
                ('agency_id', 'INT', 'FK'),
                ('required_trust_level_id', 'INT', 'FK'),
                ('token_hash', 'VARCHAR(128)', 'UQ'),
                ('issued_at', 'TIMESTAMPTZ', ''),
                ('expires_at', 'TIMESTAMPTZ', ''),
                ('status', 'VARCHAR(20)', '')
            ]
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 850, 'y': 700, 'w': 280,
            'cols': [
                ('verification_id', 'BIGINT', 'PK'),
                ('verified_at', 'TIMESTAMPTZ', ''),
                ('citizen_id', 'BIGINT', 'FK'),
                ('modality_id', 'INT', 'FK'),
                ('agency_id', 'INT', 'FK'),
                ('similarity_score', 'NUMERIC(5,4)', ''),
                ('decision', 'VARCHAR(30)', ''),
                ('client_ip', 'INET', '')
            ]
        },

        # Col 4: AUDIT LOGS & STAGING (x = 1210, w = 280)
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1210, 'y': 90, 'w': 280,
            'cols': [
                ('login_id', 'BIGINT', 'PK'),
                ('login_time', 'TIMESTAMPTZ', ''),
                ('username', 'TEXT', ''),
                ('client_ip', 'INET', ''),
                ('client_port', 'INT', ''),
                ('auth_method', 'VARCHAR(50)', ''),
                ('session_status', 'VARCHAR(30)', '')
            ]
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1210, 'y': 320, 'w': 280,
            'cols': [
                ('change_id', 'BIGINT', 'PK'),
                ('changed_at', 'TIMESTAMPTZ', ''),
                ('username', 'TEXT', ''),
                ('table_schema', 'TEXT', ''),
                ('table_name', 'TEXT', ''),
                ('operation', 'VARCHAR(10)', ''),
                ('row_id', 'TEXT', ''),
                ('old_data', 'JSONB', ''),
                ('new_data', 'JSONB', '')
            ]
        },
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1210, 'y': 600, 'w': 280,
            'cols': [
                ('import_id', 'BIGINT', 'PK'),
                ('batch_uuid', 'UUID', ''),
                ('source_system', 'VARCHAR(100)', ''),
                ('raw_payload', 'JSONB', ''),
                ('loaded_at', 'TIMESTAMPTZ', ''),
                ('status', 'VARCHAR(20)', ''),
                ('error_message', 'TEXT', '')
            ]
        },
    ]

    header_h = 24
    row_h = 20

    def get_row_y(t, col_name):
        col_names = [c[0] for c in t['cols']]
        idx = col_names.index(col_name)
        return t['y'] + header_h + idx * row_h + row_h / 2

    tmap = {f"{t['schema']}.{t['name']}": t for t in tables}

    # PK Stubs (where lines leave a PK with a single "1" and "||" marker)
    # Each stub is (start_x, y, end_x, y)
    pk_stubs = [
        # ref.trust_levels.trust_level_id
        {'x1': 320, 'y': get_row_y(tmap['ref.trust_levels'], 'trust_level_id'), 'x2': 335, 'lbl_x': 326},
        # ref.document_types.doc_type_id
        {'x1': 320, 'y': get_row_y(tmap['ref.document_types'], 'doc_type_id'), 'x2': 335, 'lbl_x': 326},
        # ref.biometric_modalities.modality_id
        {'x1': 320, 'y': get_row_y(tmap['ref.biometric_modalities'], 'modality_id'), 'x2': 335, 'lbl_x': 326},
        # ref.agencies.agency_id
        {'x1': 320, 'y': get_row_y(tmap['ref.agencies'], 'agency_id'), 'x2': 335, 'lbl_x': 326},
        # app.citizens.citizen_id
        {'x1': 720, 'y': get_row_y(tmap['app.citizens'], 'citizen_id'), 'x2': 735, 'lbl_x': 726},
        # app.digital_profiles.profile_id
        {'x1': 720, 'y': get_row_y(tmap['app.digital_profiles'], 'profile_id'), 'x2': 735, 'lbl_x': 726},
    ]

    # 14 Discrete relationship lines (from stub end x to target table FK)
    links = [
        # 1. ref.trust_levels.trust_level_id (1) -> app.digital_profiles.trust_level_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (360, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (360, get_row_y(tmap['app.digital_profiles'], 'trust_level_id')),
                    (440, get_row_y(tmap['app.digital_profiles'], 'trust_level_id'))],
            'end_lbl': ('N', 424, get_row_y(tmap['app.digital_profiles'], 'trust_level_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 2. ref.trust_levels.trust_level_id (1) -> app.access_tokens.required_trust_level_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (345, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (345, 295),
                    (780, 295),
                    (780, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id')),
                    (850, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 3. ref.document_types.doc_type_id (1) -> app.electronic_passports.doc_type_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (375, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (375, get_row_y(tmap['app.electronic_passports'], 'doc_type_id')),
                    (440, get_row_y(tmap['app.electronic_passports'], 'doc_type_id'))],
            'end_lbl': ('N', 424, get_row_y(tmap['app.electronic_passports'], 'doc_type_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 4. ref.biometric_modalities.modality_id (1) -> app.biometric_templates.modality_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (390, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (390, get_row_y(tmap['app.biometric_templates'], 'modality_id')),
                    (440, get_row_y(tmap['app.biometric_templates'], 'modality_id'))],
            'end_lbl': ('N', 424, get_row_y(tmap['app.biometric_templates'], 'modality_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 5. ref.biometric_modalities.modality_id (1) -> audit.biometric_verifications.modality_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (360, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (360, 525),
                    (795, 525),
                    (795, get_row_y(tmap['audit.biometric_verifications'], 'modality_id')),
                    (850, get_row_y(tmap['audit.biometric_verifications'], 'modality_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['audit.biometric_verifications'], 'modality_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 6. ref.agencies.agency_id (1) -> app.access_consents.agency_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (345, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (345, 810),
                    (810, 810),
                    (810, get_row_y(tmap['app.access_consents'], 'agency_id')),
                    (850, get_row_y(tmap['app.access_consents'], 'agency_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['app.access_consents'], 'agency_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 7. ref.agencies.agency_id (1) -> app.access_tokens.agency_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (345, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (345, 820),
                    (825, 820),
                    (825, get_row_y(tmap['app.access_tokens'], 'agency_id')),
                    (850, get_row_y(tmap['app.access_tokens'], 'agency_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['app.access_tokens'], 'agency_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 8. ref.agencies.agency_id (1) -> audit.biometric_verifications.agency_id (N)
        {
            'pts': [(335, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (345, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (345, 830),
                    (840, 830),
                    (840, get_row_y(tmap['audit.biometric_verifications'], 'agency_id')),
                    (850, get_row_y(tmap['audit.biometric_verifications'], 'agency_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['audit.biometric_verifications'], 'agency_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 9. app.citizens.citizen_id (1) -> app.digital_profiles.citizen_id (1) [UNIQUE FK: STRICT 1:1 !]
        {
            'pts': [(735, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (745, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (745, get_row_y(tmap['app.digital_profiles'], 'citizen_id')),
                    (720, get_row_y(tmap['app.digital_profiles'], 'citizen_id'))],
            'end_lbl': ('1', 736, get_row_y(tmap['app.digital_profiles'], 'citizen_id') - 5),
            'end_marker': 'one-end'
        },

        # 10. app.citizens.citizen_id (1) -> app.electronic_passports.citizen_id (N)
        {
            'pts': [(735, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (755, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (755, get_row_y(tmap['app.electronic_passports'], 'citizen_id')),
                    (720, get_row_y(tmap['app.electronic_passports'], 'citizen_id'))],
            'end_lbl': ('N', 736, get_row_y(tmap['app.electronic_passports'], 'citizen_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 11. app.citizens.citizen_id (1) -> app.biometric_templates.citizen_id (N)
        {
            'pts': [(735, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (765, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (765, get_row_y(tmap['app.biometric_templates'], 'citizen_id')),
                    (720, get_row_y(tmap['app.biometric_templates'], 'citizen_id'))],
            'end_lbl': ('N', 736, get_row_y(tmap['app.biometric_templates'], 'citizen_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 12. app.citizens.citizen_id (1) -> audit.biometric_verifications.citizen_id (N)
        {
            'pts': [(735, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (775, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (775, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id')),
                    (850, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 13. app.digital_profiles.profile_id (1) -> app.access_consents.profile_id (N)
        {
            'pts': [(735, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (785, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (785, get_row_y(tmap['app.access_consents'], 'profile_id')),
                    (850, get_row_y(tmap['app.access_consents'], 'profile_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['app.access_consents'], 'profile_id') - 5),
            'end_marker': 'crowsfoot'
        },

        # 14. app.digital_profiles.profile_id (1) -> app.access_tokens.profile_id (N)
        {
            'pts': [(735, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (795, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (795, get_row_y(tmap['app.access_tokens'], 'profile_id')),
                    (850, get_row_y(tmap['app.access_tokens'], 'profile_id'))],
            'end_lbl': ('N', 834, get_row_y(tmap['app.access_tokens'], 'profile_id') - 5),
            'end_marker': 'crowsfoot'
        },
    ]

    svg_w = 1540
    svg_h = 1110

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('''<defs>
        <!-- Crow's Foot: Many end (>|) -->
        <marker id="crowsfoot" viewBox="0 0 12 12" refX="12" refY="6" markerWidth="10" markerHeight="10" orient="auto">
            <path d="M 0 6 L 12 0 M 0 6 L 12 12 M 0 6 L 12 6" fill="none" stroke="#000000" stroke-width="1.2" />
            <line x1="4" y1="0" x2="4" y2="12" stroke="#000000" stroke-width="1.2" />
        </marker>
        <!-- Mandatory One: Start (||) -->
        <marker id="one-start" viewBox="0 0 10 12" refX="0" refY="6" markerWidth="8" markerHeight="10" orient="auto">
            <line x1="2" y1="1" x2="2" y2="11" stroke="#000000" stroke-width="1.2" />
            <line x1="6" y1="1" x2="6" y2="11" stroke="#000000" stroke-width="1.2" />
        </marker>
        <!-- Mandatory One: End (||) for 1:1 relations -->
        <marker id="one-end" viewBox="0 0 10 12" refX="10" refY="6" markerWidth="8" markerHeight="10" orient="auto">
            <line x1="4" y1="1" x2="4" y2="11" stroke="#000000" stroke-width="1.2" />
            <line x1="8" y1="1" x2="8" y2="11" stroke="#000000" stroke-width="1.2" />
        </marker>
    </defs>''')
    svg.append('<style>')
    svg.append('''
        .tbl-border { fill: #ffffff; stroke: #000000; stroke-width: 1.2; }
        .row-line { stroke: #000000; stroke-width: 0.8; }
        .tbl-hdr { font-family: "Times New Roman", Times, serif; font-size: 12px; font-weight: bold; fill: #000000; text-anchor: middle; }
        .col-tag { font-family: "Times New Roman", Times, serif; font-size: 10px; font-weight: bold; fill: #000000; }
        .col-name { font-family: "Times New Roman", Times, serif; font-size: 10.5px; fill: #000000; }
        .col-type { font-family: "Courier New", Courier, monospace; font-size: 9.5px; fill: #333333; text-anchor: end; }
        .conn-ortho { fill: none; stroke: #000000; stroke-width: 1.1; }
        .card-lbl { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; font-weight: bold; fill: #000000;
                    paint-order: stroke; stroke: #ffffff; stroke-width: 3.5px; stroke-linecap: round; stroke-linejoin: round; }
        .title-txt { font-family: "Times New Roman", Times, serif; font-size: 14px; font-weight: bold; fill: #000000; }
        .legend-txt { font-family: "Times New Roman", Times, serif; font-size: 11px; fill: #222222; }
    ''')
    svg.append('</style>')

    # Pure white background
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#ffffff" />')

    # Header / Title and Legend
    svg.append(f'<text x="50" y="32" class="title-txt">ER-диаграмма доменной модели: Защита БД систем цифровой идентификации граждан (Вариант 12)</text>')
    svg.append(f'<text x="50" y="52" class="legend-txt">Обозначения связей: 1 — первичный ключ («один»), N — внешний ключ («многие»); || — строго один, &gt;| — один или многие (нотация Crow\'s Foot / IE); app.citizens → app.digital_profiles: 1 : 1 (UNIQUE FK)</text>')
    svg.append(f'<line x1="50" y1="65" x2="{svg_w - 50}" y2="65" stroke="#000000" stroke-width="1" />')

    # Draw PK Stubs (clean single exit from primary key)
    for s in pk_stubs:
        svg.append(f'<line x1="{s["x1"]}" y1="{s["y"]}" x2="{s["x2"]}" y2="{s["y"]}" class="conn-ortho" marker-start="url(#one-start)" />')
        svg.append(f'<text x="{s["lbl_x"]}" y="{s["y"] - 5}" class="card-lbl">1</text>')

    # Draw Connections
    for l in links:
        pts = l['pts']
        d_str = f"M {pts[0][0]} {pts[0][1]}"
        for pt in pts[1:]:
            d_str += f" L {pt[0]} {pt[1]}"
        
        end_marker = l['end_marker']
        svg.append(f'<path d="{d_str}" class="conn-ortho" marker-end="url(#{end_marker})" />')

        # Draw End Cardinality label
        e_txt, ex, ey = l['end_lbl']
        svg.append(f'<text x="{ex}" y="{ey}" class="card-lbl">{e_txt}</text>')

    # Draw Tables
    for t in tables:
        x, y, w = t['x'], t['y'], t['w']
        col_count = len(t['cols'])
        h = header_h + col_count * row_h
        full_name = f"{t['schema']}.{t['name']}"

        # Outer border
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="tbl-border" />')
        
        # Header text
        svg.append(f'<text x="{x + w/2}" y="{y + 16}" class="tbl-hdr">{full_name}</text>')
        # Header bottom line
        svg.append(f'<line x1="{x}" y1="{y + header_h}" x2="{x + w}" y2="{y + header_h}" class="row-line" />')

        # Columns
        for r_idx, (col_name, col_type, col_role) in enumerate(t['cols']):
            curr_y = y + header_h + r_idx * row_h
            if r_idx > 0:
                svg.append(f'<line x1="{x}" y1="{curr_y}" x2="{x + w}" y2="{curr_y}" class="row-line" />')
            
            text_y = curr_y + 14
            # Draw Tag (PK, FK, UQ)
            tag_offset = 8
            if col_role:
                svg.append(f'<text x="{x + tag_offset}" y="{text_y}" class="col-tag">({col_role})</text>')
                tag_w = len(f"({col_role})") * 6.5
                svg.append(f'<text x="{x + tag_offset + tag_w}" y="{text_y}" class="col-name">{col_name}</text>')
            else:
                svg.append(f'<text x="{x + tag_offset}" y="{text_y}" class="col-name">{col_name}</text>')
            
            # Draw SQL Type (right-aligned)
            svg.append(f'<text x="{x + w - 8}" y="{text_y}" class="col-type">{col_type}</text>')

    svg.append('</svg>')

    os.makedirs('images', exist_ok=True)
    svg_path = 'images/er_diagram.svg'
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print("Saved images/er_diagram.svg")

    # Render PNG
    typ_code = '#set page(width: auto, height: auto, margin: 15pt)\n#image("er_diagram.svg")\n'
    with open('images/temp_er.typ', 'w', encoding='utf-8') as f:
        f.write(typ_code)
    
    png_path = 'images/er_diagram.png'
    res = subprocess.run(['.\\typst.exe', 'compile', '--format', 'png', '--ppi', '180', 'images/temp_er.typ', png_path], capture_output=True, text=True)
    if os.path.exists('images/temp_er.typ'):
        os.remove('images/temp_er.typ')
    
    if res.returncode == 0:
        print(f"Rendered {png_path} successfully (size: {os.path.getsize(png_path)} bytes)")
    else:
        print("Typst error:", res.stderr)

if __name__ == '__main__':
    generate_perfect_er()
