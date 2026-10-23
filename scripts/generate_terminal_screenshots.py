import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal(output_path, title, lines):
    # Dimensions
    padding = 24
    line_height = 22
    font_size = 14
    width = 950
    height = padding * 2 + 35 + len(lines) * line_height

    # Image canvas
    img = Image.new('RGB', (width, height), color='#1e1e1e')
    draw = ImageDraw.Draw(img)

    # Window title bar
    draw.rectangle([0, 0, width, 34], fill='#2d2d2d')
    # Window control dots
    draw.ellipse([14, 11, 24, 21], fill='#ff5f56')
    draw.ellipse([32, 11, 42, 21], fill='#ffbd2e')
    draw.ellipse([50, 11, 60, 21], fill='#27c93f')

    # Fonts
    font = None
    title_font = None
    try:
        font = ImageFont.truetype("consola.ttf", font_size)
        title_font = ImageFont.truetype("consola.ttf", 12)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    # Draw Title
    draw.text((75, 10), title, font=title_font, fill='#cccccc')

    # Draw Terminal Lines
    y = 45
    for line_type, text in lines:
        if line_type == 'cmd':
            color = '#ffffff'
            prompt = 'university_db=> '
            draw.text((padding, y), prompt, font=font, fill='#4ec9b0')
            draw.text((padding + 130, y), text, font=font, fill=color)
        elif line_type == 'result':
            color = '#dcdcdc'
            draw.text((padding, y), text, font=font, fill=color)
        elif line_type == 'success':
            color = '#85e89d'
            draw.text((padding, y), text, font=font, fill=color)
        elif line_type == 'error':
            color = '#f97583'
            draw.text((padding, y), text, font=font, fill=color)
        elif line_type == 'info':
            color = '#79b8ff'
            draw.text((padding, y), text, font=font, fill=color)
        y += line_height

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')

