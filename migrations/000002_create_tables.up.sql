-- ============================================================================
-- Миграция 000002: Создание таблиц, ограничений и индексов
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. СХЕМА REF (Справочники)
-- ----------------------------------------------------------------------------

-- Справочник уровней доверия цифрового профиля
CREATE TABLE IF NOT EXISTS ref.trust_levels (
    trust_level_id INT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    auth_factor_min INT NOT NULL CHECK (auth_factor_min BETWEEN 1 AND 4),
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_trust_code CHECK (code IN ('ANONYMOUS', 'SIMPLIFIED', 'STANDARD', 'CONFIRMED', 'BIOMETRIC'))
);
COMMENT ON TABLE ref.trust_levels IS 'Уровни доверия единого цифрового профиля гражданина';
COMMENT ON COLUMN ref.trust_levels.trust_level_id IS 'Идентификатор уровня доверия';
COMMENT ON COLUMN ref.trust_levels.code IS 'Кодовое системное имя уровня доверия';
COMMENT ON COLUMN ref.trust_levels.name IS 'Наименование уровня доверия';
COMMENT ON COLUMN ref.trust_levels.auth_factor_min IS 'Минимальное требуемое число факторов проверки';
COMMENT ON COLUMN ref.trust_levels.description IS 'Описание разрешенных операций на данном уровне';
COMMENT ON COLUMN ref.trust_levels.is_active IS 'Флаг активности классификатора';

-- Справочник типов удостоверяющих документов
CREATE TABLE IF NOT EXISTS ref.document_types (
    doc_type_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type_code VARCHAR(30) NOT NULL UNIQUE,
    type_name VARCHAR(150) NOT NULL,
    has_rfid_chip BOOLEAN NOT NULL DEFAULT TRUE,
    validity_years INT NOT NULL CHECK (validity_years > 0),
    CONSTRAINT chk_doc_type_code CHECK (type_code IN ('E_PASSPORT', 'DIGITAL_ID_CARD', 'FOREIGN_PASSPORT', 'RESIDENCE_PERMIT'))
);
COMMENT ON TABLE ref.document_types IS 'Классификатор цифровых и электронных документов удостоверения личности';
COMMENT ON COLUMN ref.document_types.doc_type_id IS 'Первичный ключ типа документа';
COMMENT ON COLUMN ref.document_types.type_code IS 'Уникальный код типа документа';
COMMENT ON COLUMN ref.document_types.type_name IS 'Полное наименование документа';
COMMENT ON COLUMN ref.document_types.has_rfid_chip IS 'Признак наличия криптографического RFID-чипа';
COMMENT ON COLUMN ref.document_types.validity_years IS 'Срок действия документа в годах';

-- Справочник биометрических модальностей
CREATE TABLE IF NOT EXISTS ref.biometric_modalities (
    modality_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    iso_standard VARCHAR(100) NOT NULL,
    far_limit NUMERIC(8,6) NOT NULL CHECK (far_limit > 0 AND far_limit < 1),
    frr_limit NUMERIC(8,6) NOT NULL CHECK (frr_limit > 0 AND frr_limit < 1),
    CONSTRAINT chk_modality_code CHECK (code IN ('FACE_2D', 'FACE_3D', 'FINGERPRINT_SLAP', 'FINGERPRINT_ROLL', 'IRIS', 'VOICE'))
);
COMMENT ON TABLE ref.biometric_modalities IS 'Классификатор биометрических параметров согласно стандартам ISO/IEC';
COMMENT ON COLUMN ref.biometric_modalities.modality_id IS 'Идентификатор модальности';
COMMENT ON COLUMN ref.biometric_modalities.code IS 'Кодовое обозначение биометрического признака';
COMMENT ON COLUMN ref.biometric_modalities.name IS 'Наименование биометрической модальности';
COMMENT ON COLUMN ref.biometric_modalities.iso_standard IS 'Стандарт формата шаблона (ГОСТ/ISO)';
COMMENT ON COLUMN ref.biometric_modalities.far_limit IS 'Предел коэффициента ложного пропуска (FAR)';
COMMENT ON COLUMN ref.biometric_modalities.frr_limit IS 'Предел коэффициента ложного отказа (FRR)';

