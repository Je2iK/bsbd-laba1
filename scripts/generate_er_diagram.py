import os
import subprocess

def generate_rock_solid_er():
    tables = [
        # Col 1: REF (x = 50, w = 240)
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 50, 'y': 50, 'w': 240,
            'cols': ['trust_level_id', 'code', 'name', 'auth_factor_min', 'description', 'is_active'],
            'pks': ['trust_level_id'], 'fks': []
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 50, 'y': 260, 'w': 240,
            'cols': ['doc_type_id', 'type_code', 'type_name', 'has_rfid_chip', 'validity_years'],
            'pks': ['doc_type_id'], 'fks': []
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 50, 'y': 470, 'w': 240,
            'cols': ['modality_id', 'code', 'name', 'iso_standard', 'far_limit', 'frr_limit'],
            'pks': ['modality_id'], 'fks': []
        },
        {
            'schema': 'ref', 'name': 'agencies', 'x': 50, 'y': 720, 'w': 240,
            'cols': ['agency_id', 'agency_code', 'agency_name', 'inn', 'ogrn', 'trust_tier', 'is_active'],
            'pks': ['agency_id'], 'fks': []
        },

        # Col 2: APP CORE (x = 390, w = 240)
        {
            'schema': 'app', 'name': 'citizens', 'x': 390, 'y': 50, 'w': 240,
            'cols': ['citizen_id', 'first_name', 'last_name', 'middle_name', 'birth_date', 'birth_place', 'gender', 'created_at'],
            'pks': ['citizen_id'], 'fks': []
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 390, 'y': 290, 'w': 240,
            'cols': ['profile_id', 'citizen_id', 'snils', 'inn', 'trust_level_id', 'profile_status', 'verified_at', 'created_at'],
            'pks': ['profile_id'], 'fks': ['citizen_id', 'trust_level_id']
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 390, 'y': 530, 'w': 240,
            'cols': ['passport_id', 'citizen_id', 'doc_type_id', 'chip_uid', 'series', 'number', 'issue_date', 'expiry_date', 'issuing_authority_code', 'encrypted_chip_payload', 'is_active'],
            'pks': ['passport_id'], 'fks': ['citizen_id', 'doc_type_id']
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 390, 'y': 840, 'w': 240,
            'cols': ['biometric_id', 'citizen_id', 'modality_id', 'template_hash', 'encrypted_template', 'quality_score', 'capture_device_id', 'registered_at', 'status'],
            'pks': ['biometric_id'], 'fks': ['citizen_id', 'modality_id']
        },

        # Col 3: APP ACCESS & AUDIT VERIF (x = 760, w = 250)
        {
            'schema': 'app', 'name': 'access_consents', 'x': 760, 'y': 170, 'w': 250,
            'cols': ['consent_id', 'profile_id', 'agency_id', 'scope', 'granted_at', 'valid_until', 'is_revoked', 'consent_signature'],
            'pks': ['consent_id'], 'fks': ['profile_id', 'agency_id']
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 760, 'y': 430, 'w': 250,
            'cols': ['token_id', 'profile_id', 'agency_id', 'required_trust_level_id', 'token_hash', 'issued_at', 'expires_at', 'status'],
            'pks': ['token_id'], 'fks': ['profile_id', 'agency_id', 'required_trust_level_id']
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 760, 'y': 710, 'w': 250,
            'cols': ['verification_id', 'verified_at', 'citizen_id', 'modality_id', 'agency_id', 'similarity_score', 'decision', 'client_ip'],
            'pks': ['verification_id'], 'fks': ['citizen_id', 'modality_id', 'agency_id']
        },

        # Col 4: AUDIT LOGS & STAGING (x = 1110, w = 240)
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1110, 'y': 60, 'w': 240,
            'cols': ['login_id', 'login_time', 'username', 'client_ip', 'client_port', 'auth_method', 'session_status'],
            'pks': ['login_id'], 'fks': []
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1110, 'y': 290, 'w': 240,
            'cols': ['change_id', 'changed_at', 'username', 'table_schema', 'table_name', 'operation', 'row_id', 'old_data', 'new_data'],
            'pks': ['change_id'], 'fks': []
        },
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1110, 'y': 580, 'w': 240,
            'cols': ['import_id', 'batch_uuid', 'source_system', 'raw_payload', 'loaded_at', 'status', 'error_message'],
            'pks': ['import_id'], 'fks': []
        },
    ]

    header_h = 24
    row_h = 20

    def get_row_y(t, col_name):
        idx = t['cols'].index(col_name)
        return t['y'] + header_h + idx * row_h + row_h / 2

    tmap = {f"{t['schema']}.{t['name']}": t for t in tables}

    # All 14 continuous polylines
    links = [
        # 1. trust_levels.trust_level_id -> digital_profiles.trust_level_id
        [(290, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
         (320, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
         (320, get_row_y(tmap['app.digital_profiles'], 'trust_level_id')),
         (390, get_row_y(tmap['app.digital_profiles'], 'trust_level_id'))],

        # 2. trust_levels.trust_level_id -> access_tokens.required_trust_level_id
        [(290, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
         (310, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
         (310, 250),
         (710, 250),
         (710, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id')),
         (760, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id'))],

        # 3. document_types.doc_type_id -> electronic_passports.doc_type_id
        [(290, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
         (330, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
         (330, get_row_y(tmap['app.electronic_passports'], 'doc_type_id')),
         (390, get_row_y(tmap['app.electronic_passports'], 'doc_type_id'))],

        # 4. biometric_modalities.modality_id -> biometric_templates.modality_id
        [(290, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
         (340, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
         (340, get_row_y(tmap['app.biometric_templates'], 'modality_id')),
         (390, get_row_y(tmap['app.biometric_templates'], 'modality_id'))],

        # 5. biometric_modalities.modality_id -> biometric_verifications.modality_id
        [(290, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
         (320, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
         (320, 500),
         (720, 500),
         (720, get_row_y(tmap['audit.biometric_verifications'], 'modality_id')),
         (760, get_row_y(tmap['audit.biometric_verifications'], 'modality_id'))],

        # 6. agencies.agency_id -> access_consents.agency_id
        [(290, get_row_y(tmap['ref.agencies'], 'agency_id')),
         (305, get_row_y(tmap['ref.agencies'], 'agency_id')),
         (305, 800),
         (730, 800),
         (730, get_row_y(tmap['app.access_consents'], 'agency_id')),
         (760, get_row_y(tmap['app.access_consents'], 'agency_id'))],

        # 7. agencies.agency_id -> access_tokens.agency_id
        [(290, get_row_y(tmap['ref.agencies'], 'agency_id')),
         (305, get_row_y(tmap['ref.agencies'], 'agency_id')),
         (305, 800),
         (740, 800),
         (740, get_row_y(tmap['app.access_tokens'], 'agency_id')),
         (760, get_row_y(tmap['app.access_tokens'], 'agency_id'))],

        # 8. agencies.agency_id -> biometric_verifications.agency_id
        [(290, get_row_y(tmap['ref.agencies'], 'agency_id')),
         (305, get_row_y(tmap['ref.agencies'], 'agency_id')),
         (305, 800),
         (750, 800),
         (750, get_row_y(tmap['audit.biometric_verifications'], 'agency_id')),
         (760, get_row_y(tmap['audit.biometric_verifications'], 'agency_id'))],

        # 9. citizens.citizen_id -> digital_profiles.citizen_id
        [(630, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.digital_profiles'], 'citizen_id')),
         (630, get_row_y(tmap['app.digital_profiles'], 'citizen_id'))],

        # 10. citizens.citizen_id -> electronic_passports.citizen_id
        [(630, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.electronic_passports'], 'citizen_id')),
         (630, get_row_y(tmap['app.electronic_passports'], 'citizen_id'))],

        # 11. citizens.citizen_id -> biometric_templates.citizen_id
        [(630, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.biometric_templates'], 'citizen_id')),
         (630, get_row_y(tmap['app.biometric_templates'], 'citizen_id'))],

        # 12. citizens.citizen_id -> biometric_verifications.citizen_id
        [(630, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['app.citizens'], 'citizen_id')),
         (670, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id')),
         (760, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id'))],

        # 13. digital_profiles.profile_id -> access_consents.profile_id
        [(630, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
         (690, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
         (690, get_row_y(tmap['app.access_consents'], 'profile_id')),
         (760, get_row_y(tmap['app.access_consents'], 'profile_id'))],

        # 14. digital_profiles.profile_id -> access_tokens.profile_id
        [(630, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
         (690, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
         (690, get_row_y(tmap['app.access_tokens'], 'profile_id')),
         (760, get_row_y(tmap['app.access_tokens'], 'profile_id'))],
    ]

    svg_w = 1400
    svg_h = 1090

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('''<defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <polygon points="0,0 10,5 0,10" fill="#ffffff" stroke="#000000" stroke-width="1.2" />
        </marker>
    </defs>''')
    svg.append('<style>')
    svg.append('''
        .tbl-border { fill: #ffffff; stroke: #000000; stroke-width: 1.2; }
        .row-line { stroke: #000000; stroke-width: 0.8; }
        .tbl-hdr { font-family: Arial, Helvetica, sans-serif; font-size: 11px; font-weight: bold; fill: #000000; text-anchor: middle; }
        .col-txt { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; fill: #000000; }
        .bold-tag { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; font-weight: bold; fill: #000000; }
        .conn-ortho { fill: none; stroke: #000000; stroke-width: 1; }
    ''')
    svg.append('</style>')

    # Pure white background
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#ffffff" />')

    # Draw Connections
    for pts in links:
        d_str = f"M {pts[0][0]} {pts[0][1]}"
        for pt in pts[1:]:
            d_str += f" L {pt[0]} {pt[1]}"
        svg.append(f'<path d="{d_str}" class="conn-ortho" marker-end="url(#arrow)" />')

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
        for r_idx, c in enumerate(t['cols']):
            curr_y = y + header_h + r_idx * row_h
            if r_idx > 0:
                svg.append(f'<line x1="{x}" y1="{curr_y}" x2="{x + w}" y2="{curr_y}" class="row-line" />')
            
            # Text inside row
            text_y = curr_y + 14
            if c in t['pks']:
                svg.append(f'<text x="{x + 8}" y="{text_y}" class="bold-tag">(PK) <tspan font-weight="normal">{c}</tspan></text>')
            elif c in t['fks']:
                svg.append(f'<text x="{x + 8}" y="{text_y}" class="bold-tag">(FK) <tspan font-weight="normal">{c}</tspan></text>')
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
    generate_rock_solid_er()
