-- ============================================================================
-- Миграция 000005: Row Level Security (RLS) с контролем по уровням доверия
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

-- Включение RLS и принудительного применения (FORCE RLS)
ALTER TABLE app.digital_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.digital_profiles FORCE ROW LEVEL SECURITY;

ALTER TABLE app.electronic_passports ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.electronic_passports FORCE ROW LEVEL SECURITY;

ALTER TABLE app.biometric_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.biometric_templates FORCE ROW LEVEL SECURITY;


-- ----------------------------------------------------------------------------
-- 1. ПОЛИТИКИ ДЛЯ ЕДИНОГО ЦИФРОВОГО ПРОФИЛЯ (app.digital_profiles)
-- ----------------------------------------------------------------------------

-- Администраторы и владельцы имеют полный доступ
DROP POLICY IF EXISTS p_admin_profiles ON app.digital_profiles;
CREATE POLICY p_admin_profiles ON app.digital_profiles
    FOR ALL
    TO app_owner, dml_admin
    USING (TRUE)
    WITH CHECK (TRUE);

-- Чтение профиля гражданином (только свой профиль)
DROP POLICY IF EXISTS p_citizen_read_own_profile ON app.digital_profiles;
CREATE POLICY p_citizen_read_own_profile ON app.digital_profiles
    FOR SELECT
    TO PUBLIC
    USING (
        citizen_id = NULLIF(current_setting('app.current_citizen_id', true), '')::bigint
    );

-- Межведомственный доступ: проверка уровня доверия и согласия
DROP POLICY IF EXISTS p_agency_read_profile ON app.digital_profiles;
CREATE POLICY p_agency_read_profile ON app.digital_profiles
    FOR SELECT
    TO app_reader, app_writer
    USING (
        -- Проверка минимально допустимого уровня доверия сессии
        COALESCE(NULLIF(current_setting('app.current_trust_level', true), '')::int, 0) >= trust_level_id
        OR
        -- Либо наличие активного непросроченного согласия от гражданина
        EXISTS (
            SELECT 1 FROM app.access_consents ac
            WHERE ac.profile_id = app.digital_profiles.profile_id
              AND ac.agency_id = NULLIF(current_setting('app.current_agency_id', true), '')::int
              AND ac.is_revoked IS FALSE
              AND ac.valid_until > CURRENT_TIMESTAMP
              AND ac.scope IN ('PROFILE_READ', 'FULL_ACCESS')
        )
    );


-- ----------------------------------------------------------------------------
-- 2. ПОЛИТИКИ ДЛЯ ЭЛЕКТРОННЫХ ПАСПОРТОВ (app.electronic_passports)
-- ----------------------------------------------------------------------------

DROP POLICY IF EXISTS p_admin_passports ON app.electronic_passports;
CREATE POLICY p_admin_passports ON app.electronic_passports
    FOR ALL
    TO app_owner, dml_admin
    USING (TRUE)
    WITH CHECK (TRUE);

-- Гражданин видит статус и данные только своего паспорта
DROP POLICY IF EXISTS p_citizen_read_own_passport ON app.electronic_passports;
CREATE POLICY p_citizen_read_own_passport ON app.electronic_passports
    FOR SELECT
    TO PUBLIC
    USING (
        citizen_id = NULLIF(current_setting('app.current_citizen_id', true), '')::bigint
    );

-- Доступ ведомств к паспортам: только при подтвержденном уровне доверия (>= 3) и согласии
DROP POLICY IF EXISTS p_agency_verify_passports ON app.electronic_passports;
CREATE POLICY p_agency_verify_passports ON app.electronic_passports
    FOR SELECT
    TO app_reader, app_writer
    USING (
        COALESCE(NULLIF(current_setting('app.current_trust_level', true), '')::int, 0) >= 3
        AND EXISTS (
            SELECT 1 FROM app.digital_profiles dp
            JOIN app.access_consents ac ON ac.profile_id = dp.profile_id
            WHERE dp.citizen_id = app.electronic_passports.citizen_id
              AND ac.agency_id = NULLIF(current_setting('app.current_agency_id', true), '')::int
              AND ac.is_revoked IS FALSE
              AND ac.valid_until > CURRENT_TIMESTAMP
              AND ac.scope IN ('DOCS_VERIFY', 'FULL_ACCESS')
        )
    );


-- ----------------------------------------------------------------------------
-- 3. ПОЛИТИКИ ДЛЯ БИОМЕТРИЧЕСКИХ ДАННЫХ (app.biometric_templates)
-- ----------------------------------------------------------------------------

DROP POLICY IF EXISTS p_admin_biometrics ON app.biometric_templates;
CREATE POLICY p_admin_biometrics ON app.biometric_templates
    FOR ALL
    TO app_owner, dml_admin
    USING (TRUE)
    WITH CHECK (TRUE);

-- Гражданин может просматривать статус наличия своих биометрических шаблонов
DROP POLICY IF EXISTS p_citizen_read_own_biometrics ON app.biometric_templates;
CREATE POLICY p_citizen_read_own_biometrics ON app.biometric_templates
    FOR SELECT
    TO PUBLIC
    USING (
        citizen_id = NULLIF(current_setting('app.current_citizen_id', true), '')::bigint
    );

-- Ведомства: доступ к биометрии строго на биометрическом уровне доверия (уровень 4) и при согласии
DROP POLICY IF EXISTS p_agency_match_biometrics ON app.biometric_templates;
CREATE POLICY p_agency_match_biometrics ON app.biometric_templates
    FOR SELECT
    TO app_reader, app_writer
    USING (
        COALESCE(NULLIF(current_setting('app.current_trust_level', true), '')::int, 0) >= 4
        AND EXISTS (
            SELECT 1 FROM app.digital_profiles dp
            JOIN app.access_consents ac ON ac.profile_id = dp.profile_id
            WHERE dp.citizen_id = app.biometric_templates.citizen_id
              AND ac.agency_id = NULLIF(current_setting('app.current_agency_id', true), '')::int
              AND ac.is_revoked IS FALSE
              AND ac.valid_until > CURRENT_TIMESTAMP
              AND ac.scope IN ('BIOMETRIC_MATCH', 'FULL_ACCESS')
        )
    );
