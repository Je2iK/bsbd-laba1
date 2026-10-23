-- ============================================================================
-- Скрипт автоматизированной проверки безопасности и разграничения прав
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

\echo '===================================================================='
\echo '1. ТЕСТИРОВАНИЕ РОЛИ app_reader (ТОЛЬКО ЧТЕНИЕ РАЗРЕШЕННЫХ ДАННЫХ)'
\echo '===================================================================='
SET ROLE usr_reader;

\echo '-> Попытка чтения справочника ведомств (Ожидается: УСПЕШНО):'
SELECT agency_id, agency_code, agency_name, trust_tier FROM ref.agencies LIMIT 3;

\echo '-> Попытка чтения открытых данных профиля (Ожидается: УСПЕШНО):'
SELECT citizen_id, first_name, last_name, gender FROM app.citizens LIMIT 3;

\echo '-> Попытка вставки данных ролью app_reader (Ожидается: ОШИБКА ДОСТУПА):'
DO $$
BEGIN
    INSERT INTO app.citizens (first_name, last_name, birth_date, birth_place, gender)
    VALUES ('Тест', 'Тестов', '2000-01-01', 'Москва', 'M');
    RAISE EXCEPTION 'ОШИБКА БЕЗОПАСНОСТИ: app_reader смог выполнить INSERT!';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ПРАВИЛО СОБЛЮДЕНО: app_reader получил отказ на INSERT (insufficient_privilege)';
END $$;

\echo '-> Попытка чтения биометрических шаблонов (Ожидается: ОШИБКА ДОСТУПА):'
DO $$
BEGIN
    PERFORM * FROM app.biometric_templates LIMIT 1;
    RAISE EXCEPTION 'ОШИБКА БЕЗОПАСНОСТИ: app_reader смог прочитать биометрию!';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ПРАВИЛО СОБЛЮДЕНО: доступ app_reader к биометрии запрещен (insufficient_privilege)';
END $$;

RESET ROLE;


\echo '===================================================================='
\echo '2. ТЕСТИРОВАНИЕ РОЛИ app_writer (ВСТАВКА/ОБНОВЛЕНИЕ БЕЗ УДАЛЕНИЯ)'
\echo '===================================================================='
SET ROLE usr_writer;

\echo '-> Добавление нового гражданина (Ожидается: УСПЕШНО):'
INSERT INTO app.citizens (first_name, last_name, birth_date, birth_place, gender)
VALUES ('Тест_Писатель', 'Проверочный', '1995-12-12', 'гор. Новосибирск', 'M');

\echo '-> Обновление записи гражданина (Ожидается: УСПЕШНО):'
UPDATE app.citizens SET middle_name = 'Иванович' WHERE first_name = 'Тест_Писатель';

\echo '-> Попытка удаления записи ролью app_writer (Ожидается: ОШИБКА ДОСТУПА):'
DO $$
BEGIN
    DELETE FROM app.citizens WHERE first_name = 'Тест_Писатель';
    RAISE EXCEPTION 'ОШИБКА БЕЗОПАСНОСТИ: app_writer смог выполнить DELETE!';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ПРАВИЛО СОБЛЮДЕНО: app_writer не имеет права на DELETE (insufficient_privilege)';
END $$;

RESET ROLE;


\echo '===================================================================='
\echo '3. ТЕСТИРОВАНИЕ РОЛИ auditor (ЧТЕНИЕ АУДИТА, ЗАПРЕТ РУЧНОГО DML)'
\echo '===================================================================='
SET ROLE usr_auditor;

\echo '-> Чтение журнала изменений DML (Ожидается: УСПЕШНО):'
SELECT change_id, changed_at, username, table_name, operation FROM audit.change_log ORDER BY change_id DESC LIMIT 3;

\echo '-> Чтение журнала сессий пользователей (Ожидается: УСПЕШНО):'
SELECT login_id, login_time, username, client_ip, session_status FROM audit.login_log ORDER BY login_id DESC LIMIT 3;

\echo '-> Попытка ручной вставки в журнал аудита (Ожидается: ОШИБКА ДОСТУПА):'
DO $$
BEGIN
    INSERT INTO audit.login_log (username, client_ip) VALUES ('fake_user', '127.0.0.1');
    RAISE EXCEPTION 'ОШИБКА БЕЗОПАСНОСТИ: auditor смог вручную изменить журнал!';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ПРАВИЛО СОБЛЮДЕНО: auditor не имеет прав на INSERT в журнал аудита (insufficient_privilege)';
