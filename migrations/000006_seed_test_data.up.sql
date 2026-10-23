-- ============================================================================
-- Миграция 000006: Тестовые данные (≥ 10 строк в ключевых таблицах)
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

-- Гарантия достаточной длины полей хешей
ALTER TABLE app.access_tokens ALTER COLUMN token_hash TYPE VARCHAR(128);
ALTER TABLE app.biometric_templates ALTER COLUMN template_hash TYPE VARCHAR(128);

-- 1. Справочник уровней доверия
INSERT INTO ref.trust_levels (trust_level_id, code, name, auth_factor_min, description) VALUES
(1, 'ANONYMOUS',  'Анонимный уровень',            1, 'Доступ только к публичным открытым сведениям без идентификации'),
(2, 'SIMPLIFIED', 'Упрощенная идентификация',     1, 'Саморегистрация по номеру телефона / email'),
(3, 'STANDARD',   'Стандартная идентификация',    2, 'Проверка СНИЛС и паспортных данных по базам МВД/СФР'),
(4, 'CONFIRMED',  'Подтвержденная учетная запись', 2, 'Личная явка в МФЦ или через онлайн-банкинг с сертификатом УКЭП'),
(5, 'BIOMETRIC',  'Биометрическая идентификация', 3, 'Подтверждение через Единую биометрическую систему (ЕБС)')
ON CONFLICT (trust_level_id) DO NOTHING;

-- 2. Справочник типов удостоверяющих документов
INSERT INTO ref.document_types (type_code, type_name, has_rfid_chip, validity_years) VALUES
('E_PASSPORT',       'Паспорт гражданина РФ с электронным носителем', TRUE, 10),
('DIGITAL_ID_CARD',  'Цифровое удостоверение личности (Смарт-карта)',  TRUE, 5),
('FOREIGN_PASSPORT', 'Заграничный биометрический паспорт',             TRUE, 10),
('RESIDENCE_PERMIT', 'Электронный вид на жительство иностранного лица', TRUE, 5)
ON CONFLICT (type_code) DO NOTHING;

-- 3. Справочник биометрических модальностей
INSERT INTO ref.biometric_modalities (code, name, iso_standard, far_limit, frr_limit) VALUES
('FACE_2D',          'Фотоизображение лица 2D',         'ISO/IEC 19794-5', 0.000100, 0.015000),
('FACE_3D',          'Трехмерная модель лица 3D',       'ISO/IEC 19794-5', 0.000010, 0.008000),
('FINGERPRINT_SLAP', 'Четырехпальцевый плоский оттиск', 'ISO/IEC 19794-4', 0.000010, 0.010000),
('FINGERPRINT_ROLL', 'Прокатанный отпечаток пальца',    'ISO/IEC 19794-4', 0.000005, 0.005000),
('IRIS',             'Изображение радужной оболочки',   'ISO/IEC 19794-6', 0.000001, 0.001000),
('VOICE',            'Голосовой биометрический слепок', 'ISO/IEC 19794-13', 0.001000, 0.030000)
ON CONFLICT (code) DO NOTHING;

-- 4. Справочник ведомств (10 строк)
INSERT INTO ref.agencies (agency_code, agency_name, inn, ogrn, trust_tier) VALUES
('MVD',        'Министерство внутренних дел РФ',                       '7704212345', '1037700012345', 5),
('FNS',        'Федеральная налоговая служба РФ',                      '7707329876', '1047707019876', 5),
('DIGITAL',    'Министерство цифрового развития, связи и массовых ком.', '7710349123', '1047714039123', 5),
('SFR',        'Социальный фонд России',                               '7706801234', '1027739011234', 4),
('FSSP',       'Федеральная служба судебных приставов',                '7709505678', '1047796055678', 4),
('ROSREESTR',  'Федеральная служба государственной регистрации',       '7709219812', '1027700489812', 4),
('SBER',       'ПАО Сбербанк',                                         '7707083893', '1027700132195', 4),
('VTB',        'Банк ВТБ (ПАО)',                                       '7702070139', '1027739609391', 4),
('GOSUSLUGI',  'ФГИС Единый портал государственных услуг (ЕПГУ)',       '7705123999', '1037739123999', 5),
('POST_BANK',  'АО Почта Банк',                                        '3232005484', '1023200000123', 3)
ON CONFLICT (agency_code) DO NOTHING;

