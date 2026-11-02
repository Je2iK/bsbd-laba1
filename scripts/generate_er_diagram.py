import os
import subprocess

def generate_exact_table_er():
    tables = [
        # Col 1: REF (x = 50, w = 230)
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 50, 'y': 60, 'w': 230,
            'cols': ['(PK) trust_level_id', 'code', 'name', 'auth_factor_min', 'description', 'is_active']
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 50, 'y': 260, 'w': 230,
            'cols': ['(PK) doc_type_id', 'type_code', 'type_name', 'has_rfid_chip', 'validity_years']
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 50, 'y': 450, 'w': 230,
            'cols': ['(PK) modality_id', 'code', 'name', 'iso_standard', 'far_limit', 'frr_limit']
        },
        {
            'schema': 'ref', 'name': 'agencies', 'x': 50, 'y': 690, 'w': 230,
            'cols': ['(PK) agency_id', 'agency_code', 'agency_name', 'inn', 'ogrn', 'trust_tier', 'is_active']
        },

        # Col 2: APP CORE (x = 390, w = 240)
        {
            'schema': 'app', 'name': 'citizens', 'x': 390, 'y': 60, 'w': 240,
            'cols': ['(PK) citizen_id', 'first_name', 'last_name', 'middle_name', 'birth_date', 'birth_place', 'gender', 'created_at']
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 390, 'y': 300, 'w': 240,
            'cols': ['(PK) profile_id', '(FK) citizen_id', 'snils', 'inn', '(FK) trust_level_id', 'profile_status', 'verified_at', 'created_at']
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 390, 'y': 540, 'w': 240,
            'cols': ['(PK) passport_id', '(FK) citizen_id', '(FK) doc_type_id', 'chip_uid', 'series', 'number', 'issue_date', 'expiry_date', 'issuing_authority_code', 'encrypted_chip_payload', 'is_active']
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 390, 'y': 840, 'w': 240,
            'cols': ['(PK) biometric_id', '(FK) citizen_id', '(FK) modality_id', 'template_hash', 'encrypted_template', 'quality_score', 'capture_device_id', 'registered_at', 'status']
        },

        # Col 3: APP ACCESS & AUDIT VERIF (x = 760, w = 250)
        {
            'schema': 'app', 'name': 'access_consents', 'x': 760, 'y': 160, 'w': 250,
            'cols': ['(PK) consent_id', '(FK) profile_id', '(FK) agency_id', 'scope', 'granted_at', 'valid_until', 'is_revoked', 'consent_signature']
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 760, 'y': 410, 'w': 250,
            'cols': ['(PK) token_id', '(FK) profile_id', '(FK) agency_id', '(FK) required_trust_level_id', 'token_hash', 'issued_at', 'expires_at', 'status']
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 760, 'y': 680, 'w': 250,
            'cols': ['(PK) verification_id', 'verified_at', '(FK) citizen_id', '(FK) modality_id', '(FK) agency_id', 'similarity_score', 'decision', 'client_ip']
        },

        # Col 4: AUDIT LOGS & STAGING (x = 1110, w = 240)
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1110, 'y': 60, 'w': 240,
            'cols': ['(PK) login_id', 'login_time', 'username', 'client_ip', 'client_port', 'auth_method', 'session_status']
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1110, 'y': 290, 'w': 240,
            'cols': ['(PK) change_id', 'changed_at', 'username', 'table_schema', 'table_name', 'operation', 'row_id', 'old_data', 'new_data']
        },
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1110, 'y': 560, 'w': 240,
            'cols': ['(PK) import_id', 'batch_uuid', 'source_system', 'raw_payload', 'loaded_at', 'status', 'error_message']
        },
    ]

    header_h = 24
    row_h = 20

    def get_row_y(t, col_substr):
        for idx, col in enumerate(t['cols']):
            if col_substr in col:
                return t['y'] + header_h + idx * row_h + row_h / 2
        raise ValueError(f"Column {col_substr} not found in {t['name']}")

    tmap = {f"{t['schema']}.{t['name']}": t for t in tables}

    # PK Stubs (exit dot + single "1" label)
    # Col 1 right edge = 280
    # Col 2 right edge = 630
    pk_stubs = [
        {'x1': 280, 'y': get_row_y(tmap['ref.trust_levels'], 'trust_level_id'), 'x2': 295, 'lbl_x': 286},
        {'x1': 280, 'y': get_row_y(tmap['ref.document_types'], 'doc_type_id'), 'x2': 295, 'lbl_x': 286},
        {'x1': 280, 'y': get_row_y(tmap['ref.biometric_modalities'], 'modality_id'), 'x2': 295, 'lbl_x': 286},
        {'x1': 280, 'y': get_row_y(tmap['ref.agencies'], 'agency_id'), 'x2': 295, 'lbl_x': 286},
        {'x1': 630, 'y': get_row_y(tmap['app.citizens'], 'citizen_id'), 'x2': 645, 'lbl_x': 636},
        {'x1': 630, 'y': get_row_y(tmap['app.digital_profiles'], 'profile_id'), 'x2': 645, 'lbl_x': 636},
    ]

    # 14 Discrete, perfectly routed orthogonal lines with "1:N" or "1:1" right at the arrow!
    links = [
        # 1. ref.trust_levels.trust_level_id -> app.digital_profiles.trust_level_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (320, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (320, get_row_y(tmap['app.digital_profiles'], 'trust_level_id')),
                    (390, get_row_y(tmap['app.digital_profiles'], 'trust_level_id'))],
            'arrow_lbl': ('1:N', 366, get_row_y(tmap['app.digital_profiles'], 'trust_level_id') - 5),
        },

        # 2. ref.trust_levels.trust_level_id -> app.access_tokens.required_trust_level_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (305, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (305, 270),
                    (710, 270),
                    (710, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id')),
                    (760, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id') - 5),
        },

        # 3. ref.document_types.doc_type_id -> app.electronic_passports.doc_type_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (335, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (335, get_row_y(tmap['app.electronic_passports'], 'doc_type_id')),
                    (390, get_row_y(tmap['app.electronic_passports'], 'doc_type_id'))],
            'arrow_lbl': ('1:N', 366, get_row_y(tmap['app.electronic_passports'], 'doc_type_id') - 5),
        },

        # 4. ref.biometric_modalities.modality_id -> app.biometric_templates.modality_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (350, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (350, get_row_y(tmap['app.biometric_templates'], 'modality_id')),
                    (390, get_row_y(tmap['app.biometric_templates'], 'modality_id'))],
            'arrow_lbl': ('1:N', 366, get_row_y(tmap['app.biometric_templates'], 'modality_id') - 5),
        },

        # 5. ref.biometric_modalities.modality_id -> audit.biometric_verifications.modality_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (320, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (320, 510),
                    (720, 510),
                    (720, get_row_y(tmap['audit.biometric_verifications'], 'modality_id')),
                    (760, get_row_y(tmap['audit.biometric_verifications'], 'modality_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['audit.biometric_verifications'], 'modality_id') - 5),
        },

        # 6. ref.agencies.agency_id -> app.access_consents.agency_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (305, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (305, 795),
                    (730, 795),
                    (730, get_row_y(tmap['app.access_consents'], 'agency_id')),
                    (760, get_row_y(tmap['app.access_consents'], 'agency_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['app.access_consents'], 'agency_id') - 5),
        },

        # 7. ref.agencies.agency_id -> app.access_tokens.agency_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (305, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (305, 808),
                    (740, 808),
                    (740, get_row_y(tmap['app.access_tokens'], 'agency_id')),
                    (760, get_row_y(tmap['app.access_tokens'], 'agency_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['app.access_tokens'], 'agency_id') - 5),
        },

        # 8. ref.agencies.agency_id -> audit.biometric_verifications.agency_id
        {
            'rel': '1:N',
            'pts': [(295, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (305, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (305, 821),
                    (750, 821),
                    (750, get_row_y(tmap['audit.biometric_verifications'], 'agency_id')),
                    (760, get_row_y(tmap['audit.biometric_verifications'], 'agency_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['audit.biometric_verifications'], 'agency_id') - 5),
        },

        # 9. app.citizens.citizen_id -> app.digital_profiles.citizen_id [UNIQUE FK: 1:1]
        {
            'rel': '1:1',
            'pts': [(645, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (665, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (665, get_row_y(tmap['app.digital_profiles'], 'citizen_id')),
                    (630, get_row_y(tmap['app.digital_profiles'], 'citizen_id'))],
            'arrow_lbl': ('1:1', 638, get_row_y(tmap['app.digital_profiles'], 'citizen_id') - 5),
        },

        # 10. app.citizens.citizen_id -> app.electronic_passports.citizen_id
        {
            'rel': '1:N',
            'pts': [(645, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (675, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (675, get_row_y(tmap['app.electronic_passports'], 'citizen_id')),
                    (630, get_row_y(tmap['app.electronic_passports'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 638, get_row_y(tmap['app.electronic_passports'], 'citizen_id') - 5),
        },

        # 11. app.citizens.citizen_id -> app.biometric_templates.citizen_id
        {
            'rel': '1:N',
            'pts': [(645, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (685, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (685, get_row_y(tmap['app.biometric_templates'], 'citizen_id')),
                    (630, get_row_y(tmap['app.biometric_templates'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 638, get_row_y(tmap['app.biometric_templates'], 'citizen_id') - 5),
        },

        # 12. app.citizens.citizen_id -> audit.biometric_verifications.citizen_id
        {
            'rel': '1:N',
            'pts': [(645, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (695, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (695, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id')),
                    (760, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id') - 5),
        },

        # 13. app.digital_profiles.profile_id -> app.access_consents.profile_id
        {
            'rel': '1:N',
            'pts': [(645, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (705, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (705, get_row_y(tmap['app.access_consents'], 'profile_id')),
                    (760, get_row_y(tmap['app.access_consents'], 'profile_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['app.access_consents'], 'profile_id') - 5),
        },

        # 14. app.digital_profiles.profile_id -> app.access_tokens.profile_id
        {
            'rel': '1:N',
            'pts': [(645, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (715, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (715, get_row_y(tmap['app.access_tokens'], 'profile_id')),
                    (760, get_row_y(tmap['app.access_tokens'], 'profile_id'))],
            'arrow_lbl': ('1:N', 736, get_row_y(tmap['app.access_tokens'], 'profile_id') - 5),
        },
    ]

    svg_w = 1400
    svg_h = 1080

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('''<defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
            <path d="M 0 1.5 L 10 5 L 0 8.5 Z" fill="#000000" />
        </marker>
    </defs>''')
    svg.append('<style>')
    svg.append('''
        .tbl-border { fill: #ffffff; stroke: #000000; stroke-width: 1.1; }
        .row-line   { stroke: #000000; stroke-width: 0.8; }
        .tbl-hdr    { font-family: Arial, Helvetica, sans-serif; font-size: 11px; font-weight: bold; fill: #000000; text-anchor: middle; }
        .col-txt    { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; fill: #000000; }
        .bold-tag   { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; font-weight: bold; fill: #000000; }
        .conn-line  { fill: none; stroke: #000000; stroke-width: 1.1; }
        .card-lbl   { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; font-weight: bold; fill: #000000;
                      paint-order: stroke; stroke: #ffffff; stroke-width: 3.5px; stroke-linecap: round; stroke-linejoin: round; }
    ''')
    svg.append('</style>')

    # Pure white background
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#ffffff" />')

    # Draw PK Stubs (solid dot at exit + "1" label)
    for s in pk_stubs:
        svg.append(f'<circle cx="{s["x1"]}" cy="{s["y"]}" r="3" fill="#000000" />')
        svg.append(f'<line x1="{s["x1"]}" y1="{s["y"]}" x2="{s["x2"]}" y2="{s["y"]}" class="conn-line" />')
        svg.append(f'<text x="{s["lbl_x"]}" y="{s["y"] - 5}" class="card-lbl">1</text>')

    # Draw Connections
    for l in links:
        pts = l['pts']
        d_str = f"M {pts[0][0]} {pts[0][1]}"
        for pt in pts[1:]:
            d_str += f" L {pt[0]} {pt[1]}"
        
        svg.append(f'<path d="{d_str}" class="conn-line" marker-end="url(#arrow)" />')

        # Relationship label right at the arrow (e.g. 1:N or 1:1)
        r_txt, rx, ry = l['arrow_lbl']
        svg.append(f'<text x="{rx}" y="{ry}" class="card-lbl">{r_txt}</text>')

    # Draw Tables (Pure black & white table grid matching uploaded sample)
    for t in tables:
        x, y, w = t['x'], t['y'], t['w']
        col_count = len(t['cols'])
        h = header_h + col_count * row_h
        full_name = f"{t['schema']}.{t['name']}"

        # Outer border
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="tbl-border" />')
        
        # Header text (centered, bold)
        svg.append(f'<text x="{x + w/2}" y="{y + 16}" class="tbl-hdr">{full_name}</text>')
        # Header bottom line
        svg.append(f'<line x1="{x}" y1="{y + header_h}" x2="{x + w}" y2="{y + header_h}" class="row-line" />')

        # Rows
        for r_idx, c in enumerate(t['cols']):
            curr_y = y + header_h + r_idx * row_h
            if r_idx > 0:
                svg.append(f'<line x1="{x}" y1="{curr_y}" x2="{x + w}" y2="{curr_y}" class="row-line" />')
            
            text_y = curr_y + 14
            if c.startswith('(PK)'):
                svg.append(f'<text x="{x + 8}" y="{text_y}" class="bold-tag">(PK) <tspan font-weight="normal">{c[5:]}</tspan></text>')
            elif c.startswith('(FK)'):
                svg.append(f'<text x="{x + 8}" y="{text_y}" class="bold-tag">(FK) <tspan font-weight="normal">{c[5:]}</tspan></text>')
            else:
                svg.append(f'<text x="{x + 8}" y="{text_y}" class="col-txt">{c}</text>')

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
    generate_exact_table_er()
