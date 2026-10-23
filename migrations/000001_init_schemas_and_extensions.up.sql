-- ============================================================================
-- Миграция 000001: Инициализация схем, расширений и ограничение PUBLIC
-- Вариант 12: Защита БД систем цифровой идентификации граждан
-- ============================================================================

-- Подключение криптографических функций и серверного аудита
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Создание изолированных схем
CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS stg;

-- Документирование схем
COMMENT ON SCHEMA ref IS 'Справочные классификаторы, типы документов и уровни доверия идентификации';
COMMENT ON SCHEMA app IS 'Прикладные бизнес-данные: цифровой профиль, электронные паспорта, биометрия, согласия';
COMMENT ON SCHEMA audit IS 'Журналы аудита безопасности, событийных триггеров и логирования сессий';
COMMENT ON SCHEMA stg IS 'Временные таблицы пакетной загрузки и буферы очередей';

-- Базовая безопасность: отключение неконтролируемого доступа к схеме public
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
