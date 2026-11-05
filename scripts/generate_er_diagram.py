import os
import subprocess

def generate_exact_table_er():
    # 4 Columns layout with generous, clean corridors:
    # Col 1: ref (x = 50, w = 230)      -> right edge = 280
    # Corridor 1: 280 .. 420 (width 140)
    # Col 2: app core (x = 420, w = 240) -> right edge = 660
    # Corridor 2: 660 .. 830 (width 170)
    # Col 3: app access & audit verif (x = 830, w = 250) -> right edge = 1080
    # Corridor 3: 1080 .. 1130
    # Col 4: audit logs & stg (x = 1130, w = 240) -> right edge = 1370

    tables = [
        # Col 1: REF
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

        # Col 2: APP CORE
        {
            'schema': 'app', 'name': 'citizens', 'x': 420, 'y': 60, 'w': 240,
            'cols': ['(PK) citizen_id', 'first_name', 'last_name', 'middle_name', 'birth_date', 'birth_place', 'gender', 'created_at']
        },
        {
            'schema': 'app', 'name': 'digital_profiles', 'x': 420, 'y': 300, 'w': 240,
            'cols': ['(PK) profile_id', '(FK) citizen_id', 'snils', 'inn', '(FK) trust_level_id', 'profile_status', 'verified_at', 'created_at']
        },
        {
            'schema': 'app', 'name': 'electronic_passports', 'x': 420, 'y': 540, 'w': 240,
            'cols': ['(PK) passport_id', '(FK) citizen_id', '(FK) doc_type_id', 'chip_uid', 'series', 'number', 'issue_date', 'expiry_date', 'issuing_authority_code', 'encrypted_chip_payload', 'is_active']
        },
        {
            'schema': 'app', 'name': 'biometric_templates', 'x': 420, 'y': 840, 'w': 240,
            'cols': ['(PK) biometric_id', '(FK) citizen_id', '(FK) modality_id', 'template_hash', 'encrypted_template', 'quality_score', 'capture_device_id', 'registered_at', 'status']
        },

        # Col 3: APP ACCESS & AUDIT VERIF
        {
            'schema': 'app', 'name': 'access_consents', 'x': 850, 'y': 160, 'w': 250,
            'cols': ['(PK) consent_id', '(FK) profile_id', '(FK) agency_id', 'scope', 'granted_at', 'valid_until', 'is_revoked', 'consent_signature']
        },
        {
            'schema': 'app', 'name': 'access_tokens', 'x': 850, 'y': 410, 'w': 250,
            'cols': ['(PK) token_id', '(FK) profile_id', '(FK) agency_id', '(FK) required_trust_level_id', 'token_hash', 'issued_at', 'expires_at', 'status']
        },
        {
            'schema': 'audit', 'name': 'biometric_verifications', 'x': 850, 'y': 680, 'w': 250,
            'cols': ['(PK) verification_id', 'verified_at', '(FK) citizen_id', '(FK) modality_id', '(FK) agency_id', 'similarity_score', 'decision', 'client_ip']
        },

        # Col 4: AUDIT LOGS & STAGING
        {
            'schema': 'audit', 'name': 'login_log', 'x': 1160, 'y': 60, 'w': 240,
            'cols': ['(PK) login_id', 'login_time', 'username', 'client_ip', 'client_port', 'auth_method', 'session_status']
        },
        {
            'schema': 'audit', 'name': 'change_log', 'x': 1160, 'y': 290, 'w': 240,
            'cols': ['(PK) change_id', 'changed_at', 'username', 'table_schema', 'table_name', 'operation', 'row_id', 'old_data', 'new_data']
        },
        {
            'schema': 'stg', 'name': 'passport_batch_import', 'x': 1160, 'y': 560, 'w': 240,
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

    # Col 1 right edge = 280. Stub goes 280 -> 305. Label '1' at 293 (clear of table border <= 280 and vertical lines >= 315)
    # Col 2 right edge = 660. Stub goes 660 -> 685. Label '1' at 673 (clear of table border <= 660 and vertical lines >= 695)
    pk_stubs = [
        {'x1': 280, 'y': get_row_y(tmap['ref.trust_levels'], 'trust_level_id'), 'x2': 305, 'lbl_x': 293},
        {'x1': 280, 'y': get_row_y(tmap['ref.document_types'], 'doc_type_id'), 'x2': 305, 'lbl_x': 293},
        {'x1': 280, 'y': get_row_y(tmap['ref.biometric_modalities'], 'modality_id'), 'x2': 305, 'lbl_x': 293},
        {'x1': 280, 'y': get_row_y(tmap['ref.agencies'], 'agency_id'), 'x2': 305, 'lbl_x': 293},
        {'x1': 660, 'y': get_row_y(tmap['app.citizens'], 'citizen_id'), 'x2': 685, 'lbl_x': 673},
        {'x1': 660, 'y': get_row_y(tmap['app.digital_profiles'], 'profile_id'), 'x2': 685, 'lbl_x': 673},
    ]

    # Links definition:
    # Corridor 1 (280..420):
    #   Vertical drop lines:
    #     Line 2: x = 315
    #     Line 5: x = 328
    #     Line 6,7,8: x = 315 (from agency_id downwards)
    #     Line 1: x = 345
    #     Line 3: x = 360
    #     Line 4: x = 375
    #   Zone 390..420 is COMPLETELY FREE of vertical lines!
    #   All arrows into Col 2 enter at x = 420. Labels '1:N' are placed at x = 402. ZERO intersections!
    #
    # Corridor 2 (660..830):
    #   Vertical drop lines:
    #     Line 9:  x = 695 (loops back to digital_profiles at 660)
    #     Line 10: x = 708 (loops back to electronic_passports at 660)
    #     Line 11: x = 720 (loops back to biometric_templates at 660)
    #     Line 12: x = 732 (citizens -> biometric_verifications)
    #     Line 13: x = 744 (digital_profiles -> access_consents)
    #     Line 14: x = 756 (digital_profiles -> access_tokens)
    #     Line 2:  x = 768 (ref.trust_levels -> access_tokens)
    #     Line 5:  x = 778 (ref.biometric_modalities -> biometric_verifications)
    #     Line 6:  x = 788 (ref.agencies -> access_consents)
    #     Line 7:  x = 798 (ref.agencies -> access_tokens)
    #     Line 8:  x = 808 (ref.agencies -> biometric_verifications)
    #   Zone 815..830 is COMPLETELY FREE of vertical lines!
    #   All arrows into Col 3 enter at x = 830. Labels '1:N' are placed at x = 820. ZERO intersections!
    #   Loops back to Col 2 (Lines 9, 10, 11) enter at x = 660 from right.
    #   Horizontal loop line is from 695/708/720 back to 660.
    #   Label is placed at x = 678, perfectly between 660 and vertical lines >= 695.

    links = [
        # 1. ref.trust_levels.trust_level_id -> app.digital_profiles.trust_level_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (345, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (345, get_row_y(tmap['app.digital_profiles'], 'trust_level_id')),
                    (420, get_row_y(tmap['app.digital_profiles'], 'trust_level_id'))],
            'arrow_lbl': ('1:N', 402, get_row_y(tmap['app.digital_profiles'], 'trust_level_id') - 6),
        },

        # 2. ref.trust_levels.trust_level_id -> app.access_tokens.required_trust_level_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (315, get_row_y(tmap['ref.trust_levels'], 'trust_level_id')),
                    (315, 270),
                    (768, 270),
                    (768, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id')),
                    (850, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['app.access_tokens'], 'required_trust_level_id') - 6),
        },

        # 3. ref.document_types.doc_type_id -> app.electronic_passports.doc_type_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (360, get_row_y(tmap['ref.document_types'], 'doc_type_id')),
                    (360, get_row_y(tmap['app.electronic_passports'], 'doc_type_id')),
                    (420, get_row_y(tmap['app.electronic_passports'], 'doc_type_id'))],
            'arrow_lbl': ('1:N', 402, get_row_y(tmap['app.electronic_passports'], 'doc_type_id') - 6),
        },

        # 4. ref.biometric_modalities.modality_id -> app.biometric_templates.modality_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (375, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (375, get_row_y(tmap['app.biometric_templates'], 'modality_id')),
                    (420, get_row_y(tmap['app.biometric_templates'], 'modality_id'))],
            'arrow_lbl': ('1:N', 402, get_row_y(tmap['app.biometric_templates'], 'modality_id') - 6),
        },

        # 5. ref.biometric_modalities.modality_id -> audit.biometric_verifications.modality_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (328, get_row_y(tmap['ref.biometric_modalities'], 'modality_id')),
                    (328, 510),
                    (778, 510),
                    (778, get_row_y(tmap['audit.biometric_verifications'], 'modality_id')),
                    (850, get_row_y(tmap['audit.biometric_verifications'], 'modality_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['audit.biometric_verifications'], 'modality_id') - 6),
        },

        # 6. ref.agencies.agency_id -> app.access_consents.agency_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (315, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (315, 795),
                    (788, 795),
                    (788, get_row_y(tmap['app.access_consents'], 'agency_id')),
                    (850, get_row_y(tmap['app.access_consents'], 'agency_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['app.access_consents'], 'agency_id') - 6),
        },

        # 7. ref.agencies.agency_id -> app.access_tokens.agency_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (315, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (315, 808),
                    (798, 808),
                    (798, get_row_y(tmap['app.access_tokens'], 'agency_id')),
                    (850, get_row_y(tmap['app.access_tokens'], 'agency_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['app.access_tokens'], 'agency_id') - 6),
        },

        # 8. ref.agencies.agency_id -> audit.biometric_verifications.agency_id
        {
            'rel': '1:N',
            'pts': [(305, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (315, get_row_y(tmap['ref.agencies'], 'agency_id')),
                    (315, 821),
                    (808, 821),
                    (808, get_row_y(tmap['audit.biometric_verifications'], 'agency_id')),
                    (850, get_row_y(tmap['audit.biometric_verifications'], 'agency_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['audit.biometric_verifications'], 'agency_id') - 6),
        },

        # 9. app.citizens.citizen_id -> app.digital_profiles.citizen_id [UNIQUE FK: 1:1]
        {
            'rel': '1:1',
            'pts': [(685, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (695, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (695, get_row_y(tmap['app.digital_profiles'], 'citizen_id')),
                    (660, get_row_y(tmap['app.digital_profiles'], 'citizen_id'))],
            'arrow_lbl': ('1:1', 678, get_row_y(tmap['app.digital_profiles'], 'citizen_id') - 6),
        },

        # 10. app.citizens.citizen_id -> app.electronic_passports.citizen_id
        {
            'rel': '1:N',
            'pts': [(685, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (708, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (708, get_row_y(tmap['app.electronic_passports'], 'citizen_id')),
                    (660, get_row_y(tmap['app.electronic_passports'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 678, get_row_y(tmap['app.electronic_passports'], 'citizen_id') - 6),
        },

        # 11. app.citizens.citizen_id -> app.biometric_templates.citizen_id
        {
            'rel': '1:N',
            'pts': [(685, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (720, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (720, get_row_y(tmap['app.biometric_templates'], 'citizen_id')),
                    (660, get_row_y(tmap['app.biometric_templates'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 678, get_row_y(tmap['app.biometric_templates'], 'citizen_id') - 6),
        },

        # 12. app.citizens.citizen_id -> audit.biometric_verifications.citizen_id
        {
            'rel': '1:N',
            'pts': [(685, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (732, get_row_y(tmap['app.citizens'], 'citizen_id')),
                    (732, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id')),
                    (850, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['audit.biometric_verifications'], 'citizen_id') - 6),
        },

        # 13. app.digital_profiles.profile_id -> app.access_consents.profile_id
        {
            'rel': '1:N',
            'pts': [(685, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (744, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (744, get_row_y(tmap['app.access_consents'], 'profile_id')),
                    (850, get_row_y(tmap['app.access_consents'], 'profile_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['app.access_consents'], 'profile_id') - 6),
        },

        # 14. app.digital_profiles.profile_id -> app.access_tokens.profile_id
        {
            'rel': '1:N',
            'pts': [(685, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (756, get_row_y(tmap['app.digital_profiles'], 'profile_id')),
                    (756, get_row_y(tmap['app.access_tokens'], 'profile_id')),
                    (850, get_row_y(tmap['app.access_tokens'], 'profile_id'))],
            'arrow_lbl': ('1:N', 825, get_row_y(tmap['app.access_tokens'], 'profile_id') - 6),
        },
    ]

    svg_w = 1450
    svg_h = 1080

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('''<defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
            <path d="M 0 1.5 L 10 5 L 0 8.5 Z" fill="#000000" />
        </marker>
        <marker id="arrow-left" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
            <path d="M 10 1.5 L 0 5 L 10 8.5 Z" fill="#000000" />
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
                      text-anchor: middle; paint-order: stroke; stroke: #ffffff; stroke-width: 4px; stroke-linecap: round; stroke-linejoin: round; }
    ''')
    svg.append('</style>')

    # Pure white background
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#ffffff" />')

    # Draw PK Stubs (solid dot at exit + "1" label above stub)
    for s in pk_stubs:
        svg.append(f'<circle cx="{s["x1"]}" cy="{s["y"]}" r="3" fill="#000000" />')
        svg.append(f'<line x1="{s["x1"]}" y1="{s["y"]}" x2="{s["x2"]}" y2="{s["y"]}" class="conn-line" />')
        svg.append(f'<text x="{s["lbl_x"]}" y="{s["y"] - 6}" class="card-lbl">1</text>')

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
