-- ============================================================================
-- Откат миграции 000002
-- ============================================================================

DROP TABLE IF EXISTS stg.passport_batch_import CASCADE;
DROP TABLE IF EXISTS audit.biometric_verifications CASCADE;
DROP TABLE IF EXISTS audit.change_log CASCADE;
DROP TABLE IF EXISTS audit.login_log CASCADE;
DROP TABLE IF EXISTS app.access_tokens CASCADE;
DROP TABLE IF EXISTS app.access_consents CASCADE;
DROP TABLE IF EXISTS app.biometric_templates CASCADE;
DROP TABLE IF EXISTS app.electronic_passports CASCADE;
DROP TABLE IF EXISTS app.digital_profiles CASCADE;
DROP TABLE IF EXISTS app.citizens CASCADE;
DROP TABLE IF EXISTS ref.agencies CASCADE;
DROP TABLE IF EXISTS ref.biometric_modalities CASCADE;
DROP TABLE IF EXISTS ref.document_types CASCADE;
DROP TABLE IF EXISTS ref.trust_levels CASCADE;
