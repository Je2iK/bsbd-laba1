DROP FUNCTION IF EXISTS audit.fn_log_session_login(TEXT, TEXT);

DROP TRIGGER IF EXISTS trg_audit_access_consents ON app.access_consents;
DROP TRIGGER IF EXISTS trg_audit_biometric_templates ON app.biometric_templates;
DROP TRIGGER IF EXISTS trg_audit_electronic_passports ON app.electronic_passports;
DROP TRIGGER IF EXISTS trg_audit_digital_profiles ON app.digital_profiles;
DROP TRIGGER IF EXISTS trg_audit_citizens ON app.citizens;

DROP FUNCTION IF EXISTS audit.fn_log_change();