-- 5. Граждане (12 строк)
INSERT INTO app.citizens (first_name, last_name, middle_name, birth_date, birth_place, gender) VALUES
('Александр', 'Иванов',    'Сергеевич',   '1985-04-12', 'гор. Москва', 'M'),
('Елена',     'Смирнова',  'Владимировна','1990-08-25', 'гор. Новосибирск', 'F'),
('Дмитрий',   'Кузнецов',  'Алексеевич',  '1978-11-03', 'гор. Санкт-Петербург', 'M'),
('Анна',      'Попова',    'Игоревна',    '1995-02-17', 'гор. Екатеринбург', 'F'),
('Максим',    'Васильев',  'Олегович',    '2001-06-30', 'гор. Казань', 'M'),
('Ольга',     'Новикова',  'Викторовна',  '1988-09-14', 'гор. Нижний Новгород', 'F'),
('Сергей',    'Морозов',   'Павлович',    '1972-12-05', 'гор. Самара', 'M'),
('Татьяна',   'Федорова',  'Андреевна',   '1993-03-22', 'гор. Омск', 'F'),
('Иван',      'Соколов',   'Денисович',   '1999-07-19', 'гор. Челябинск', 'M'),
('Мария',     'Михайлова', 'Романовна',   '1982-10-08', 'гор. Уфа', 'F'),
('Павел',     'Чубреич',   'Ярославович', '2003-05-15', 'гор. Новосибирск', 'M'),
('Наталья',   'Кравцова',  'Евгеньевна',  '1996-01-28', 'гор. Красноярск', 'F');

-- 6. Единые цифровые профили (12 строк)
INSERT INTO app.digital_profiles (citizen_id, snils, inn, trust_level_id, profile_status, verified_at) VALUES
(1,  '11223344556', '770112345678', 5, 'ACTIVE', '2023-01-15 10:00:00+03'),
(2,  '22334455667', '540198765432', 5, 'ACTIVE', '2023-02-20 11:30:00+03'),
(3,  '33445566778', '780145612378', 4, 'ACTIVE', '2023-03-10 14:15:00+03'),
(4,  '44556677889', '660167891234', 4, 'ACTIVE', '2023-04-05 09:45:00+03'),
(5,  '55667788990', '160123456789', 3, 'ACTIVE', '2023-05-12 16:20:00+03'),
(6,  '66778899001', '520134567890', 3, 'ACTIVE', '2023-06-18 12:00:00+03'),
(7,  '77889900112', '630189012345', 4, 'ACTIVE', '2023-07-22 15:10:00+03'),
(8,  '88990011223', '550190123456', 2, 'ACTIVE', '2023-08-30 17:00:00+03'),
(9,  '99001122334', '740101234567', 5, 'ACTIVE', '2023-09-14 10:40:00+03'),
(10, '10111213141', '020112345678', 3, 'ACTIVE', '2023-10-01 13:25:00+03'),
(11, '12131415161', '540899887766', 5, 'ACTIVE', '2023-11-11 11:11:00+03'),
(12, '13141516171', '240177665544', 4, 'ACTIVE', '2023-12-05 14:50:00+03');

