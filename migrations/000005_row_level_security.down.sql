DROP POLICY IF EXISTS p_agency_match_biometrics ON app.biometric_templates;
DROP POLICY IF EXISTS p_citizen_read_own_biometrics ON app.biometric_templates;
DROP POLICY IF EXISTS p_admin_biometrics ON app.biometric_templates;

DROP POLICY IF EXISTS p_agency_verify_passports ON app.electronic_passports;
DROP POLICY IF EXISTS p_citizen_read_own_passport ON app.electronic_passports;
DROP POLICY IF EXISTS p_admin_passports ON app.electronic_passports;

DROP POLICY IF EXISTS p_agency_read_profile ON app.digital_profiles;
DROP POLICY IF EXISTS p_citizen_read_own_profile ON app.digital_profiles;
DROP POLICY IF EXISTS p_admin_profiles ON app.digital_profiles;

ALTER TABLE app.biometric_templates NO FORCE ROW LEVEL SECURITY;
ALTER TABLE app.biometric_templates DISABLE ROW LEVEL SECURITY;

ALTER TABLE app.electronic_passports NO FORCE ROW LEVEL SECURITY;
ALTER TABLE app.electronic_passports DISABLE ROW LEVEL SECURITY;

ALTER TABLE app.digital_profiles NO FORCE ROW LEVEL SECURITY;
ALTER TABLE app.digital_profiles DISABLE ROW LEVEL SECURITY;
