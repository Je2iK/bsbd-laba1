import os
import subprocess

def generate_perfect_bw_er():
    tables = [
        # Col 1: REF (x = 40, w = 230)
        {
            'schema': 'ref', 'name': 'trust_levels', 'x': 40, 'y': 40, 'w': 230,
            'cols': ['trust_level_id', 'code', 'name', 'auth_factor_min', 'description', 'is_active'],
            'pks': ['trust_level_id'], 'fks': []
        },
        {
            'schema': 'ref', 'name': 'document_types', 'x': 40, 'y': 240, 'w': 230,
            'cols': ['doc_type_id', 'type_code', 'type_name', 'has_rfid_chip', 'validity_years'],
            'pks': ['doc_type_id'], 'fks': []
        },
        {
            'schema': 'ref', 'name': 'biometric_modalities', 'x': 40, 'y': 440, 'w': 230,
            'cols': ['modality_id', 'code', 'name', 'iso_standard', 'far_limit', 'frr_limit'],
            'pks': ['modality_id'], 'fks': []
        },
        {
            'schema': 'ref', 'name': 'agencies', 'x': 40, 'y': 660, 'w': 230,
            'cols': ['agency_id', 'agency_code', 'agency_name', 'inn', 'ogrn', 'trust_tier', 'is_active'],
            'pks': ['agency_id'], 'fks': []
        },

        # Col 2: APP CORE (x = 350, w = 240)
        {
            'schema': 'app', 'name': 'citizens', 'x': 350, 'y': 40, 'w': 240,
            'cols': ['citizen_id', 'first_name', 'last_name', 'middle_name', 'birth_date', 'birth_place', 'gender', 'created_at'],
            'pks': ['citizen_id'], 'fks': []
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 350, 'y': 280, 'w': 240,
            'cols': ['profile_id', 'citizen_id', 'snils', 'inn', 'trust_level_id', 'profile_status', 'verified_at', 'created_at'],
            'pks': ['profile_id'], 'fks': ['citizen_id', 'trust_level_id']
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 350, 'y': 520, 'w': 240,
            'cols': ['passport_id', 'citizen_id', 'doc_type_id', 'chip_uid', 'series', 'number', 'issue_date', 'expiry_date', 'issuing_authority_code', 'encrypted_chip_payload', 'is_active'],
            'pks': ['passport_id'], 'fks': ['citizen_id', 'doc_type_id']
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 350, 'y': 820, 'w': 240,
            'cols': ['biometric_id', 'citizen_id', 'modality_id', 'template_hash', 'encrypted_template', 'quality_score', 'capture_device_id', 'registered_at', 'status'],
            'pks': ['biometric_id'], 'fks': ['citizen_id', 'modality_id']
        },

        # Col 3: APP ACCESS & AUDIT VERIF (x = 690, w = 250)
        {
            'schema': 'app', 'name': 'access_consents', 'x': 690, 'y': 170, 'w': 250,
            'cols': ['consent_id', 'profile_id', 'agency_id', 'scope', 'granted_at', 'valid_until', 'is_revoked', 'consent_signature'],
            'pks': ['consent_id'], 'fks': ['profile_id', 'agency_id']
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 690, 'y': 410, 'w': 250,
            'cols': ['token_id', 'profile_id', 'agency_id', 'required_trust_level_id', 'token_hash', 'issued_at', 'expires_at', 'status'],
            'pks': ['token_id'], 'fks': ['profile_id', 'agency_id', 'required_trust_level_id']
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 690, 'y': 670, 'w': 250,
            'cols': ['verification_id', 'verified_at', 'citizen_id', 'modality_id', 'agency_id', 'similarity_score', 'decision', 'client_ip'],
            'pks': ['verification_id'], 'fks': ['citizen_id', 'modality_id', 'agency_id']
        },

        # Col 4: AUDIT LOGS & STAGING (x = 1010, w = 240)
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1010, 'y': 60, 'w': 240,
            'cols': ['login_id', 'login_time', 'username', 'client_ip', 'client_port', 'auth_method', 'session_status'],
            'pks': ['login_id'], 'fks': []
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1010, 'y': 280, 'w': 240,
            'cols': ['change_id', 'changed_at', 'username', 'table_schema', 'table_name', 'operation', 'row_id', 'old_data', 'new_data'],
            'pks': ['change_id'], 'fks': []
        },
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1010, 'y': 560, 'w': 240,
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

    # Line paths (polylines with right angles)
    # Target ends get arrow marker
    polylines = []

    # 1. citizen_id bus:
    # From app.citizens.citizen_id (350+240=590, y)
    cit_y = get_row_y(tmap['app.citizens'], 'citizen_id')
    bus_cit_x = 640
    # Main trunk
    polylines.append([(590, cit_y), (bus_cit_x, cit_y), (bus_cit_x, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id'))])
    # Branch to digital_profiles (citizen_id at left side: x=590 right side, enters at right: (bus_cit_x, dp_y) -> (590, dp_y))
    dp_cit_y = get_row_y(tmap['app.digital_profiles'], 'citizen_id')
    polylines.append([(bus_cit_x, dp_cit_y), (590, dp_cit_y)])
    # Branch to electronic_passports (citizen_id at right side: (bus_cit_x, ep_y) -> (590, ep_y))
    ep_cit_y = get_row_y(tmap['app.electronic_passports'], 'citizen_id')
    polylines.append([(bus_cit_x, ep_cit_y), (590, ep_cit_y)])
    # Branch to biometric_templates (citizen_id at right side: (bus_cit_x, bt_y) -> (590, bt_y))
    bt_cit_y = get_row_y(tmap['app.biometric_templates'], 'citizen_id')
    polylines.append([(bus_cit_x, bt_cit_y), (590, bt_cit_y)])
    # Branch to biometric_verifications (left side: (bus_cit_x, bv_cit_y) -> (690, bv_cit_y))
    bv_cit_y = get_row_y(tmap['audit.biometric_verifications'], 'citizen_id')
    polylines.append([(bus_cit_x, bv_cit_y), (690, bv_cit_y)])

    # 2. profile_id bus:
    # From app.digital_profiles.profile_id (590, dp_prof_y)
    dp_prof_y = get_row_y(tmap['app.digital_profiles'], 'profile_id')
    bus_prof_x = 655
    ac_prof_y = get_row_y(tmap['app.access_consents'], 'profile_id')
    at_prof_y = get_row_y(tmap['app.access_tokens'], 'profile_id')
    polylines.append([(590, dp_prof_y), (bus_prof_x, dp_prof_y), (bus_prof_x, at_prof_y)])
    polylines.append([(bus_prof_x, ac_prof_y), (690, ac_prof_y)])
    polylines.append([(bus_prof_x, at_prof_y), (690, at_prof_y)])

    # 3. agency_id bus:
    # From ref.agencies.agency_id (270, ag_y)
    ag_y = get_row_y(tmap['ref.agencies'], 'agency_id')
    bus_ag_x1 = 300
    cross_ag_y = 780 # corridor between passports and biometrics
    bus_ag_x2 = 670
    ac_ag_y = get_row_y(tmap['app.access_consents'], 'agency_id')
    at_ag_y = get_row_y(tmap['app.access_tokens'], 'agency_id')
    bv_ag_y = get_row_y(tmap['audit.biometric_verifications'], 'agency_id')
    polylines.append([(270, ag_y), (bus_ag_x1, ag_y), (bus_ag_x1, cross_ag_y), (bus_ag_x2, cross_ag_y), (bus_ag_x2, ac_ag_y)])
    polylines.append([(bus_ag_x2, ac_ag_y), (690, ac_ag_y)])
    polylines.append([(bus_ag_x2, at_ag_y), (690, at_ag_y)])
    polylines.append([(bus_ag_x2, bv_ag_y), (690, bv_ag_y)])

    # 4. trust_level_id:
    # From ref.trust_levels.trust_level_id (270, tl_y)
    tl_y = get_row_y(tmap['ref.trust_levels'], 'trust_level_id')
    dp_tl_y = get_row_y(tmap['app.digital_profiles'], 'trust_level_id')
    at_req_tl_y = get_row_y(tmap['app.access_tokens'], 'required_trust_level_id')
    bus_tl_x = 315
    cross_tl_y = 255 # corridor between citizens and digital_profiles
    bus_tl_x2 = 662
    # Branch to digital_profiles
    polylines.append([(270, tl_y), (bus_tl_x, tl_y), (bus_tl_x, dp_tl_y), (350, dp_tl_y)])
    # Branch to access_tokens
    polylines.append([(bus_tl_x, cross_tl_y), (bus_tl_x2, cross_tl_y), (bus_tl_x2, at_req_tl_y), (690, at_req_tl_y)])

    # 5. doc_type_id:
    # From ref.document_types.doc_type_id (270, dt_y) to app.electronic_passports.doc_type_id (350, ep_dt_y)
    dt_y = get_row_y(tmap['ref.document_types'], 'doc_type_id')
    ep_dt_y = get_row_y(tmap['app.electronic_passports'], 'doc_type_id')
    polylines.append([(270, dt_y), (325, dt_y), (325, ep_dt_y), (350, ep_dt_y)])

    # 6. modality_id:
    # From ref.biometric_modalities.modality_id (270, mod_y)
    mod_y = get_row_y(tmap['ref.biometric_modalities'], 'modality_id')
    bt_mod_y = get_row_y(tmap['app.biometric_templates'], 'modality_id')
    bv_mod_y = get_row_y(tmap['audit.biometric_verifications'], 'modality_id')
    bus_mod_x = 335
    cross_mod_y = 795
    bus_mod_x2 = 678
    # Branch to biometric_templates
    polylines.append([(270, mod_y), (bus_mod_x, mod_y), (bus_mod_x, bt_mod_y), (350, bt_mod_y)])
    # Branch to biometric_verifications
    polylines.append([(bus_mod_x, cross_mod_y), (bus_mod_x2, cross_mod_y), (bus_mod_x2, bv_mod_y), (690, bv_mod_y)])

    svg_w = 1290
    svg_h = 1040

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('''<defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
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
    for pts in polylines:
        d_str = f"M {pts[0][0]} {pts[0][1]}"
        for pt in pts[1:]:
            d_str += f" L {pt[0]} {pt[1]}"
        
        # Check if last point touches a table border -> add arrow marker
        last_x = pts[-1][0]
        # In our layout, target table inputs are at x=350, x=590, x=690
        has_arrow = last_x in (350, 590, 690)
        marker_attr = ' marker-end="url(#arrow)"' if has_arrow else ''
        svg.append(f'<path d="{d_str}" class="conn-ortho"{marker_attr} />')

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
    generate_perfect_bw_er()