-- 7. Электронные паспорта с шифрованием pgcrypto (12 строк)
-- Данные чипа зашифрованы симметричным ключом системы 'GovDigitalPassSecretKey2026'
INSERT INTO app.electronic_passports (
    citizen_id, doc_type_id, chip_uid, series, number, issue_date, expiry_date, issuing_authority_code, encrypted_chip_payload, is_active
) VALUES
(1,  1, 'E0040100112233AA', '4515', '102030', '2020-05-10', '2030-05-10', '770-001', pgp_sym_encrypt('CHIP_DATA_CITIZEN_1_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(2,  1, 'E0040100112233BB', '5016', '203040', '2021-06-15', '2031-06-15', '540-002', pgp_sym_encrypt('CHIP_DATA_CITIZEN_2_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(3,  1, 'E0040100112233CC', '4017', '304050', '2019-09-20', '2029-09-20', '780-003', pgp_sym_encrypt('CHIP_DATA_CITIZEN_3_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(4,  2, 'E0040100112233DD', '6518', '405060', '2022-01-12', '2027-01-12', '660-004', pgp_sym_encrypt('CHIP_DATA_CITIZEN_4_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(5,  1, 'E0040100112233EE', '9219', '506070', '2021-08-22', '2031-08-22', '160-005', pgp_sym_encrypt('CHIP_DATA_CITIZEN_5_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(6,  1, 'E0040100112233FF', '2220', '607080', '2020-11-05', '2030-11-05', '520-006', pgp_sym_encrypt('CHIP_DATA_CITIZEN_6_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(7,  1, 'E004010011223311', '3621', '708090', '2018-03-14', '2028-03-14', '630-007', pgp_sym_encrypt('CHIP_DATA_CITIZEN_7_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(8,  2, 'E004010011223322', '5222', '809010', '2023-04-18', '2028-04-18', '550-008', pgp_sym_encrypt('CHIP_DATA_CITIZEN_8_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(9,  1, 'E004010011223333', '7523', '901020', '2022-10-25', '2032-10-25', '740-009', pgp_sym_encrypt('CHIP_DATA_CITIZEN_9_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(10, 1, 'E004010011223344', '8024', '012030', '2021-12-01', '2031-12-01', '020-010', pgp_sym_encrypt('CHIP_DATA_CITIZEN_10_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(11, 1, 'E004010011223355', '5025', '123456', '2023-07-07', '2033-07-07', '540-011', pgp_sym_encrypt('CHIP_DATA_CITIZEN_11_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE),
(12, 1, 'E004010011223366', '0426', '234567', '2022-09-19', '2032-09-19', '240-012', pgp_sym_encrypt('CHIP_DATA_CITIZEN_12_BAC_AA', 'GovDigitalPassSecretKey2026'), TRUE);

-- 8. Биометрические шаблоны с шифрованием pgcrypto (12 строк)
INSERT INTO app.biometric_templates (
    citizen_id, modality_id, template_hash, encrypted_template, quality_score, capture_device_id, status
) VALUES
(1,  1, 'a1b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0001', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_1_FLOAT512', 'BiometricGovVault2026'), 98.50, 'SCANNER_DVISION_PRO_01', 'VERIFIED'),
(1,  3, 'b1b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0002', pgp_sym_encrypt('VEC_FINGER_CITIZEN_1_MINUTIAE', 'BiometricGovVault2026'), 96.00, 'CROSSMATCH_GUARDIAN_01', 'VERIFIED'),
(2,  1, 'c1b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0003', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_2_FLOAT512', 'BiometricGovVault2026'), 99.10, 'SCANNER_DVISION_PRO_02', 'VERIFIED'),
(2,  5, 'd1b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0004', pgp_sym_encrypt('VEC_IRIS_CITIZEN_2_GABOR_2048', 'BiometricGovVault2026'), 99.80, 'IRIS_RECOG_STATION_01', 'VERIFIED'),
(3,  1, 'e1b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0005', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_3_FLOAT512', 'BiometricGovVault2026'), 94.20, 'SCANNER_DVISION_PRO_03', 'VERIFIED'),
(4,  1, 'f1b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0006', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_4_FLOAT512', 'BiometricGovVault2026'), 97.40, 'SCANNER_DVISION_PRO_04', 'VERIFIED'),
(5,  3, '01b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0007', pgp_sym_encrypt('VEC_FINGER_CITIZEN_5_MINUTIAE', 'BiometricGovVault2026'), 91.50, 'CROSSMATCH_GUARDIAN_02', 'VERIFIED'),
(6,  1, '11b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0008', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_6_FLOAT512', 'BiometricGovVault2026'), 93.80, 'SCANNER_DVISION_PRO_05', 'VERIFIED'),
(7,  1, '21b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0009', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_7_FLOAT512', 'BiometricGovVault2026'), 95.90, 'SCANNER_DVISION_PRO_06', 'VERIFIED'),
(9,  1, '31b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0010', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_9_FLOAT512', 'BiometricGovVault2026'), 98.70, 'SCANNER_DVISION_PRO_07', 'VERIFIED'),
(11, 1, '41b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0011', pgp_sym_encrypt('VEC_FACE2D_CITIZEN_11_FLOAT512', 'BiometricGovVault2026'), 99.40, 'SCANNER_DVISION_PRO_08', 'VERIFIED'),
(11, 3, '51b2c3d4e5f60123456789abcdef0123456789abcdef0123456789abcdef0012', pgp_sym_encrypt('VEC_FINGER_CITIZEN_11_MINUTIAE', 'BiometricGovVault2026'), 97.20, 'CROSSMATCH_GUARDIAN_03', 'VERIFIED');

-- 9. Согласия на доступ к цифровому профилю (12 строк, M:N)
INSERT INTO app.access_consents (profile_id, agency_id, scope, granted_at, valid_until, consent_signature) VALUES
(1,  1, 'FULL_ACCESS',      '2024-01-01', '2027-01-01', 'SIG_RSA_SHA256_CITIZEN_1_MVD'),
(1,  7, 'PROFILE_READ',     '2024-02-01', '2026-02-01', 'SIG_RSA_SHA256_CITIZEN_1_SBER'),
(2,  2, 'DOCS_VERIFY',      '2024-01-10', '2026-01-10', 'SIG_RSA_SHA256_CITIZEN_2_FNS'),
(2,  7, 'BIOMETRIC_MATCH',  '2024-03-01', '2025-03-01', 'SIG_RSA_SHA256_CITIZEN_2_SBER'),
(3,  4, 'PROFILE_READ',     '2024-01-15', '2027-01-15', 'SIG_RSA_SHA256_CITIZEN_3_SFR'),
(4,  8, 'DOCS_VERIFY',      '2024-02-20', '2025-02-20', 'SIG_RSA_SHA256_CITIZEN_4_VTB'),
(5,  9, 'FULL_ACCESS',      '2024-01-05', '2029-01-05', 'SIG_RSA_SHA256_CITIZEN_5_EPGU'),
(6,  6, 'PROFILE_READ',     '2024-04-12', '2026-04-12', 'SIG_RSA_SHA256_CITIZEN_6_ROSREESTR'),
(7,  5, 'DOCS_VERIFY',      '2024-05-18', '2025-05-18', 'SIG_RSA_SHA256_CITIZEN_7_FSSP'),
(9,  7, 'BIOMETRIC_MATCH',  '2024-06-01', '2025-06-01', 'SIG_RSA_SHA256_CITIZEN_9_SBER'),
(11, 1, 'FULL_ACCESS',      '2024-01-01', '2028-01-01', 'SIG_RSA_SHA256_CITIZEN_11_MVD'),
(11, 7, 'BIOMETRIC_MATCH',  '2024-01-15', '2026-01-15', 'SIG_RSA_SHA256_CITIZEN_11_SBER');

-- 10. Межведомственные токены доступа (10 строк)
INSERT INTO app.access_tokens (profile_id, agency_id, required_trust_level_id, token_hash, issued_at, expires_at) VALUES
(1,  1, 5, 'a000000000000000000000000000000000000000000000000000000000000001', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '12 hours'),
(1,  7, 3, 'a000000000000000000000000000000000000000000000000000000000000002', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '6 hours'),
(2,  2, 4, 'a000000000000000000000000000000000000000000000000000000000000003', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '24 hours'),
(2,  7, 5, 'a000000000000000000000000000000000000000000000000000000000000004', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '2 hours'),
(3,  4, 3, 'a000000000000000000000000000000000000000000000000000000000000005', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '8 hours'),
(4,  8, 4, 'a000000000000000000000000000000000000000000000000000000000000006', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '4 hours'),
(5,  9, 3, 'a000000000000000000000000000000000000000000000000000000000000007', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '48 hours'),
(9,  7, 5, 'a000000000000000000000000000000000000000000000000000000000000008', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 hour'),
(11, 1, 5, 'a000000000000000000000000000000000000000000000000000000000000009', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '12 hours'),
(11, 7, 5, 'a000000000000000000000000000000000000000000000000000000000000010', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '2 hours')
ON CONFLICT (token_hash) DO NOTHING;

-- 11. Журнал тестовых подключений
INSERT INTO audit.login_log (login_time, username, client_ip, client_port, auth_method, session_status) VALUES
('2024-10-23 08:00:00+03', 'usr_reader',  '192.168.10.15'::inet, 54100, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:05:00+03', 'usr_writer',  '192.168.10.16'::inet, 54102, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:10:00+03', 'usr_auditor', '192.168.10.20'::inet, 54110, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:15:00+03', 'usr_dml',     '192.168.10.30'::inet, 54120, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:20:00+03', 'usr_ddl',     '192.168.10.35'::inet, 54130, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:25:00+03', 'usr_sec',     '192.168.10.40'::inet, 54140, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:30:00+03', 'unknown_bot', '10.0.0.99'::inet,     44321, 'PASSWORD',      'DENIED'),
('2024-10-23 08:35:00+03', 'usr_reader',  '192.168.10.15'::inet, 54155, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:40:00+03', 'usr_writer',  '192.168.10.16'::inet, 54160, 'SCRAM-SHA-256', 'SUCCESS'),
('2024-10-23 08:45:00+03', 'postgres',    '127.0.0.1'::inet,     54000, 'TRUST',          'SUCCESS');

-- 12. Пакетная загрузка в staging (5 строк)
INSERT INTO stg.passport_batch_import (source_system, raw_payload, status) VALUES
('SMEV_MVD_PASSPORT_ISSUE', '{"batch_id": 101, "items_count": 25, "region": "54", "operator": "mvd_op_77"}', 'PROCESSED'),
('SMEV_MVD_PASSPORT_ISSUE', '{"batch_id": 102, "items_count": 40, "region": "77", "operator": "mvd_op_12"}', 'PROCESSED'),
('EBS_BIOMETRIC_REG',       '{"session": "ebs-9910", "quality": 99.2, "vector_format": "iso5"}',              'PROCESSED'),
('SMEV_MVD_PASSPORT_ISSUE', '{"batch_id": 103, "items_count": 10, "error": "CORRUPTED_XML"}',               'ERROR'),
('EPGU_CONSENT_SYNC',       '{"sync_id": 5541, "count": 120, "timestamp": "2024-10-23T08:40:00Z"}',          'PENDING');
