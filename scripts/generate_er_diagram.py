import os
import subprocess

def generate_svg():
    # Colors for schemas
    colors = {
        'ref':   {'header': '#23497d', 'bg': '#f4f7fb', 'border': '#1e395b', 'badge': '#23497d'},
        'app':   {'header': '#0e6936', 'bg': '#f0f9f3', 'border': '#0b532c', 'badge': '#0e6936'},
        'audit': {'header': '#9c381e', 'bg': '#fdf2ef', 'border': '#7a2f1c', 'badge': '#9c381e'},
        'stg':   {'header': '#613d91', 'bg': '#f7f3fb', 'border': '#4d3370', 'badge': '#613d91'},
    }

    # Table definitions
    tables = [
        # REF (Col 1: x = 60, w = 310)
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 60, 'y': 70, 'w': 310,
            'cols': [
                ('PK', 'trust_level_id', 'INT'),
                ('UQ', 'code', 'VARCHAR(30)'),
                ('  ', 'name', 'VARCHAR(100)'),
                ('  ', 'auth_factor_min', 'INT'),
                ('  ', 'description', 'TEXT'),
                ('  ', 'is_active', 'BOOLEAN'),
            ]
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 60, 'y': 290, 'w': 310,
            'cols': [
                ('PK', 'doc_type_id', 'INT'),
                ('UQ', 'type_code', 'VARCHAR(30)'),
                ('  ', 'type_name', 'VARCHAR(150)'),
                ('  ', 'has_rfid_chip', 'BOOLEAN'),
                ('  ', 'validity_years', 'INT'),
            ]
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 60, 'y': 510, 'w': 310,
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
            'schema': 'ref', 'name': 'agencies', 'x': 60, 'y': 760, 'w': 310,
            'cols': [
                ('PK', 'agency_id', 'INT'),
                ('UQ', 'agency_code', 'VARCHAR(50)'),
                ('  ', 'agency_name', 'VARCHAR(255)'),
                ('UQ', 'inn', 'VARCHAR(12)'),
                ('UQ', 'ogrn', 'VARCHAR(15)'),
                ('  ', 'trust_tier', 'INT'),
                ('  ', 'is_active', 'BOOLEAN'),
            ]
        },

        # APP (Col 2: x = 490, w = 340)
        {
            'schema': 'app', 'name': 'citizens', 'x': 490, 'y': 70, 'w': 340,
            'cols': [
                ('PK', 'citizen_id', 'BIGINT'),
                ('  ', 'first_name', 'VARCHAR(100)'),
                ('  ', 'last_name', 'VARCHAR(100)'),
                ('  ', 'middle_name', 'VARCHAR(100)'),
                ('  ', 'birth_date', 'DATE'),
                ('  ', 'birth_place', 'VARCHAR(255)'),
                ('  ', 'gender', 'CHAR(1)'),
                ('  ', 'created_at', 'TIMESTAMPTZ'),
            ]
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 490, 'y': 330, 'w': 340,
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
            'schema': 'app', 'name': 'electronic_passports', 'x': 490, 'y': 590, 'w': 340,
            'cols': [
                ('PK', 'passport_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'doc_type_id', 'INT'),
                ('UQ', 'chip_uid', 'VARCHAR(64)'),
                ('UQ', 'series, number', 'CHAR(4), CHAR(6)'),
                ('  ', 'issue_date', 'DATE'),
                ('  ', 'expiry_date', 'DATE'),
                ('  ', 'encrypted_chip_payload', 'BYTEA [pgcrypto]'),
                ('  ', 'is_active', 'BOOLEAN'),
            ]
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 490, 'y': 860, 'w': 340,
            'cols': [
                ('PK', 'biometric_id', 'BIGINT'),
                ('FK', 'citizen_id', 'BIGINT'),
                ('FK', 'modality_id', 'INT'),
                ('UQ', 'template_hash', 'CHAR(64)'),
                ('  ', 'encrypted_template', 'BYTEA [pgcrypto]'),
                ('  ', 'quality_score', 'NUMERIC(5,2)'),
                ('  ', 'capture_device_id', 'VARCHAR(100)'),
                ('  ', 'status', 'VARCHAR(30)'),
            ]
        },

        # APP TOKENS & CONSENTS (Col 3: x = 940, w = 330)
        {
            'schema': 'app', 'name': 'access_consents', 'x': 940, 'y': 220, 'w': 330,
            'cols': [
                ('PK', 'consent_id', 'BIGINT'),
                ('FK', 'profile_id', 'BIGINT'),
                ('FK', 'agency_id', 'INT'),
                ('UQ', '(profile, agency, scope)', ''),
                ('  ', 'scope', 'VARCHAR(100)'),
                ('  ', 'granted_at', 'TIMESTAMPTZ'),
                ('  ', 'valid_until', 'TIMESTAMPTZ'),
                ('  ', 'is_revoked', 'BOOLEAN'),
            ]
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 940, 'y': 520, 'w': 330,
            'cols': [
                ('PK', 'token_id', 'BIGINT'),
                ('FK', 'profile_id', 'BIGINT'),
                ('FK', 'agency_id', 'INT'),
                ('FK', 'required_trust_level_id', 'INT'),
                ('UQ', 'token_hash', 'VARCHAR(128)'),
                ('  ', 'issued_at', 'TIMESTAMPTZ'),
                ('  ', 'expires_at', 'TIMESTAMPTZ'),
                ('  ', 'status', 'VARCHAR(20)'),
            ]
        },

        # AUDIT & STG (Col 4: x = 1390, w = 320)
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1390, 'y': 70, 'w': 320,
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
            'schema': 'audit', 'name': 'change_log', 'x': 1390, 'y': 280, 'w': 320,
            'cols': [
                ('PK', 'change_id', 'BIGINT'),
                ('  ', 'changed_at', 'TIMESTAMPTZ'),
                ('  ', 'username', 'TEXT'),
                ('  ', 'table_name', 'TEXT'),
                ('  ', 'operation', 'VARCHAR(10)'),
                ('  ', 'row_id', 'TEXT'),
                ('  ', 'old_data / new_data', 'JSONB'),
            ]
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 1390, 'y': 550, 'w': 320,
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
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1390, 'y': 840, 'w': 320,
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

    # Map tables by full name
    tbl_map = {f"{t['schema']}.{t['name']}": t for t in tables}

    # All 14 Foreign Keys accurately defined with exact pathing, cardinality and field names
    fk_links = [
        # 1. trust_levels -> digital_profiles (1:N)
        {
            'src': 'ref.trust_levels', 'dst': 'app.digital_profiles',
            'fk': 'trust_level_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 120), (430, 120), (430, 420), (490, 420)]
        },
        # 2. trust_levels -> access_tokens (1:N)
        {
            'src': 'ref.trust_levels', 'dst': 'app.access_tokens',
            'fk': 'required_trust_level_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 95), (410, 95), (410, 40), (900, 40), (900, 590), (940, 590)]
        },
        # 3. citizens -> digital_profiles (1:1 UQ)
        {
            'src': 'app.citizens', 'dst': 'app.digital_profiles',
            'fk': 'citizen_id', 'c_src': '1', 'c_dst': '1', 'color': '#0e6936',
            'pts': [(660, 255), (660, 330)]
        },
        # 4. citizens -> electronic_passports (1:N)
        {
            'src': 'app.citizens', 'dst': 'app.electronic_passports',
            'fk': 'citizen_id', 'c_src': '1', 'c_dst': 'N', 'color': '#0e6936',
            'pts': [(830, 140), (860, 140), (860, 640), (830, 640)]
        },
        # 5. document_types -> electronic_passports (1:N)
        {
            'src': 'ref.document_types', 'dst': 'app.electronic_passports',
            'fk': 'doc_type_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 340), (430, 340), (430, 650), (490, 650)]
        },
        # 6. citizens -> biometric_templates (1:N)
        {
            'src': 'app.citizens', 'dst': 'app.biometric_templates',
            'fk': 'citizen_id', 'c_src': '1', 'c_dst': 'N', 'color': '#0e6936',
            'pts': [(490, 160), (450, 160), (450, 910), (490, 910)]
        },
        # 7. biometric_modalities -> biometric_templates (1:N)
        {
            'src': 'ref.biometric_modalities', 'dst': 'app.biometric_templates',
            'fk': 'modality_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 560), (430, 560), (430, 930), (490, 930)]
        },
        # 8. digital_profiles -> access_consents (1:N)
        {
            'src': 'app.digital_profiles', 'dst': 'app.access_consents',
            'fk': 'profile_id', 'c_src': '1', 'c_dst': 'N', 'color': '#0e6936',
            'pts': [(830, 370), (885, 370), (885, 290), (940, 290)]
        },
        # 9. agencies -> access_consents (1:N)
        {
            'src': 'ref.agencies', 'dst': 'app.access_consents',
            'fk': 'agency_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 800), (420, 800), (420, 810), (880, 810), (880, 320), (940, 320)]
        },
        # 10. digital_profiles -> access_tokens (1:N)
        {
            'src': 'app.digital_profiles', 'dst': 'app.access_tokens',
            'fk': 'profile_id', 'c_src': '1', 'c_dst': 'N', 'color': '#0e6936',
            'pts': [(830, 400), (885, 400), (885, 560), (940, 560)]
        },
        # 11. agencies -> access_tokens (1:N)
        {
            'src': 'ref.agencies', 'dst': 'app.access_tokens',
            'fk': 'agency_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 825), (430, 825), (430, 820), (890, 820), (890, 620), (940, 620)]
        },
        # 12. citizens -> biometric_verifications (1:N)
        {
            'src': 'app.citizens', 'dst': 'audit.biometric_verifications',
            'fk': 'citizen_id', 'c_src': '1', 'c_dst': 'N', 'color': '#0e6936',
            'pts': [(830, 110), (910, 110), (910, 470), (1330, 470), (1330, 615), (1390, 615)]
        },
        # 13. biometric_modalities -> biometric_verifications (1:N)
        {
            'src': 'ref.biometric_modalities', 'dst': 'audit.biometric_verifications',
            'fk': 'modality_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 590), (410, 590), (410, 1050), (1340, 1050), (1340, 645), (1390, 645)]
        },
        # 14. agencies -> biometric_verifications (1:N)
        {
            'src': 'ref.agencies', 'dst': 'audit.biometric_verifications',
            'fk': 'agency_id', 'c_src': '1', 'c_dst': 'N', 'color': '#23497d',
            'pts': [(370, 850), (400, 850), (400, 1070), (1350, 1070), (1350, 675), (1390, 675)]
        },
    ]

    svg_width = 1780
    svg_height = 1120

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg.append('<defs>')
    # Arrow markers
    svg.append('''
        <marker id="arrow-ref" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#23497d" />
        </marker>
        <marker id="arrow-app" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#0e6936" />
        </marker>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
            <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.08"/>
        </filter>
    ''')
    svg.append('</defs>')

    svg.append('<style>')
    svg.append('''
        .title { font-family: "Segoe UI", Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #111; }
        .subtitle { font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; fill: #555; }
        .tbl-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #ffffff; }
        .col-txt { font-family: "Consolas", "Courier New", monospace; font-size: 11px; fill: #222; }
        .pk { font-weight: bold; fill: #b7472a; }
        .fk { font-weight: bold; fill: #23497d; }
        .uq { font-weight: bold; fill: #6a1b9a; }
        .type { fill: #666; font-size: 10px; }
        .conn-line { fill: none; stroke-width: 1.8; stroke-dasharray: 5, 3; }
        .card-lbl { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; font-weight: bold; fill: #111; }
        .fk-badge-txt { font-family: "Consolas", monospace; font-size: 9px; fill: #fff; font-weight: bold; }
    ''')
    svg.append('</style>')

    # Background
    svg.append(f'<rect width="{svg_width}" height="{svg_height}" fill="#fafbfc" />')

    # Watermark / Title
    svg.append('<text x="50" y="32" class="title">ER-диаграмма домена: Защита БД систем цифровой идентификации граждан (Вариант 12)</text>')
    svg.append('<text x="50" y="48" class="subtitle">Полная реляционная модель: 14 сущностей, 14 внешних ключей (FK), разделение на схемы ref / app / audit / stg</text>')

    # Draw Legend
    leg_x = 1080
    leg_y = 18
    for schema, col in colors.items():
        svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="18" height="18" rx="3" fill="{col["header"]}" />')
        svg.append(f'<text x="{leg_x+24}" y="{leg_y+14}" font-family="Segoe UI" font-size="12px" font-weight="bold" fill="#333">Схема {schema}</text>')
        leg_x += 140

    # Draw Connections (Lines, Arrows, Cardinalities, FK Badges)
    for link in fk_links:
        pts = link['pts']
        color = link['color']
        marker_id = "arrow-ref" if color == '#23497d' else "arrow-app"

        # Construct polyline / smooth path
        path_str = f"M {pts[0][0]} {pts[0][1]}"
        for pt in pts[1:]:
            path_str += f" L {pt[0]} {pt[1]}"

        # Background stroke for visibility
        svg.append(f'<path d="{path_str}" stroke="#ffffff" stroke-width="4" fill="none" />')
        # Main dashed line
        svg.append(f'<path d="{path_str}" class="conn-line" stroke="{color}" marker-end="url(#{marker_id})" />')

        # Start dot (PK source)
        svg.append(f'<circle cx="{pts[0][0]}" cy="{pts[0][1]}" r="3.5" fill="{color}" stroke="#fff" stroke-width="1.2" />')

        # Cardinality text at source
        c_src_x = pts[0][0] + (10 if pts[1][0] >= pts[0][0] else -15)
        c_src_y = pts[0][1] - 5
        svg.append(f'<text x="{c_src_x}" y="{c_src_y}" class="card-lbl" fill="{color}">{link["c_src"]}</text>')

        # Cardinality text at destination
        dst_pt = pts[-1]
        c_dst_x = dst_pt[0] + (-18 if pts[-2][0] <= dst_pt[0] else 10)
        c_dst_y = dst_pt[1] - 5
        svg.append(f'<text x="{c_dst_x}" y="{c_dst_y}" class="card-lbl" fill="{color}">{link["c_dst"]}</text>')

        # Small FK label pill along middle segment
        mid_idx = len(pts) // 2
        p1, p2 = pts[mid_idx-1], pts[mid_idx]
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        fk_name = link['fk']
        badge_w = len(fk_name) * 5.8 + 10
        svg.append(f'<rect x="{mx - badge_w/2}" y="{my - 7}" width="{badge_w}" height="14" rx="3" fill="{color}" opacity="0.9" />')
        svg.append(f'<text x="{mx}" y="{my + 3.5}" text-anchor="middle" class="fk-badge-txt">{fk_name}</text>')

    # Draw Tables
    for t in tables:
        full_name = f"{t['schema']}.{t['name']}"
        x = t['x']
        y = t['y']
        w = t['w']
        col_count = len(t['cols'])
        row_h = 20
        header_h = 26
        h = header_h + col_count * row_h + 8

        c = colors[t['schema']]
        # Table container with shadow
        svg.append(f'<g filter="url(#shadow)">')
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="1.4" />')
        # Header
        svg.append(f'<path d="M {x} {y+5} Q {x} {y} {x+5} {y} L {x+w-5} {y} Q {x+w} {y} {x+w} {y+5} L {x+w} {y+header_h} L {x} {y+header_h} Z" fill="{c["header"]}" />')
        svg.append(f'<text x="{x+10}" y="{y+18}" class="tbl-title">{full_name}</text>')
        svg.append('</g>')

        # Columns
        col_y = y + header_h + 16
        for key_type, col_name, data_type in t['cols']:
            key_cls = "pk" if key_type == "PK" else ("fk" if key_type == "FK" else ("uq" if key_type == "UQ" else "col-txt"))
            svg.append(f'<text x="{x+10}" y="{col_y}" class="col-txt {key_cls}">{key_type}</text>')
            svg.append(f'<text x="{x+36}" y="{col_y}" class="col-txt">{col_name}</text>')
            svg.append(f'<text x="{x+w-10}" y="{col_y}" class="col-txt type" text-anchor="end">{data_type}</text>')
            col_y += row_h

    svg.append('</svg>')

    os.makedirs('images', exist_ok=True)
    svg_path = os.path.join('images', 'er_diagram.svg')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print(f'Generated {svg_path} successfully.')

    # Convert to PNG using typst
    typst_wrapper = os.path.join('images', 'temp_er.typ')
    with open(typst_wrapper, 'w', encoding='utf-8') as f:
        f.write('#set page(width: auto, height: auto, margin: 5pt)\n#image("er_diagram.svg")\n')

    png_path = os.path.join('images', 'er_diagram.png')
    res = subprocess.run(['.\\typst.exe', 'compile', '--format', 'png', '--ppi', '160', typst_wrapper, png_path], capture_output=True, text=True)
    if os.path.exists(typst_wrapper):
        os.remove(typst_wrapper)

    if res.returncode == 0:
        print(f'Rendered {png_path} successfully (size: {os.path.getsize(png_path)} bytes).')
    else:
        print(f'Typst error: {res.stderr}')

if __name__ == '__main__':
    generate_svg()
