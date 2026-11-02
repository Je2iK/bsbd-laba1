import os
import subprocess

def generate_yaroslav_style_er():
    # Schema Color Palette matching Yaroslav / dbdiagram
    schema_colors = {
        'ref':   {'header': '#2b5c8f', 'border': '#2b5c8f', 'bg': '#ffffff'},
        'app':   {'header': '#1b7a43', 'border': '#1b7a43', 'bg': '#ffffff'},
        'audit': {'header': '#b84c30', 'border': '#b84c30', 'bg': '#ffffff'},
        'stg':   {'header': '#6f42c1', 'border': '#6f42c1', 'bg': '#ffffff'},
    }

    # 12 Tables with full metadata matching PostgreSQL migrations
    tables = [
        # Col 1: REF (x = 50, w = 260)
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 50, 'y': 80, 'w': 260,
            'cols': [
                ('PK', 'trust_level_id', 'INT'),
                ('UQ', 'code', 'VARCHAR(30)'),
                ('',   'name', 'VARCHAR(100)'),
                ('',   'auth_factor_min', 'INT'),
                ('',   'description', 'TEXT'),
                ('',   'is_active', 'BOOLEAN')
            ]
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 50, 'y': 280, 'w': 260,
            'cols': [
                ('PK', 'doc_type_id', 'INT'),
                ('UQ', 'type_code', 'VARCHAR(30)'),
                ('',   'type_name', 'VARCHAR(150)'),
                ('',   'has_rfid_chip', 'BOOLEAN'),
                ('',   'validity_years', 'INT')
            ]
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 50, 'y': 470, 'w': 260,
            'cols': [
                ('PK', 'modality_id', 'INT'),
                ('UQ', 'code', 'VARCHAR(30)'),
                ('',   'name', 'VARCHAR(100)'),
                ('',   'iso_standard', 'VARCHAR(100)'),
                ('',   'far_limit', 'NUMERIC(8,6)'),
                ('',   'frr_limit', 'NUMERIC(8,6)')
            ]
        },
        {
            'schema': 'ref', 'name': 'agencies', 'x': 50, 'y': 700, 'w': 260,
            'cols': [
                ('PK', 'agency_id', 'INT'),
                ('UQ', 'agency_code', 'VARCHAR(50)'),
                ('',   'agency_name', 'VARCHAR(255)'),
                ('UQ', 'inn', 'VARCHAR(12)'),
                ('UQ', 'ogrn', 'VARCHAR(15)'),
                ('',   'trust_tier', 'INT'),
                ('',   'is_active', 'BOOLEAN')
            ]
        },

        # Col 2: APP CORE (x = 420, w = 270)
        {
            'schema': 'app', 'name': 'citizens', 'x': 420, 'y': 80, 'w': 270,
            'cols': [
                ('PK', 'citizen_id', 'BIGINT'),
                ('',   'first_name', 'VARCHAR(100)'),
                ('',   'last_name', 'VARCHAR(100)'),
                ('',   'middle_name', 'VARCHAR(100)'),
                ('',   'birth_date', 'DATE'),
                ('',   'birth_place', 'VARCHAR(255)'),
                ('',   'gender', 'CHAR(1)'),
                ('',   'created_at', 'TIMESTAMPTZ')
            ]
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 420, 'y': 320, 'w': 270,
            'cols': [
                ('PK', 'profile_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT (UQ)'),
                ('UQ', 'snils', 'CHAR(11)'),
                ('UQ', 'inn', 'VARCHAR(12)'),
                ('FK', 'trust_level_id', 'INT'),
                ('',   'profile_status', 'VARCHAR(30)'),
                ('',   'verified_at', 'TIMESTAMPTZ'),
                ('',   'created_at', 'TIMESTAMPTZ')
            ]
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 420, 'y': 560, 'w': 270,
            'cols': [
                ('PK', 'passport_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'doc_type_id', 'INT'),
                ('UQ', 'chip_uid', 'VARCHAR(64)'),
                ('UQ', 'series, number', 'CHAR(4), CHAR(6)'),
                ('',   'issue_date', 'DATE'),
                ('',   'expiry_date', 'DATE'),
                ('',   'issuing_authority_code', 'VARCHAR(10)'),
                ('',   'encrypted_chip_payload', 'BYTEA [pgcrypto]'),
                ('',   'is_active', 'BOOLEAN')
            ]
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 420, 'y': 850, 'w': 270,
            'cols': [
                ('PK', 'biometric_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'modality_id', 'INT'),
                ('UQ', 'template_hash', 'CHAR(64)'),
                ('',   'encrypted_template', 'BYTEA [pgcrypto]'),
                ('',   'quality_score', 'NUMERIC(5,2)'),
                ('',   'capture_device_id', 'VARCHAR(100)'),
                ('',   'registered_at', 'TIMESTAMPTZ'),
                ('',   'status', 'VARCHAR(30)')
            ]
        },

        # Col 3: APP ACCESS & AUDIT VERIF (x = 800, w = 270)
        {
            'schema': 'app', 'name': 'access_consents', 'x': 800, 'y': 170, 'w': 270,
            'cols': [
                ('PK', 'consent_id', 'BIGINT'),
                ('FK', 'profile_id', 'BIGINT'),
                ('FK', 'agency_id', 'INT'),
                ('',   'scope', 'VARCHAR(100)'),
                ('',   'granted_at', 'TIMESTAMPTZ'),
                ('',   'valid_until', 'TIMESTAMPTZ'),
                ('',   'is_revoked', 'BOOLEAN'),
                ('',   'consent_signature', 'TEXT')
            ]
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 800, 'y': 420, 'w': 270,
            'cols': [
                ('PK', 'token_id', 'BIGINT'),
                ('FK', 'profile_id', 'BIGINT'),
                ('FK', 'agency_id', 'INT'),
                ('FK', 'required_trust_level_id', 'INT'),
                ('UQ', 'token_hash', 'VARCHAR(128)'),
                ('',   'issued_at', 'TIMESTAMPTZ'),
                ('',   'expires_at', 'TIMESTAMPTZ'),
                ('',   'status', 'VARCHAR(20)')
            ]
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 800, 'y': 700, 'w': 270,
            'cols': [
                ('PK', 'verification_id', 'BIGINT'),
                ('',   'verified_at', 'TIMESTAMPTZ'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'modality_id', 'INT'),
                ('FK', 'agency_id', 'INT'),
                ('',   'similarity_score', 'NUMERIC(5,4)'),
                ('',   'decision', 'VARCHAR(30)'),
                ('',   'client_ip', 'INET')
            ]
        },

        # Col 4: AUDIT LOGS & STAGING (x = 1170, w = 260)
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1170, 'y': 80, 'w': 260,
            'cols': [
                ('PK', 'login_id', 'BIGINT'),
                ('',   'login_time', 'TIMESTAMPTZ'),
                ('',   'username', 'TEXT'),
                ('',   'client_ip', 'INET'),
                ('',   'client_port', 'INT'),
                ('',   'auth_method', 'VARCHAR(50)'),
                ('',   'session_status', 'VARCHAR(30)')
            ]
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1170, 'y': 310, 'w': 260,
            'cols': [
                ('PK', 'change_id', 'BIGINT'),
                ('',   'changed_at', 'TIMESTAMPTZ'),
                ('',   'username', 'TEXT'),
                ('',   'table_schema', 'TEXT'),
                ('',   'table_name', 'TEXT'),
                ('',   'operation', 'VARCHAR(10)'),
                ('',   'row_id', 'TEXT'),
                ('',   'old_data', 'JSONB'),
                ('',   'new_data', 'JSONB')
            ]
        },
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1170, 'y': 600, 'w': 260,
            'cols': [
                ('PK', 'import_id', 'BIGINT'),
                ('',   'batch_uuid', 'UUID'),
                ('',   'source_system', 'VARCHAR(100)'),
                ('',   'raw_payload', 'JSONB'),
                ('',   'loaded_at', 'TIMESTAMPTZ'),
                ('',   'status', 'VARCHAR(20)'),
                ('',   'error_message', 'TEXT')
            ]
        },
    ]

    header_h = 24
    row_h = 19

    def get_row_y(t, col_name):
        col_names = [c[1] for c in t['cols']]
        idx = col_names.index(col_name)
        return t['y'] + header_h + idx * row_h + row_h / 2 + 3

    tmap = {f"{t['schema']}.{t['name']}": t for t in tables}

    # PK Stubs (dot at PK exit and single "1" label)
    pk_stubs = [
        {'x1': 310, 'y': get_row_y(tmap['ref.trust_levels'], 'trust_level_id'), 'x2': 325, 'lbl_x': 316},
        {'x1': 310, 'y': get_row_y(tmap['ref.document_types'], 'doc_type_id'), 'x2': 325, 'lbl_x': 316},
        {'x1': 310, 'y': get_row_y(tmap['ref.biometric_modalities'], 'modality_id'), 'x2': 325, 'lbl_x': 316},
        {'x1': 310, 'y': get_row_y(tmap['ref.agencies'], 'agency_id'), 'x2': 325, 'lbl_x': 316},
        {'x1': 690, 'y': get_row_y(tmap['app.citizens'], 'citizen_id'), 'x2': 705, 'lbl_x': 696},
        {'x1': 690, 'y': get_row_y(tmap['app.digital_profiles'], 'profile_id'), 'x2': 705, 'lbl_x': 696},
    ]

    # 14 Discrete relationship lines with relationship type (1:N or 1:1) right at the arrow!
    links = [
        # 1. ref.trust_levels.trust_level_id (1) -> app.digital_profiles.trust_level_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (350, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (350, get_row_y(tmap['app.digital_profiles'], 'trust_level_id')),
                    (420, get_row_y(tmap['app.digital_profiles'], 'trust_level_id'))],
            'arrow_lbl': ('1:N', 396, get_row_y(tmap['app.digital_profiles'], 'trust_level_id') - 5),
        },

        # 2. ref.trust_levels.trust_level_id (1) -> app.access_tokens.required_trust_level_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (335, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (335, 295),
                    (745, 295),
                    (745, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id')),
                    (800, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id') - 5),
        },

        # 3. ref.document_types.doc_type_id (1) -> app.electronic_passports.doc_type_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (365, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (365, get_row_y(tmap['app.electronic_passports'], 'doc_type_id')),
                    (420, get_row_y(tmap['app.electronic_passports'], 'doc_type_id'))],
            'arrow_lbl': ('1:N', 396, get_row_y(tmap['app.electronic_passports'], 'doc_type_id') - 5),
        },

        # 4. ref.biometric_modalities.modality_id (1) -> app.biometric_templates.modality_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (380, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (380, get_row_y(tmap['app.biometric_templates'], 'modality_id')),
                    (420, get_row_y(tmap['app.biometric_templates'], 'modality_id'))],
            'arrow_lbl': ('1:N', 396, get_row_y(tmap['app.biometric_templates'], 'modality_id') - 5),
        },

        # 5. ref.biometric_modalities.modality_id (1) -> audit.biometric_verifications.modality_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (350, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (350, 535),
                    (755, 535),
                    (755, get_row_y(tmap['audit.biometric_verifications'], 'modality_id')),
                    (800, get_row_y(tmap['audit.biometric_verifications'], 'modality_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['audit.biometric_verifications'], 'modality_id') - 5),
        },

        # 6. ref.agencies.agency_id (1) -> app.access_consents.agency_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (335, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (335, 825),
                    (765, 825),
                    (765, get_row_y(tmap['app.access_consents'], 'agency_id')),
                    (800, get_row_y(tmap['app.access_consents'], 'agency_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['app.access_consents'], 'agency_id') - 5),
        },

        # 7. ref.agencies.agency_id (1) -> app.access_tokens.agency_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (335, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (335, 835),
                    (775, 835),
                    (775, get_row_y(tmap['app.access_tokens'], 'agency_id')),
                    (800, get_row_y(tmap['app.access_tokens'], 'agency_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['app.access_tokens'], 'agency_id') - 5),
        },

        # 8. ref.agencies.agency_id (1) -> audit.biometric_verifications.agency_id (N)
        {
            'rel': '1:N',
            'pts': [(325, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (335, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (335, 845),
                    (785, 845),
                    (785, get_row_y(tmap['audit.biometric_verifications'], 'agency_id')),
                    (800, get_row_y(tmap['audit.biometric_verifications'], 'agency_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['audit.biometric_verifications'], 'agency_id') - 5),
        },

        # 9. app.citizens.citizen_id (1) -> app.digital_profiles.citizen_id (1) [STRICT 1:1 !]
        {
            'rel': '1:1',
            'pts': [(705, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (715, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (715, get_row_y(tmap['app.digital_profiles'], 'citizen_id')),
                    (690, get_row_y(tmap['app.digital_profiles'], 'citizen_id'))],
            'arrow_lbl': ('1:1', 698, get_row_y(tmap['app.digital_profiles'], 'citizen_id') - 5),
        },

        # 10. app.citizens.citizen_id (1) -> app.electronic_passports.citizen_id (N)
        {
            'rel': '1:N',
            'pts': [(705, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (725, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (725, get_row_y(tmap['app.electronic_passports'], 'citizen_id')),
                    (690, get_row_y(tmap['app.electronic_passports'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 698, get_row_y(tmap['app.electronic_passports'], 'citizen_id') - 5),
        },

        # 11. app.citizens.citizen_id (1) -> app.biometric_templates.citizen_id (N)
        {
            'rel': '1:N',
            'pts': [(705, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (735, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (735, get_row_y(tmap['app.biometric_templates'], 'citizen_id')),
                    (690, get_row_y(tmap['app.biometric_templates'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 698, get_row_y(tmap['app.biometric_templates'], 'citizen_id') - 5),
        },

        # 12. app.citizens.citizen_id (1) -> audit.biometric_verifications.citizen_id (N)
        {
            'rel': '1:N',
            'pts': [(705, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (745, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (745, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id')),
                    (800, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id') - 5),
        },

        # 13. app.digital_profiles.profile_id (1) -> app.access_consents.profile_id (N)
        {
            'rel': '1:N',
            'pts': [(705, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (755, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (755, get_row_y(tmap['app.access_consents'], 'profile_id')),
                    (800, get_row_y(tmap['app.access_consents'], 'profile_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['app.access_consents'], 'profile_id') - 5),
        },

        # 14. app.digital_profiles.profile_id (1) -> app.access_tokens.profile_id (N)
        {
            'rel': '1:N',
            'pts': [(705, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (765, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (765, get_row_y(tmap['app.access_tokens'], 'profile_id')),
                    (800, get_row_y(tmap['app.access_tokens'], 'profile_id'))],
            'arrow_lbl': ('1:N', 776, get_row_y(tmap['app.access_tokens'], 'profile_id') - 5),
        },
    ]

    svg_w = 1480
    svg_h = 1100

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('''<defs>
        <!-- Arrowhead pointing to target table -->
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 1.5 L 10 5 L 0 8.5 Z" fill="#2d3748" />
        </marker>
        <!-- Soft Card Shadow -->
        <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="115%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.08" />
        </filter>
    </defs>''')
    svg.append('<style>')
    svg.append('''
        .main-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #1a202c; }
        .legend-lbl { font-family: "Segoe UI", Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #4a5568; }
        .tbl-title  { font-family: "Segoe UI", Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #ffffff; }
        
        .col-name   { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; fill: #2d3748; }
        .col-type   { font-family: "Courier New", Courier, monospace; font-size: 10px; fill: #718096; text-anchor: end; }
        
        .tag-pk     { font-family: "Segoe UI", Arial, sans-serif; font-size: 10px; font-weight: bold; fill: #e53e3e; }
        .tag-fk     { font-family: "Segoe UI", Arial, sans-serif; font-size: 10px; font-weight: bold; fill: #3182ce; }
        .tag-uq     { font-family: "Segoe UI", Arial, sans-serif; font-size: 10px; font-weight: bold; fill: #805ad5; }
        
        .conn-line  { fill: none; stroke: #4a5568; stroke-width: 1.3; }
        .card-lbl   { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; font-weight: bold; fill: #1a202c;
                      paint-order: stroke; stroke: #ffffff; stroke-width: 3.5px; stroke-linecap: round; stroke-linejoin: round; }
        .rel-lbl    { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5px; font-weight: bold; fill: #1a202c;
                      paint-order: stroke; stroke: #ffffff; stroke-width: 3.5px; stroke-linecap: round; stroke-linejoin: round; }
    ''')
    svg.append('</style>')

    # Pure white background
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#fcfdfd" />')

    # Top Header & Legend matching Yaroslav
    svg.append(f'<text x="50" y="32" class="main-title">ER-диаграмма домена: Защита БД систем цифровой идентификации граждан (Вариант 12)</text>')
    
    # Legend pills (Right side of header)
    leg_items = [
        ('ref', '#2b5c8f', 'Схема ref'),
        ('app', '#1b7a43', 'Схема app'),
        ('audit', '#b84c30', 'Схема audit'),
        ('stg', '#6f42c1', 'Схема stg')
    ]
    lx = 750
    for code, col, name in leg_items:
        svg.append(f'<rect x="{lx}" y="20" width="14" height="14" rx="3" fill="{col}" />')
        svg.append(f'<text x="{lx + 20}" y="32" class="legend-lbl">{name}</text>')
        lx += 120

    # PK Stubs (dot at PK exit and single "1" label)
    for s in pk_stubs:
        svg.append(f'<circle cx="{s["x1"]}" cy="{s["y"]}" r="3.5" fill="#4a5568" />')
        svg.append(f'<line x1="{s["x1"]}" y1="{s["y"]}" x2="{s["x2"]}" y2="{s["y"]}" class="conn-line" />')
        svg.append(f'<text x="{s["lbl_x"]}" y="{s["y"] - 5}" class="card-lbl">1</text>')

    # Draw Connections with Relationship Indicator at the Arrow
    for l in links:
        pts = l['pts']
        d_str = f"M {pts[0][0]} {pts[0][1]}"
        for pt in pts[1:]:
            d_str += f" L {pt[0]} {pt[1]}"
        
        svg.append(f'<path d="{d_str}" class="conn-line" marker-end="url(#arrow)" />')

        # Draw Relationship label directly at the arrow (e.g. 1:N or 1:1)
        r_txt, rx, ry = l['arrow_lbl']
        svg.append(f'<text x="{rx}" y="{ry}" class="rel-lbl">{r_txt}</text>')

    # Draw Tables (Yaroslav dbdiagram card style)
    for t in tables:
        x, y, w = t['x'], t['y'], t['w']
        col_count = len(t['cols'])
        h = header_h + col_count * row_h + 8
        full_name = f"{t['schema']}.{t['name']}"
        sc = schema_colors[t['schema']]

        # Table container with shadow and rounded corners
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" ry="5" fill="#ffffff" stroke="{sc["border"]}" stroke-width="1.3" filter="url(#card-shadow)" />')
        
        # Header banner (rounded top)
        header_path = f'''M {x} {y+5} 
                          A 5 5 0 0 1 {x+5} {y} 
                          L {x+w-5} {y} 
                          A 5 5 0 0 1 {x+w} {y+5} 
                          L {x+w} {y+header_h} 
                          L {x} {y+header_h} Z'''
        svg.append(f'<path d="{header_path}" fill="{sc["header"]}" />')
        svg.append(f'<text x="{x + 10}" y="{y + 17}" class="tbl-title">{full_name}</text>')

        # Columns
        col_start_y = y + header_h + 15
        for r_idx, (role, col_name, col_type) in enumerate(t['cols']):
            curr_y = col_start_y + r_idx * row_h
            
            # Badge
            if role == 'PK':
                svg.append(f'<text x="{x + 10}" y="{curr_y}" class="tag-pk">PK</text>')
            elif role == 'FK':
                svg.append(f'<text x="{x + 10}" y="{curr_y}" class="tag-fk">FK</text>')
            elif role == 'UQ':
                svg.append(f'<text x="{x + 10}" y="{curr_y}" class="tag-uq">UQ</text>')
            
            # Column Name
            name_x = x + 34
            svg.append(f'<text x="{name_x}" y="{curr_y}" class="col-name">{col_name}</text>')
            
            # Data Type (right-aligned)
            svg.append(f'<text x="{x + w - 10}" y="{curr_y}" class="col-type">{col_type}</text>')

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
    generate_yaroslav_style_er()