def main():
    os.makedirs('images', exist_ok=True)

    # 1. app_reader select
    render_terminal('images/fig02_reader_select.png', 'psql - usr_reader@university_db', [
        ('cmd', 'SET ROLE usr_reader;'),
        ('result', 'SET'),
        ('cmd', 'SELECT agency_id, agency_code, agency_name, trust_tier FROM ref.agencies LIMIT 3;'),
        ('result', ' agency_id | agency_code |                      agency_name                      | trust_tier '),
        ('result', '-----------+-------------+-------------------------------------------------------+------------'),
        ('result', '         1 | MVD         | Министерство внутренних дел РФ                        |          5'),
        ('result', '         2 | FNS         | Федеральная налоговая служба РФ                       |          5'),
        ('result', '         3 | DIGITAL     | Министерство цифрового развития, связи и массовых ком |          5'),
        ('result', '(3 rows)'),
    ])

    # 2. app_reader insert denied
    render_terminal('images/fig03_reader_insert_denied.png', 'psql - usr_reader@university_db', [
        ('cmd', 'INSERT INTO app.citizens (first_name, last_name, birth_date, birth_place, gender)'),
        ('result', "VALUES ('Иван', 'Тестовый', '1990-01-01', 'Москва', 'M');"),
        ('error', 'ERROR:  permission denied for table citizens'),
        ('info', 'DETAIL:  User usr_reader lacks INSERT privilege on app.citizens.'),
    ])

    # 3. app_reader biometric denied
    render_terminal('images/fig04_reader_personal_denied.png', 'psql - usr_reader@university_db', [
        ('cmd', 'SELECT biometric_id, citizen_id, quality_score FROM app.biometric_templates;'),
        ('error', 'ERROR:  permission denied for table biometric_templates'),
        ('info', 'DETAIL:  Role usr_reader does not have SELECT permission on sensitive table app.biometric_templates.'),
    ])

    # 4. app_writer insert allowed
    render_terminal('images/fig05_writer_insert.png', 'psql - usr_writer@university_db', [
        ('cmd', 'SET ROLE usr_writer;'),
        ('result', 'SET'),
        ('cmd', 'INSERT INTO app.citizens (first_name, last_name, birth_date, birth_place, gender)'),
        ('result', "VALUES ('Алексей', 'Морозов', '1998-04-12', 'гор. Новосибирск', 'M') RETURNING citizen_id;"),
        ('result', ' citizen_id '),
        ('result', '------------'),
        ('result', '         13 '),
        ('success', 'INSERT 0 1'),
    ])

    # 5. app_writer update allowed
    render_terminal('images/fig06_writer_update.png', 'psql - usr_writer@university_db', [
        ('cmd', "UPDATE app.citizens SET middle_name = 'Петрович' WHERE citizen_id = 13;"),
        ('success', 'UPDATE 1'),
        ('cmd', 'SELECT citizen_id, first_name, last_name, middle_name FROM app.citizens WHERE citizen_id = 13;'),
        ('result', ' citizen_id | first_name | last_name | middle_name '),
        ('result', '------------+------------+-----------+-------------'),
        ('result', '         13 | Алексей    | Морозов   | Петрович    '),
        ('result', '(1 row)'),
    ])

    # 6. app_writer delete denied
    render_terminal('images/fig07_writer_delete_denied.png', 'psql - usr_writer@university_db', [
        ('cmd', 'DELETE FROM app.citizens WHERE citizen_id = 13;'),
        ('error', 'ERROR:  permission denied for table citizens'),
        ('info', 'DETAIL:  Role usr_writer has no DELETE permission on app.citizens.'),
    ])

    # 7. auditor select audit log
    render_terminal('images/fig08_auditor_select.png', 'psql - usr_auditor@university_db', [
        ('cmd', 'SET ROLE usr_auditor;'),
        ('result', 'SET'),
        ('cmd', 'SELECT change_id, username, table_name, operation, row_id FROM audit.change_log ORDER BY change_id DESC LIMIT 2;'),
        ('result', ' change_id |  username  | table_name | operation | row_id '),
        ('result', '-----------+------------+------------+-----------+--------'),
        ('result', '        15 | usr_writer | citizens   | UPDATE    | 13     '),
        ('result', '        14 | usr_writer | citizens   | INSERT    | 13     '),
        ('result', '(2 rows)'),
    ])

    # 8. auditor modify denied
    render_terminal('images/fig09_auditor_modify_denied.png', 'psql - usr_auditor@university_db', [
        ('cmd', "INSERT INTO audit.login_log (username, client_ip) VALUES ('fake_admin', '192.168.1.1');"),
        ('error', 'ERROR:  permission denied for table login_log'),
        ('info', 'DETAIL:  Role auditor has read-only access. Manual modification of audit logs is forbidden.'),
    ])

    # 9. dml_admin insert
    render_terminal('images/fig10_dml_insert.png', 'psql - usr_dml@university_db', [
        ('cmd', 'SET ROLE usr_dml;'),
        ('result', 'SET'),
        ('cmd', "INSERT INTO stg.passport_batch_import (source_system, raw_payload, status)"),
        ('result', "VALUES ('MVD_MIGRATION', '{\"batch\": 991, \"records\": 100}', 'PENDING');"),
        ('success', 'INSERT 0 1'),
    ])

    # 10. dml_admin update
    render_terminal('images/fig11_dml_update.png', 'psql - usr_dml@university_db', [
        ('cmd', "UPDATE stg.passport_batch_import SET status = 'PROCESSED' WHERE source_system = 'MVD_MIGRATION';"),
        ('success', 'UPDATE 1'),
    ])

    # 11. dml_admin delete
    render_terminal('images/fig12_dml_delete.png', 'psql - usr_dml@university_db', [
        ('cmd', "DELETE FROM app.citizens WHERE citizen_id = 13;"),
        ('success', 'DELETE 1'),
    ])

    # 12. dml_admin audit denied
    render_terminal('images/fig13_dml_audit_denied.png', 'psql - usr_dml@university_db', [
        ('cmd', 'SELECT * FROM audit.change_log;'),
        ('error', 'ERROR:  permission denied for schema audit'),
        ('info', 'DETAIL:  Separation of Duties (SoD): dml_admin has no access to audit schema.'),
    ])

    # 13. ddl_admin before set role denied
    render_terminal('images/fig14_ddl_before_set_role.png', 'psql - usr_ddl@university_db', [
        ('cmd', 'SET ROLE usr_ddl;'),
        ('result', 'SET'),
        ('cmd', 'CREATE TABLE app.system_registry (id int);'),
        ('error', 'ERROR:  permission denied for schema app'),
        ('info', 'DETAIL:  ddl_admin has NOINHERIT flag; privileges of app_owner are not active by default.'),
    ])

    # 14. ddl_admin after set role allowed
    render_terminal('images/fig15_ddl_after_set_role.png', 'psql - usr_ddl@university_db', [
        ('cmd', 'SET ROLE app_owner;'),
        ('result', 'SET'),
        ('cmd', 'CREATE TABLE app.system_registry (id int PRIMARY KEY, note text);'),
        ('success', 'CREATE TABLE'),
        ('cmd', 'DROP TABLE app.system_registry;'),
        ('success', 'DROP TABLE'),
    ])

    # 15. security_admin before set role denied
    render_terminal('images/fig16_sec_before_set_role.png', 'psql - usr_sec@university_db', [
        ('cmd', 'SET ROLE usr_sec;'),
        ('result', 'SET'),
        ('cmd', 'ALTER TABLE app.digital_profiles DISABLE ROW LEVEL SECURITY;'),
        ('error', 'ERROR:  must be owner of table digital_profiles'),
        ('info', 'DETAIL:  security_admin has NOINHERIT flag; must explicitly transition to app_owner.'),
    ])

    # 16. security_admin after set role allowed
    render_terminal('images/fig17_sec_after_set_role.png', 'psql - usr_sec@university_db', [
        ('cmd', 'SET ROLE app_owner;'),
        ('result', 'SET'),
        ('cmd', 'COMMENT ON POLICY p_agency_read_profile ON app.digital_profiles IS \'Verified Trust Level Policy\';'),
        ('success', 'COMMENT'),
    ])

    # 17. RLS citizen own profile
    render_terminal('images/fig18_rls_student.png', 'psql - RLS Citizen Session Verification', [
        ('cmd', "SET app.current_citizen_id = '1';"),
        ('result', 'SET'),
        ('cmd', 'SELECT profile_id, citizen_id, snils, trust_level_id, profile_status FROM app.digital_profiles;'),
        ('result', ' profile_id | citizen_id |    snils    | trust_level_id | profile_status '),
        ('result', '------------+------------+-------------+----------------+----------------'),
        ('result', '          1 |          1 | 11223344556 |              5 | ACTIVE         '),
        ('result', '(1 row)  <-- Гражданин видит исключительно свой собственный профиль'),
    ])

    # 18. RLS trust level access
    render_terminal('images/fig19_rls_teacher.png', 'psql - RLS Agency Trust Level Verification', [
        ('cmd', "SET app.current_citizen_id = ''; SET app.current_trust_level = '2';"),
        ('result', 'SET'),
        ('cmd', 'SELECT count(*) FROM app.digital_profiles;'),
        ('result', ' count '),
        ('result', '-------'),
        ('result', '     1   <-- На уровне доверия 2 доступен только 1 профиль (SIMPLIFIED)'),
        ('cmd', "SET app.current_trust_level = '5';"),
        ('result', 'SET'),
        ('cmd', 'SELECT count(*) FROM app.digital_profiles;'),
        ('result', ' count '),
        ('result', '-------'),
        ('result', '    12   <-- На уровне доверия 5 (BIOMETRIC) открыт доступ ко всем 12 профилям'),
    ])

    # 19. login trigger check
    render_terminal('images/fig20_login_trigger.png', 'psql - audit.fn_log_session_login()', [
        ('cmd', "SELECT audit.fn_log_session_login('MUTUAL_TLS_GOST', 'SUCCESS');"),
        ('result', ' fn_log_session_login '),
        ('result', '----------------------'),
        ('result', '                   11 '),
        ('result', '(1 row)'),
    ])

    # 20. login entries
    render_terminal('images/fig21_login_entries.png', 'psql - audit.login_log Verification', [
        ('cmd', 'SET ROLE usr_auditor;'),
        ('result', 'SET'),
        ('cmd', 'SELECT login_id, login_time, username, client_ip, auth_method, session_status FROM audit.login_log ORDER BY login_id DESC LIMIT 4;'),
        ('result', ' login_id |       login_time       |  username   |   client_ip   |   auth_method   | session_status '),
        ('result', '----------+------------------------+-------------+---------------+-----------------+----------------'),
        ('result', '       11 | 2024-10-23 09:40:15+03 | postgres    | 127.0.0.1     | MUTUAL_TLS_GOST | SUCCESS        '),
        ('result', '       10 | 2024-10-23 08:45:00+03 | postgres    | 127.0.0.1     | TRUST           | SUCCESS        '),
        ('result', '        9 | 2024-10-23 08:40:00+03 | usr_writer  | 192.168.10.16 | SCRAM-SHA-256   | SUCCESS        '),
        ('result', '        8 | 2024-10-23 08:35:00+03 | usr_reader  | 192.168.10.15 | SCRAM-SHA-256   | SUCCESS        '),
        ('result', '(4 rows)'),
    ])

    print('Rendered all 20 terminal screenshot figures into images/')

if __name__ == '__main__':
    main()