-- Справочник ведомств и организаций-потребителей
CREATE TABLE IF NOT EXISTS ref.agencies (
    agency_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agency_code VARCHAR(50) NOT NULL UNIQUE,
    agency_name VARCHAR(255) NOT NULL,
    inn VARCHAR(12) NOT NULL UNIQUE CHECK (length(inn) IN (10, 12) AND inn ~ '^[0-9]+$'),
    ogrn VARCHAR(15) NOT NULL UNIQUE CHECK (length(ogrn) IN (13, 15) AND ogrn ~ '^[0-9]+$'),
    trust_tier INT NOT NULL CHECK (trust_tier BETWEEN 1 AND 5),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
COMMENT ON TABLE ref.agencies IS 'Реестр государственных и корпоративных потребителей идентификационных сервисов';
COMMENT ON COLUMN ref.agencies.agency_id IS 'Идентификатор ведомства/организации';
COMMENT ON COLUMN ref.agencies.agency_code IS 'Системный код ведомства (например, МВД, ФНС, СФР)';
COMMENT ON COLUMN ref.agencies.agency_name IS 'Полное официальное наименование';
COMMENT ON COLUMN ref.agencies.inn IS 'ИНН организации';
COMMENT ON COLUMN ref.agencies.ogrn IS 'ОГРН организации';
COMMENT ON COLUMN ref.agencies.trust_tier IS 'Уровень доверия организации в контуре взаимодействия (1-5)';
COMMENT ON COLUMN ref.agencies.is_active IS 'Флаг активности подключения ведомства';


-- ----------------------------------------------------------------------------
-- 2. СХЕМА APP (Прикладные бизнес-данные)
-- ----------------------------------------------------------------------------

-- Базовые сведения о гражданах (ПДн)
CREATE TABLE IF NOT EXISTS app.citizens (
    citizen_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL CHECK (length(first_name) >= 1),
    last_name VARCHAR(100) NOT NULL CHECK (length(last_name) >= 1),
    middle_name VARCHAR(100),
    birth_date DATE NOT NULL CHECK (birth_date > '1900-01-01' AND birth_date <= CURRENT_DATE),
    birth_place VARCHAR(255) NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE app.citizens IS 'Реестр граждан (персональные данные)';
COMMENT ON COLUMN app.citizens.citizen_id IS 'Уникальный номер гражданина в системе';
COMMENT ON COLUMN app.citizens.first_name IS 'Имя гражданина';
COMMENT ON COLUMN app.citizens.last_name IS 'Фамилия гражданина';
COMMENT ON COLUMN app.citizens.middle_name IS 'Отчество гражданина (при наличии)';
COMMENT ON COLUMN app.citizens.birth_date IS 'Дата рождения';
COMMENT ON COLUMN app.citizens.birth_place IS 'Место рождения по свидетельству';
COMMENT ON COLUMN app.citizens.gender IS 'Пол (M - мужской, F - женский)';
COMMENT ON COLUMN app.citizens.created_at IS 'Дата и время первичной регистрации записи';

-- Единый цифровой профиль гражданина
CREATE TABLE IF NOT EXISTS app.digital_profiles (
    profile_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    citizen_id BIGINT NOT NULL UNIQUE REFERENCES app.citizens(citizen_id) ON DELETE RESTRICT,
    snils CHAR(11) NOT NULL UNIQUE CHECK (snils ~ '^[0-9]{11}$'),
    inn VARCHAR(12) NOT NULL UNIQUE CHECK (length(inn) = 12 AND inn ~ '^[0-9]+$'),
    trust_level_id INT NOT NULL REFERENCES ref.trust_levels(trust_level_id) ON DELETE RESTRICT,
    profile_status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE' CHECK (profile_status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'BLOCKED', 'REVOKED')),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE app.digital_profiles IS 'Единый цифровой профиль гражданина с фиксацией уровня доверия';
COMMENT ON COLUMN app.digital_profiles.profile_id IS 'Идентификатор цифрового профиля';
COMMENT ON COLUMN app.digital_profiles.citizen_id IS 'Внешний ключ гражданина';
COMMENT ON COLUMN app.digital_profiles.snils IS 'СНИЛС (11 цифр)';
COMMENT ON COLUMN app.digital_profiles.inn IS 'ИНН физического лица (12 цифр)';
COMMENT ON COLUMN app.digital_profiles.trust_level_id IS 'Текущий подтвержденный уровень доверия';
COMMENT ON COLUMN app.digital_profiles.profile_status IS 'Статус учетной записи профиля';
COMMENT ON COLUMN app.digital_profiles.verified_at IS 'Дата подтверждения уровня доверия';
COMMENT ON COLUMN app.digital_profiles.created_at IS 'Дата создания цифрового профиля';

-- Электронные паспорта и смарт-карты (чувствительные данные)
CREATE TABLE IF NOT EXISTS app.electronic_passports (
    passport_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    citizen_id BIGINT NOT NULL REFERENCES app.citizens(citizen_id) ON DELETE RESTRICT,
    doc_type_id INT NOT NULL REFERENCES ref.document_types(doc_type_id) ON DELETE RESTRICT,
    chip_uid VARCHAR(64) NOT NULL UNIQUE CHECK (chip_uid ~ '^[A-Fa-f0-9]+$'),
    series CHAR(4) NOT NULL CHECK (series ~ '^[0-9]{4}$'),
    number CHAR(6) NOT NULL CHECK (number ~ '^[0-9]{6}$'),
    issue_date DATE NOT NULL CHECK (issue_date <= CURRENT_DATE),
    expiry_date DATE NOT NULL CHECK (expiry_date > issue_date),
    issuing_authority_code VARCHAR(10) NOT NULL CHECK (issuing_authority_code ~ '^[0-9]{3}-[0-9]{3}$'),
    encrypted_chip_payload BYTEA NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_passport_series_number UNIQUE(series, number)
);
COMMENT ON TABLE app.electronic_passports IS 'Реестр электронных паспортов с зашифрованными данными крипточипа';
COMMENT ON COLUMN app.electronic_passports.passport_id IS 'Идентификатор паспорта';
COMMENT ON COLUMN app.electronic_passports.citizen_id IS 'Владелец паспорта (гражданин)';
COMMENT ON COLUMN app.electronic_passports.doc_type_id IS 'Тип документа из классификатора';
COMMENT ON COLUMN app.electronic_passports.chip_uid IS 'Аппаратный уникальный идентификатор RFID-чипа';
COMMENT ON COLUMN app.electronic_passports.series IS 'Серия бланка паспорта';
COMMENT ON COLUMN app.electronic_passports.number IS 'Номер бланка паспорта';
COMMENT ON COLUMN app.electronic_passports.issue_date IS 'Дата выдачи';
COMMENT ON COLUMN app.electronic_passports.expiry_date IS 'Срок окончания действия';
COMMENT ON COLUMN app.electronic_passports.issuing_authority_code IS 'Код подразделения органа выдачи';
COMMENT ON COLUMN app.electronic_passports.encrypted_chip_payload IS 'Криптографически зашифрованный образ чипа (pgcrypto)';
COMMENT ON COLUMN app.electronic_passports.is_active IS 'Флаг валидности документа';

-- Биометрические шаблоны (особо чувствительные Restricted-данные)
CREATE TABLE IF NOT EXISTS app.biometric_templates (
    biometric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    citizen_id BIGINT NOT NULL REFERENCES app.citizens(citizen_id) ON DELETE RESTRICT,
    modality_id INT NOT NULL REFERENCES ref.biometric_modalities(modality_id) ON DELETE RESTRICT,
    template_hash CHAR(64) NOT NULL UNIQUE CHECK (template_hash ~ '^[A-Fa-f0-9]{64}$'),
    encrypted_template BYTEA NOT NULL,
    quality_score NUMERIC(5,2) NOT NULL CHECK (quality_score BETWEEN 0.00 AND 100.00),
    capture_device_id VARCHAR(100) NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'VERIFIED' CHECK (status IN ('PENDING', 'VERIFIED', 'DEPRECATED', 'REVOKED')),
    CONSTRAINT uq_citizen_modality UNIQUE(citizen_id, modality_id)
);
COMMENT ON TABLE app.biometric_templates IS 'Единое биометрическое хранилище с шифрованием биовекторов';
COMMENT ON COLUMN app.biometric_templates.biometric_id IS 'Идентификатор биометрической записи';
COMMENT ON COLUMN app.biometric_templates.citizen_id IS 'Гражданин-субъект биометрии';
COMMENT ON COLUMN app.biometric_templates.modality_id IS 'Биометрическая модальность (лицо, отпечаток, радужка)';
COMMENT ON COLUMN app.biometric_templates.template_hash IS 'SHA-256 хеш нормализованного вектора';
COMMENT ON COLUMN app.biometric_templates.encrypted_template IS 'Зашифрованный симметричным шифром вектор биометрии (pgcrypto)';
COMMENT ON COLUMN app.biometric_templates.quality_score IS 'Оценка качества сэмпла (0.00 - 100.00)';
COMMENT ON COLUMN app.biometric_templates.capture_device_id IS 'Идентификатор сертифицированного сканера/камеры';
COMMENT ON COLUMN app.biometric_templates.registered_at IS 'Время регистрации биометрического образца';
COMMENT ON COLUMN app.biometric_templates.status IS 'Статус биометрического шаблона';

-- Согласия гражданина на доступ к цифровому профилю (M:N связь)
CREATE TABLE IF NOT EXISTS app.access_consents (
    consent_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_id BIGINT NOT NULL REFERENCES app.digital_profiles(profile_id) ON DELETE RESTRICT,
    agency_id INT NOT NULL REFERENCES ref.agencies(agency_id) ON DELETE RESTRICT,
    scope VARCHAR(100) NOT NULL CHECK (scope IN ('PROFILE_READ', 'DOCS_VERIFY', 'BIOMETRIC_MATCH', 'FULL_ACCESS')),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMPTZ NOT NULL CHECK (valid_until > granted_at),
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    consent_signature TEXT NOT NULL,
    CONSTRAINT uq_profile_agency_scope UNIQUE(profile_id, agency_id, scope)
);
COMMENT ON TABLE app.access_consents IS 'Юридические согласия гражданина на обработку и передачу данных профиля (M:N)';
COMMENT ON COLUMN app.access_consents.consent_id IS 'Идентификатор согласия';
COMMENT ON COLUMN app.access_consents.profile_id IS 'Цифровой профиль гражданина';
COMMENT ON COLUMN app.access_consents.agency_id IS 'Ведомство или организация-получатель доступа';
COMMENT ON COLUMN app.access_consents.scope IS 'Объем передаваемых полномочий';
COMMENT ON COLUMN app.access_consents.granted_at IS 'Дата и время дачи согласия';
COMMENT ON COLUMN app.access_consents.valid_until IS 'Срок действия согласия';
COMMENT ON COLUMN app.access_consents.is_revoked IS 'Признак отзыва согласия гражданином';
COMMENT ON COLUMN app.access_consents.consent_signature IS 'Электронная цифровая подпись согласия';

-- Токены межведомственного доступа с контролем уровней доверия
CREATE TABLE IF NOT EXISTS app.access_tokens (
    token_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_id BIGINT NOT NULL REFERENCES app.digital_profiles(profile_id) ON DELETE RESTRICT,
    agency_id INT NOT NULL REFERENCES ref.agencies(agency_id) ON DELETE RESTRICT,
    required_trust_level_id INT NOT NULL REFERENCES ref.trust_levels(trust_level_id) ON DELETE RESTRICT,
    token_hash CHAR(64) NOT NULL UNIQUE,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL CHECK (expires_at > issued_at),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'REVOKED'))
);
COMMENT ON TABLE app.access_tokens IS 'Активные токены межведомственного доступа с верификацией уровня доверия';
COMMENT ON COLUMN app.access_tokens.token_id IS 'Идентификатор токена';
COMMENT ON COLUMN app.access_tokens.profile_id IS 'Целевой цифровой профиль';
COMMENT ON COLUMN app.access_tokens.agency_id IS 'Ведомство, запросившее токен';
COMMENT ON COLUMN app.access_tokens.required_trust_level_id IS 'Минимальный требуемый уровень доверия для сессии';
COMMENT ON COLUMN app.access_tokens.token_hash IS 'Криптографический хеш токена';
COMMENT ON COLUMN app.access_tokens.issued_at IS 'Время выдачи токена';
COMMENT ON COLUMN app.access_tokens.expires_at IS 'Время истечения срока действия';
COMMENT ON COLUMN app.access_tokens.status IS 'Статус валидности токена';


-- ----------------------------------------------------------------------------
-- 3. СХЕМА AUDIT (Аудит и безопасность)
-- ----------------------------------------------------------------------------

-- Журнал подключений пользователей
CREATE TABLE IF NOT EXISTS audit.login_log (
    login_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL,
    client_ip INET,
    client_port INT,
    auth_method VARCHAR(50) DEFAULT 'PASSWORD',
    session_status VARCHAR(30) DEFAULT 'SUCCESS' CHECK (session_status IN ('SUCCESS', 'DENIED', 'TERMINATED'))
);
COMMENT ON TABLE audit.login_log IS 'Журнал регистрации сессий и сетевых подключений пользователей БД';
COMMENT ON COLUMN audit.login_log.login_id IS 'Идентификатор записи сессии';
COMMENT ON COLUMN audit.login_log.login_time IS 'Время установки соединения';
COMMENT ON COLUMN audit.login_log.username IS 'Имя пользователя/роли БД';
COMMENT ON COLUMN audit.login_log.client_ip IS 'IP-адрес клиента';
COMMENT ON COLUMN audit.login_log.client_port IS 'Сетевой порт клиента';
COMMENT ON COLUMN audit.login_log.auth_method IS 'Метод аутентификации';
COMMENT ON COLUMN audit.login_log.session_status IS 'Статус сессии';

-- Журнал изменений чувствительных данных
CREATE TABLE IF NOT EXISTS audit.change_log (
    change_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL,
    table_schema TEXT NOT NULL,
    table_name TEXT NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    row_id TEXT,
    old_data JSONB,
    new_data JSONB
);
COMMENT ON TABLE audit.change_log IS 'Аудит изменений данных в прикладных таблицах (DML-аудит)';
COMMENT ON COLUMN audit.change_log.change_id IS 'Идентификатор события аудита';
COMMENT ON COLUMN audit.change_log.changed_at IS 'Время совершения изменения';
COMMENT ON COLUMN audit.change_log.username IS 'Роль, совершившая транзакцию';
COMMENT ON COLUMN audit.change_log.table_schema IS 'Схема измененной таблицы';
COMMENT ON COLUMN audit.change_log.table_name IS 'Имя измененной таблицы';
COMMENT ON COLUMN audit.change_log.operation IS 'Тип операции (INSERT/UPDATE/DELETE)';
COMMENT ON COLUMN audit.change_log.row_id IS 'Идентификатор затронутой строки';
COMMENT ON COLUMN audit.change_log.old_data IS 'JSON образ строки до модификации';
COMMENT ON COLUMN audit.change_log.new_data IS 'JSON образ строки после модификации';

-- Журнал биометрических верификаций
CREATE TABLE IF NOT EXISTS audit.biometric_verifications (
    verification_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    citizen_id BIGINT NOT NULL REFERENCES app.citizens(citizen_id) ON DELETE RESTRICT,
    modality_id INT NOT NULL REFERENCES ref.biometric_modalities(modality_id) ON DELETE RESTRICT,
    agency_id INT NOT NULL REFERENCES ref.agencies(agency_id) ON DELETE RESTRICT,
    similarity_score NUMERIC(5,4) NOT NULL CHECK (similarity_score BETWEEN 0.0 AND 1.0),
    decision VARCHAR(30) NOT NULL CHECK (decision IN ('MATCH', 'NO_MATCH', 'SUSPICIOUS_LIVENESS')),
    client_ip INET
);
COMMENT ON TABLE audit.biometric_verifications IS 'Протокол попыток верификации биометрических данных ведомствами';
COMMENT ON COLUMN audit.biometric_verifications.verification_id IS 'Идентификатор транзакции сверки';
COMMENT ON COLUMN audit.biometric_verifications.verified_at IS 'Время попытки распознавания';
COMMENT ON COLUMN audit.biometric_verifications.citizen_id IS 'Идентификатор проверяемого гражданина';
COMMENT ON COLUMN audit.biometric_verifications.modality_id IS 'Модальность биометрического вектора';
COMMENT ON COLUMN audit.biometric_verifications.agency_id IS 'Инициатор верификации';
COMMENT ON COLUMN audit.biometric_verifications.similarity_score IS 'Вычисленный балл сходства (0.0000 - 1.0000)';
COMMENT ON COLUMN audit.biometric_verifications.decision IS 'Итоговое решение системы идентификации';
COMMENT ON COLUMN audit.biometric_verifications.client_ip IS 'Сетевой адрес инициатора запроса';


-- ----------------------------------------------------------------------------
-- 4. СХЕМА STG (Промежуточные/staging таблицы)
-- ----------------------------------------------------------------------------

-- Пакетная загрузка данных для выдачи электронных паспортов
CREATE TABLE IF NOT EXISTS stg.passport_batch_import (
    import_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_uuid UUID NOT NULL DEFAULT gen_random_uuid(),
    source_system VARCHAR(100) NOT NULL,
    raw_payload JSONB NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSED', 'ERROR')),
    error_message TEXT
);
COMMENT ON TABLE stg.passport_batch_import IS 'Буферная таблица пакетного импорта паспортных данных из ведомств';
COMMENT ON COLUMN stg.passport_batch_import.import_id IS 'Идентификатор импортируемой записи';
COMMENT ON COLUMN stg.passport_batch_import.batch_uuid IS 'UUID пакета загрузки';
COMMENT ON COLUMN stg.passport_batch_import.source_system IS 'Система-источник данных (СМЭВ/МВД)';
COMMENT ON COLUMN stg.passport_batch_import.raw_payload IS 'Сырые JSON данные бланка и чипа';
COMMENT ON COLUMN stg.passport_batch_import.loaded_at IS 'Время загрузки во временный буфер';
COMMENT ON COLUMN stg.passport_batch_import.status IS 'Статус конвейера обработки';
COMMENT ON COLUMN stg.passport_batch_import.error_message IS 'Текст ошибки валидации при сбое';


-- ----------------------------------------------------------------------------
-- 5. ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ И ВНЕШНИХ КЛЮЧЕЙ
-- ----------------------------------------------------------------------------

-- ref
CREATE INDEX IF NOT EXISTS idx_agencies_tier ON ref.agencies(trust_tier);

-- app
CREATE INDEX IF NOT EXISTS idx_citizens_names ON app.citizens(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_citizens_birth ON app.citizens(birth_date);
CREATE INDEX IF NOT EXISTS idx_profiles_citizen ON app.digital_profiles(citizen_id);
CREATE INDEX IF NOT EXISTS idx_profiles_trust ON app.digital_profiles(trust_level_id);
CREATE INDEX IF NOT EXISTS idx_passports_citizen ON app.electronic_passports(citizen_id);
CREATE INDEX IF NOT EXISTS idx_passports_chip ON app.electronic_passports(chip_uid);
CREATE INDEX IF NOT EXISTS idx_passports_status ON app.electronic_passports(is_active);
CREATE INDEX IF NOT EXISTS idx_biometrics_citizen ON app.biometric_templates(citizen_id);
CREATE INDEX IF NOT EXISTS idx_biometrics_modality ON app.biometric_templates(modality_id);
CREATE INDEX IF NOT EXISTS idx_consents_profile ON app.access_consents(profile_id);
CREATE INDEX IF NOT EXISTS idx_consents_agency ON app.access_consents(agency_id);
CREATE INDEX IF NOT EXISTS idx_consents_valid ON app.access_consents(valid_until) WHERE is_revoked IS FALSE;
CREATE INDEX IF NOT EXISTS idx_tokens_profile_agency ON app.access_tokens(profile_id, agency_id);
CREATE INDEX IF NOT EXISTS idx_tokens_expires ON app.access_tokens(expires_at) WHERE status = 'ACTIVE';

-- audit
CREATE INDEX IF NOT EXISTS idx_login_log_time ON audit.login_log(login_time DESC);
CREATE INDEX IF NOT EXISTS idx_login_log_user ON audit.login_log(username);
CREATE INDEX IF NOT EXISTS idx_change_log_time ON audit.change_log(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_log_target ON audit.change_log(table_schema, table_name);
CREATE INDEX IF NOT EXISTS idx_bio_verif_citizen ON audit.biometric_verifications(citizen_id);
CREATE INDEX IF NOT EXISTS idx_bio_verif_time ON audit.biometric_verifications(verified_at DESC);

-- stg
CREATE INDEX IF NOT EXISTS idx_stg_import_status ON stg.passport_batch_import(status) WHERE status = 'PENDING';
