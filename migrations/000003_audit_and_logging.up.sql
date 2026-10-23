-- ============================================================================
-- Миграция 000003: Функции аудита изменений и логирования подключений
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ФУНКЦИЯ И ТРИГГЕРЫ АУДИТА ДАННЫХ (DML AUDIT)
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit.fn_log_change()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = audit, app, public
AS $$
DECLARE
    v_old_data JSONB := NULL;
    v_new_data JSONB := NULL;
    v_row_id TEXT := NULL;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        v_new_data := to_jsonb(NEW);
        -- Определение идентификатора строки через JSONB
        IF (v_new_data ? 'citizen_id') THEN v_row_id := v_new_data ->> 'citizen_id';
        ELSIF (v_new_data ? 'profile_id') THEN v_row_id := v_new_data ->> 'profile_id';
        ELSIF (v_new_data ? 'passport_id') THEN v_row_id := v_new_data ->> 'passport_id';
        ELSIF (v_new_data ? 'biometric_id') THEN v_row_id := v_new_data ->> 'biometric_id';
        ELSIF (v_new_data ? 'consent_id') THEN v_row_id := v_new_data ->> 'consent_id';
        END IF;

        INSERT INTO audit.change_log (
            username, table_schema, table_name, operation, row_id, old_data, new_data
        ) VALUES (
            session_user, TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, v_row_id, NULL, v_new_data
        );
        RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        IF (v_new_data ? 'citizen_id') THEN v_row_id := v_new_data ->> 'citizen_id';
        ELSIF (v_new_data ? 'profile_id') THEN v_row_id := v_new_data ->> 'profile_id';
        ELSIF (v_new_data ? 'passport_id') THEN v_row_id := v_new_data ->> 'passport_id';
        ELSIF (v_new_data ? 'biometric_id') THEN v_row_id := v_new_data ->> 'biometric_id';
        ELSIF (v_new_data ? 'consent_id') THEN v_row_id := v_new_data ->> 'consent_id';
        END IF;

        INSERT INTO audit.change_log (
            username, table_schema, table_name, operation, row_id, old_data, new_data
        ) VALUES (
            session_user, TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, v_row_id, v_old_data, v_new_data
        );
        RETURN NEW;

    ELSIF (TG_OP = 'DELETE') THEN
        v_old_data := to_jsonb(OLD);
        IF (v_old_data ? 'citizen_id') THEN v_row_id := v_old_data ->> 'citizen_id';
        ELSIF (v_old_data ? 'profile_id') THEN v_row_id := v_old_data ->> 'profile_id';
        ELSIF (v_old_data ? 'passport_id') THEN v_row_id := v_old_data ->> 'passport_id';
        ELSIF (v_old_data ? 'biometric_id') THEN v_row_id := v_old_data ->> 'biometric_id';
        ELSIF (v_old_data ? 'consent_id') THEN v_row_id := v_old_data ->> 'consent_id';
        END IF;

        INSERT INTO audit.change_log (
            username, table_schema, table_name, operation, row_id, old_data, new_data
        ) VALUES (
            session_user, TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, v_row_id, v_old_data, NULL
        );
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;
COMMENT ON FUNCTION audit.fn_log_change() IS 'Триггерная SECURITY DEFINER функция фиксации DML операций в change_log';

-- Привязка триггеров к критическим таблицам (с безопасным пересозданием)
DROP TRIGGER IF EXISTS trg_audit_citizens ON app.citizens;
CREATE TRIGGER trg_audit_citizens
    AFTER INSERT OR UPDATE OR DELETE ON app.citizens
    FOR EACH ROW EXECUTE FUNCTION audit.fn_log_change();

DROP TRIGGER IF EXISTS trg_audit_digital_profiles ON app.digital_profiles;
CREATE TRIGGER trg_audit_digital_profiles
    AFTER INSERT OR UPDATE OR DELETE ON app.digital_profiles
    FOR EACH ROW EXECUTE FUNCTION audit.fn_log_change();

DROP TRIGGER IF EXISTS trg_audit_electronic_passports ON app.electronic_passports;
CREATE TRIGGER trg_audit_electronic_passports
    AFTER INSERT OR UPDATE OR DELETE ON app.electronic_passports
    FOR EACH ROW EXECUTE FUNCTION audit.fn_log_change();

DROP TRIGGER IF EXISTS trg_audit_biometric_templates ON app.biometric_templates;
CREATE TRIGGER trg_audit_biometric_templates
    AFTER INSERT OR UPDATE OR DELETE ON app.biometric_templates
    FOR EACH ROW EXECUTE FUNCTION audit.fn_log_change();

DROP TRIGGER IF EXISTS trg_audit_access_consents ON app.access_consents;
CREATE TRIGGER trg_audit_access_consents
    AFTER INSERT OR UPDATE OR DELETE ON app.access_consents
    FOR EACH ROW EXECUTE FUNCTION audit.fn_log_change();


-- ----------------------------------------------------------------------------
-- 2. ЛОГИРОВАНИЕ СЕССИЙ И ПОДКЛЮЧЕНИЙ ПОЛЬЗОВАТЕЛЕЙ
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit.fn_log_session_login(
    p_auth_method TEXT DEFAULT 'PASSWORD',
    p_status TEXT DEFAULT 'SUCCESS'
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = audit, public
AS $$
DECLARE
    v_log_id BIGINT;
    v_client_ip INET;
    v_client_port INT;
BEGIN
    v_client_ip := inet_client_addr();
    v_client_port := inet_client_port();

    -- Если вызов локальный через сокет/psql без сетевого IP
    IF v_client_ip IS NULL THEN
        v_client_ip := '127.0.0.1'::inet;
        v_client_port := 0;
    END IF;

    INSERT INTO audit.login_log (
        login_time,
        username,
        client_ip,
        client_port,
        auth_method,
        session_status
    ) VALUES (
        CURRENT_TIMESTAMP,
        session_user,
        v_client_ip,
        v_client_port,
        p_auth_method,
        p_status
    ) RETURNING login_id INTO v_log_id;

    RETURN v_log_id;
END;
$$;
COMMENT ON FUNCTION audit.fn_log_session_login(TEXT, TEXT) IS 'SECURITY DEFINER функция логирования факта подключения пользователя';