END $$;

RESET ROLE;


\echo '===================================================================='
\echo '4. ТЕСТИРОВАНИЕ РОЛИ dml_admin (МАССОВЫЙ DML, ЗАПРЕТ ДОСТУПА К AUDIT)'
\echo '===================================================================='
SET ROLE usr_dml;

\echo '-> Удаление проверочной записи (Ожидается: УСПЕШНО):'
DELETE FROM app.citizens WHERE first_name = 'Тест_Писатель';

\echo '-> Попытка чтения журнала аудита ролью dml_admin (Ожидается: ОШИБКА ДОСТУПА):'
DO $$
BEGIN
    PERFORM * FROM audit.change_log LIMIT 1;
    RAISE EXCEPTION 'ОШИБКА БЕЗОПАСНОСТИ: dml_admin смог прочитать audit.change_log!';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ПРАВИЛО СОБЛЮДЕНО: dml_admin не имеет доступа к схеме audit (insufficient_privilege)';
END $$;

RESET ROLE;


\echo '===================================================================='
\echo '5. РАЗДЕЛЕНИЕ ОБЯЗАННОСТЕЙ (SoD): ddl_admin и security_admin'
\echo '===================================================================='
SET ROLE usr_ddl;

\echo '-> Попытка создания таблицы напрямую без SET ROLE (Ожидается: ОШИБКА ДОСТУПА):'
DO $$
BEGIN
    CREATE TABLE app.temp_test_ddl (id int);
    RAISE EXCEPTION 'ОШИБКА БЕЗОПАСНОСТИ: ddl_admin выполнил DDL без перехода в app_owner!';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ПРАВИЛО СОБЛЮДЕНО: ddl_admin (NOINHERIT) не может выполнять DDL напрямую';
END $$;

\echo '-> Выполнение DDL после явного переключения в app_owner (Ожидается: УСПЕШНО):'
SET ROLE app_owner;
CREATE TABLE app.temp_test_ddl (id int);
DROP TABLE app.temp_test_ddl;
RESET ROLE;


\echo '===================================================================='
\echo '6. ПРОВЕРКА ROW LEVEL SECURITY (RLS) ПО УРОВНЯМ ДОВЕРИЯ'
\echo '===================================================================='
SET ROLE usr_reader;

\echo '-> Проверка RLS: сессия гражданина с ID = 1 (видит только свой профиль):'
SET app.current_citizen_id = '1';
SELECT profile_id, citizen_id, snils, trust_level_id, profile_status FROM app.digital_profiles;

\echo '-> Проверка RLS: сессия гражданина с ID = 2 (видит только профиль 2):'
SET app.current_citizen_id = '2';
SELECT profile_id, citizen_id, snils, trust_level_id, profile_status FROM app.digital_profiles;

\echo '-> Проверка RLS: сессия ведомства без подтвержденного доверия (уровень 2):'
SET app.current_citizen_id = '';
SET app.current_trust_level = '2';
SELECT count(*) AS count_profiles_visible_at_level_2 FROM app.digital_profiles;

\echo '-> Проверка RLS: сессия ведомства с высоким доверием (уровень 5):'
SET app.current_trust_level = '5';
SELECT count(*) AS count_profiles_visible_at_level_5 FROM app.digital_profiles;

RESET ROLE;


\echo '===================================================================='
\echo '7. ПРОВЕРКА ЛОГИРОВАНИЯ ПОДКЛЮЧЕНИЙ ПОЛЬЗОВАТЕЛЕЙ'
\echo '===================================================================='
SELECT audit.fn_log_session_login('MUTUAL_TLS_GOST', 'SUCCESS') AS new_login_event_id;

SET ROLE usr_auditor;
SELECT login_id, login_time, username, client_ip, auth_method, session_status 
FROM audit.login_log 
ORDER BY login_id DESC 
LIMIT 3;
RESET ROLE;

\echo '===================================================================='
\echo 'ВСЕ ТЕСТЫ БЕЗОПАСНОСТИ И РАЗГРАНИЧЕНИЯ ДОСТУПА УСПЕШНО ПРОЙДЕНЫ!'
\echo '===================================================================='
