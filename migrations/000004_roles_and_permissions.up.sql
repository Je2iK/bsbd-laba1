-- ============================================================================
-- Миграция 000004: Роли, разделение обязанностей (SoD) и привилегии
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. СОЗДАНИЕ ГРУППОВЫХ РОЛЕЙ
-- ----------------------------------------------------------------------------

DO $$
BEGIN
    -- Прикладные роли
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_owner') THEN
        CREATE ROLE app_owner NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_reader') THEN
        CREATE ROLE app_reader NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_writer') THEN
        CREATE ROLE app_writer NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'auditor') THEN
        CREATE ROLE auditor NOLOGIN;
    END IF;

    -- Роли разделения обязанностей (Separation of Duties - SoD)
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ddl_admin') THEN
        CREATE ROLE ddl_admin NOLOGIN NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'dml_admin') THEN
        CREATE ROLE dml_admin NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'security_admin') THEN
        CREATE ROLE security_admin NOLOGIN NOINHERIT;
    END IF;
END
$$;

-- Назначение владельца схем
ALTER SCHEMA app OWNER TO app_owner;
ALTER SCHEMA ref OWNER TO app_owner;
ALTER SCHEMA stg OWNER TO app_owner;

-- Передача владения таблицами прикладной схемы роли app_owner
ALTER TABLE ref.trust_levels OWNER TO app_owner;
ALTER TABLE ref.document_types OWNER TO app_owner;
ALTER TABLE ref.biometric_modalities OWNER TO app_owner;
ALTER TABLE ref.agencies OWNER TO app_owner;

ALTER TABLE app.citizens OWNER TO app_owner;
ALTER TABLE app.digital_profiles OWNER TO app_owner;
ALTER TABLE app.electronic_passports OWNER TO app_owner;
ALTER TABLE app.biometric_templates OWNER TO app_owner;
ALTER TABLE app.access_consents OWNER TO app_owner;
ALTER TABLE app.access_tokens OWNER TO app_owner;

ALTER TABLE stg.passport_batch_import OWNER TO app_owner;


-- ----------------------------------------------------------------------------
-- 2. НАЗНАЧЕНИЕ ПРИВИЛЕГИЙ
-- ----------------------------------------------------------------------------

-- Доступ к схемам
GRANT USAGE ON SCHEMA ref TO app_reader, app_writer, dml_admin;
GRANT USAGE ON SCHEMA app TO app_reader, app_writer, dml_admin;
GRANT USAGE ON SCHEMA stg TO dml_admin;
GRANT USAGE ON SCHEMA audit TO auditor;

-- Роль app_reader: чтение справочников и некритичных прикладных данных
GRANT SELECT ON ALL TABLES IN SCHEMA ref TO app_reader;
GRANT SELECT ON app.citizens TO app_reader;
GRANT SELECT ON app.digital_profiles TO app_reader;
GRANT SELECT ON app.access_consents TO app_reader;
GRANT SELECT ON app.access_tokens TO app_reader;
-- ВНИМАНИЕ: Доступ к app.electronic_passports и app.biometric_templates НЕ предоставляется app_reader!

-- Роль app_writer: наследует права app_reader + INSERT, UPDATE на прикладные таблицы (DELETE запрещен)
GRANT app_reader TO app_writer;
GRANT INSERT, UPDATE ON app.citizens TO app_writer;
GRANT INSERT, UPDATE ON app.digital_profiles TO app_writer;
GRANT INSERT, UPDATE ON app.access_consents TO app_writer;
GRANT INSERT, UPDATE ON app.access_tokens TO app_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO app_writer;

-- Роль auditor: только чтение журналов аудита, ручной INSERT/UPDATE/DELETE запрещен
GRANT SELECT ON audit.login_log TO auditor;
GRANT SELECT ON audit.change_log TO auditor;
GRANT SELECT ON audit.biometric_verifications TO auditor;

-- Роль dml_admin: массовый DML на рабочие и промежуточные таблицы (без доступа к audit)
GRANT SELECT ON ALL TABLES IN SCHEMA ref TO dml_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO dml_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA stg TO dml_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO dml_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA stg TO dml_admin;

-- Разделение обязанностей: ddl_admin и security_admin
-- Они не наследуют права владельца автоматически (NOINHERIT), но имеют право переключаться через SET ROLE app_owner
GRANT app_owner TO ddl_admin;
GRANT app_owner TO security_admin;

-- Разрешение всем аутентифицированным пользователям регистрировать факт входа через функцию
GRANT USAGE ON SCHEMA audit TO PUBLIC;
GRANT EXECUTE ON FUNCTION audit.fn_log_session_login(TEXT, TEXT) TO PUBLIC;


-- ----------------------------------------------------------------------------
-- 3. НАСТРОЙКА DEFAULT PRIVILEGES (Защита по умолчанию)
-- ----------------------------------------------------------------------------

-- Запрет PUBLIC на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA ref REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA app REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA stg REVOKE ALL ON TABLES FROM PUBLIC;

-- Настройка прав для новых объектов, создаваемых app_owner
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA ref
    GRANT SELECT ON TABLES TO app_reader;

ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA app
    GRANT SELECT ON TABLES TO app_reader;

ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA app
    GRANT INSERT, UPDATE ON TABLES TO app_writer;

ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA app
    GRANT USAGE, SELECT ON SEQUENCES TO app_writer;


-- ----------------------------------------------------------------------------
-- 4. ТЕСТОВЫЕ ЛОГИН-ПОЛЬЗОВАТЕЛИ (NOINHERIT)
-- ----------------------------------------------------------------------------

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'usr_reader') THEN
        CREATE ROLE usr_reader WITH LOGIN PASSWORD 'ReaderPass123!' NOINHERIT;
        GRANT app_reader TO usr_reader;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'usr_writer') THEN
        CREATE ROLE usr_writer WITH LOGIN PASSWORD 'WriterPass123!' NOINHERIT;
        GRANT app_writer TO usr_writer;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'usr_auditor') THEN
        CREATE ROLE usr_auditor WITH LOGIN PASSWORD 'AuditorPass123!' NOINHERIT;
        GRANT auditor TO usr_auditor;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'usr_dml') THEN
        CREATE ROLE usr_dml WITH LOGIN PASSWORD 'DmlAdminPass123!' NOINHERIT;
        GRANT dml_admin TO usr_dml;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'usr_ddl') THEN
        CREATE ROLE usr_ddl WITH LOGIN PASSWORD 'DdlAdminPass123!' NOINHERIT;
        GRANT ddl_admin TO usr_ddl;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'usr_sec') THEN
        CREATE ROLE usr_sec WITH LOGIN PASSWORD 'SecAdminPass123!' NOINHERIT;
        GRANT security_admin TO usr_sec;
    END IF;
END
$$;
