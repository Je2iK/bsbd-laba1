import os
import math

def generate_svg():
    # Colors for schemas
    colors = {
        'ref':   {'header': '#2b5797', 'bg': '#eff4fa', 'border': '#1e395b'},
        'app':   {'header': '#107c41', 'bg': '#eef9f2', 'border': '#0b532c'},
        'audit': {'header': '#b7472a', 'bg': '#fcf0ed', 'border': '#7a2f1c'},
        'stg':   {'header': '#744da9', 'bg': '#f5f0fa', 'border': '#4d3370'},
    }

    # Entities with columns: name, pk, fk, type
    tables = [
        # REF
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 60, 'y': 60, 'w': 280,
            'cols': [
                ('PK', 'trust_level_id', 'INT'),
                ('UQ', 'code', 'VARCHAR(30)'),
                ('  ', 'name', 'VARCHAR(100)'),
                ('  ', 'auth_factor_min', 'INT'),
                ('  ', 'description', 'TEXT'),
            ]
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 60, 'y': 250, 'w': 280,
            'cols': [
                ('PK', 'doc_type_id', 'INT'),
                ('UQ', 'type_code', 'VARCHAR(30)'),
                ('  ', 'type_name', 'VARCHAR(150)'),
                ('  ', 'has_rfid_chip', 'BOOLEAN'),
                ('  ', 'validity_years', 'INT'),
            ]
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 60, 'y': 440, 'w': 280,
            'cols': [
                ('PK', 'modality_id', 'INT'),
                ('UQ', 'code', 'VARCHAR(30)'),
                ('  ', 'name', 'VARCHAR(100)'),
                ('  ', 'iso_standard', 'VARCHAR(100)'),
                ('  ', 'far_limit', 'NUMERIC(8,6)'),
                ('  ', 'frr_limit', 'NUMERIC(8,6)'),
            ]
        },
        {
            'schema': 'ref', 'name': 'agencies', 'x': 60, 'y': 660, 'w': 280,
            'cols': [
                ('PK', 'agency_id', 'INT'),
                ('UQ', 'agency_code', 'VARCHAR(50)'),
                ('  ', 'agency_name', 'VARCHAR(255)'),
                ('UQ', 'inn', 'VARCHAR(12)'),
                ('  ', 'trust_tier', 'INT'),
            ]
        },

        # APP
        {
            'schema': 'app', 'name': 'citizens', 'x': 420, 'y': 60, 'w': 320,
            'cols': [
                ('PK', 'citizen_id', 'BIGINT'),
                ('  ', 'first_name', 'VARCHAR(100)'),
                ('  ', 'last_name', 'VARCHAR(100)'),
                ('  ', 'middle_name', 'VARCHAR(100)'),
                ('  ', 'birth_date', 'DATE'),
                ('  ', 'birth_place', 'VARCHAR(255)'),
                ('  ', 'gender', 'CHAR(1)'),
            ]
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 420, 'y': 310, 'w': 320,
            'cols': [
                ('PK', 'profile_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT (UQ)'),
                ('UQ', 'snils', 'CHAR(11)'),
                ('UQ', 'inn', 'VARCHAR(12)'),
                ('FK', 'trust_level_id', 'INT'),
                ('  ', 'profile_status', 'VARCHAR(30)'),
                ('  ', 'verified_at', 'TIMESTAMPTZ'),
            ]
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 420, 'y': 570, 'w': 320,
            'cols': [
                ('PK', 'passport_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'doc_type_id', 'INT'),
                ('UQ', 'chip_uid', 'VARCHAR(64)'),
                ('UQ', 'series, number', 'CHAR(4), CHAR(6)'),
                ('  ', 'encrypted_chip_payload', 'BYTEA [pgcrypto]'),
                ('  ', 'is_active', 'BOOLEAN'),
            ]
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 420, 'y': 820, 'w': 320,
            'cols': [
                ('PK', 'biometric_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'modality_id', 'INT'),
                ('UQ', 'template_hash', 'CHAR(64)'),
                ('  ', 'encrypted_template', 'BYTEA [pgcrypto]'),
                ('  ', 'quality_score', 'NUMERIC(5,2)'),
                ('  ', 'status', 'VARCHAR(30)'),
            ]
        },

        # APP M:N & TOKENS
        {
            'schema': 'app', 'name': 'access_consents', 'x': 820, 'y': 160, 'w': 320,
            'cols': [
                ('PK', 'consent_id', 'BIGINT'),
                ('FK', 'profile_id', 'BIGINT'),
                ('FK', 'agency_id', 'INT'),
                ('  ', 'scope', 'VARCHAR(100)'),
                ('  ', 'granted_at', 'TIMESTAMPTZ'),
                ('  ', 'valid_until', 'TIMESTAMPTZ'),
                ('  ', 'is_revoked', 'BOOLEAN'),
            ]
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 820, 'y': 430, 'w': 320,
            'cols': [
                ('PK', 'token_id', 'BIGINT'),
                ('FK', 'profile_id', 'BIGINT'),
                ('FK', 'agency_id', 'INT'),
                ('FK', 'required_trust_level_id', 'INT'),
                ('UQ', 'token_hash', 'CHAR(64)'),
                ('  ', 'expires_at', 'TIMESTAMPTZ'),
                ('  ', 'status', 'VARCHAR(20)'),
            ]
        },

        # AUDIT
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1220, 'y': 60, 'w': 300,
            'cols': [
                ('PK', 'login_id', 'BIGINT'),
                ('  ', 'login_time', 'TIMESTAMPTZ'),
                ('  ', 'username', 'TEXT'),
                ('  ', 'client_ip', 'INET'),
                ('  ', 'auth_method', 'VARCHAR(50)'),
                ('  ', 'session_status', 'VARCHAR(30)'),
            ]
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1220, 'y': 280, 'w': 300,
            'cols': [
                ('PK', 'change_id', 'BIGINT'),
                ('  ', 'changed_at', 'TIMESTAMPTZ'),
                ('  ', 'username', 'TEXT'),
                ('  ', 'table_schema', 'TEXT'),
                ('  ', 'table_name', 'TEXT'),
                ('  ', 'operation', 'VARCHAR(10)'),
                ('  ', 'row_id', 'TEXT'),
                ('  ', 'old_data', 'JSONB'),
                ('  ', 'new_data', 'JSONB'),
            ]
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 1220, 'y': 560, 'w': 300,
            'cols': [
                ('PK', 'verification_id', 'BIGINT'),
                ('  ', 'verified_at', 'TIMESTAMPTZ'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'modality_id', 'INT'),
                ('FK', 'agency_id', 'INT'),
                ('  ', 'similarity_score', 'NUMERIC(5,4)'),
                ('  ', 'decision', 'VARCHAR(30)'),
            ]
        },

        # STG
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1220, 'y': 820, 'w': 300,
            'cols': [
                ('PK', 'import_id', 'BIGINT'),
                ('  ', 'batch_uuid', 'UUID'),
                ('  ', 'source_system', 'VARCHAR(100)'),
                ('  ', 'raw_payload', 'JSONB'),
                ('  ', 'loaded_at', 'TIMESTAMPTZ'),
                ('  ', 'status', 'VARCHAR(20)'),
            ]
        },
    ]

    # Connections between tables: (src_table, dst_table, label)
    connections = [
        ('ref.trust_levels', 'app.digital_profiles'),
        ('app.citizens', 'app.digital_profiles'),
        ('app.citizens', 'app.electronic_passports'),
        ('ref.document_types', 'app.electronic_passports'),
        ('app.citizens', 'app.biometric_templates'),
        ('ref.biometric_modalities', 'app.biometric_templates'),
        ('app.digital_profiles', 'app.access_consents'),
        ('ref.agencies', 'app.access_consents'),
        ('app.digital_profiles', 'app.access_tokens'),
        ('ref.agencies', 'app.access_tokens'),
        ('app.citizens', 'audit.biometric_verifications'),
        ('ref.biometric_modalities', 'audit.biometric_verifications'),
        ('ref.agencies', 'audit.biometric_verifications'),
    ]

    svg_width = 1600
    svg_height = 1080

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg.append('<style>')
    svg.append('''
        .title { font-family: "Times New Roman", serif; font-size: 20px; font-weight: bold; fill: #111; }
        .tbl-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #ffffff; }
        .col-txt { font-family: "Consolas", "Courier New", monospace; font-size: 11px; fill: #222; }
        .pk { font-weight: bold; fill: #b7472a; }
        .fk { font-weight: bold; fill: #2b5797; }
        .uq { font-weight: bold; fill: #6a1b9a; }
        .type { fill: #666; font-size: 10px; }
        .conn-line { stroke: #555; stroke-width: 1.5; stroke-dasharray: 4,3; fill: none; }
        .legend-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; font-weight: bold; }
    ''')
    svg.append('</style>')

    # Background
    svg.append(f'<rect width="{svg_width}" height="{svg_height}" fill="#fcfcfc" />')

    # Watermark / Title
    svg.append('<text x="50" y="35" class="title">ER-диаграмма домена: Защита БД систем цифровой идентификации граждан (Вариант 12)</text>')

    # Draw Legend
    leg_x = 900
    leg_y = 15
    for schema, col in colors.items():
        svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="16" height="16" rx="3" fill="{col["header"]}" />')
        svg.append(f'<text x="{leg_x+22}" y="{leg_y+13}" font-family="Segoe UI" font-size="12px" fill="#333">Схема {schema}</text>')
        leg_x += 120

    # Draw Tables
    tbl_coords = {}
    for t in tables:
        full_name = f"{t['schema']}.{t['name']}"
        x = t['x']
        y = t['y']
        w = t['w']
        col_count = len(t['cols'])
        row_h = 20
        header_h = 26
        h = header_h + col_count * row_h + 8

        tbl_coords[full_name] = {'x': x, 'y': y, 'w': w, 'h': h, 'cx': x + w/2, 'cy': y + h/2}

        c = colors[t['schema']]
        # Table container with shadow
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="1.5" />')
        # Header
        svg.append(f'<path d="M {x} {y+6} Q {x} {y} {x+6} {y} L {x+w-6} {y} Q {x+w} {y} {x+w} {y+6} L {x+w} {y+header_h} L {x} {y+header_h} Z" fill="{c["header"]}" />')
        svg.append(f'<text x="{x+10}" y="{y+18}" class="tbl-title">{full_name}</text>')

        # Columns
        col_y = y + header_h + 16
        for key_type, col_name, data_type in t['cols']:
            key_cls = "pk" if key_type == "PK" else ("fk" if key_type == "FK" else ("uq" if key_type == "UQ" else "col-txt"))
            svg.append(f'<text x="{x+10}" y="{col_y}" class="col-txt {key_cls}">{key_type}</text>')
            svg.append(f'<text x="{x+38}" y="{col_y}" class="col-txt">{col_name}</text>')
            svg.append(f'<text x="{x+w-10}" y="{col_y}" class="col-txt type" text-anchor="end">{data_type}</text>')
            col_y += row_h

    # Connectors
    for src, dst in connections:
        if src in tbl_coords and dst in tbl_coords:
            s = tbl_coords[src]
            d = tbl_coords[dst]
            
            # Simple line from right/left or bottom/top
            if s['x'] < d['x']:
                x1 = s['x'] + s['w']
                y1 = s['cy']
                x2 = d['x']
                y2 = d['cy']
            else:
                x1 = s['x']
                y1 = s['cy']
                x2 = d['x'] + d['w']
                y2 = d['cy']
                
            dx = (x2 - x1) * 0.5
            svg.append(f'<path d="M {x1} {y1} C {x1+dx} {y1}, {x2-dx} {y2}, {x2} {y2}" class="conn-line" marker-end="url(#arrow)" />')
            # End dots
            svg.append(f'<circle cx="{x1}" cy="{y1}" r="3" fill="#2b5797" />')
            svg.append(f'<circle cx="{x2}" cy="{y2}" r="3" fill="#b7472a" />')

    svg.append('</svg>')

    os.makedirs('images', exist_ok=True)
    with open('images/er_diagram.svg', 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print('Generated images/er_diagram.svg')

generate_svg()
