.PHONY: help up down down-v restart status logs migrate-up migrate-down migrate-version migrate-drop psql test report docx clean

# Переменные по умолчанию
COMPOSE = docker compose
POSTGRES_CONTAINER = laba1-postgres
DB_USER = postgres
DB_NAME = university_db
TYPST = .\typst.exe
PYTHON = python

help:
	@echo "======================================================================"
	@echo "              КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ ЛАБОРАТОРНОЙ РАБОТОЙ №1           "
	@echo "======================================================================"
	@echo "  make up               - Запустить контейнер PostgreSQL в фоне"
	@echo "  make down             - Остановить все контейнеры"
	@echo "  make down-v           - Остановить контейнеры и очистить volumes"
	@echo "  make restart          - Перезапустить контейнер PostgreSQL"
	@echo "  make status           - Показать статус работы контейнеров"
	@echo "  make logs             - Показать логи контейнера базы данных"
	@echo "----------------------------------------------------------------------"
	@echo "  make migrate-up       - Применить все миграции (golang-migrate)"
	@echo "  make migrate-down     - Откатить последнюю миграцию (шаг 1)"
	@echo "  make migrate-version  - Узнать текущую версию примененных миграций"
	@echo "  make migrate-drop     - Полный сброс схемы базы данных через migrate"
	@echo "----------------------------------------------------------------------"
	@echo "  make psql             - Войти в интерактивную консоль psql (superuser)"
	@echo "  make test             - Запустить проверочные сценарии прав и RLS"
	@echo "  make report           - Скомпилировать отчёт ГОСТ 7.32 в PDF (Typst)"
	@echo "  make docx             - Сгенерировать отчёт ГОСТ 7.32 в формате Word (.docx)"
	@echo "  make clean            - Очистить временные файлы"
	@echo "======================================================================"

up:
	$(COMPOSE) up -d postgres

down:
	$(COMPOSE) down

down-v:
	$(COMPOSE) down -v

restart:
	$(COMPOSE) restart postgres

status:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f postgres

migrate-up:
	$(COMPOSE) run --rm migrate up

migrate-down:
	$(COMPOSE) run --rm migrate down 1

migrate-version:
	$(COMPOSE) run --rm migrate version

migrate-force:
	$(COMPOSE) run --rm migrate force 0

migrate-drop:
	$(COMPOSE) run --rm migrate drop -f

psql:
	$(COMPOSE) exec -it postgres psql -U $(DB_USER) -d $(DB_NAME)

test:
	$(COMPOSE) exec -T postgres psql -U $(DB_USER) -d $(DB_NAME) -f /scripts/verify_all.sql

report:
	$(TYPST) compile report.typ "БСБД_Корецкий_ПС_ЛР1.pdf"
	@echo "Отчет успешно скомпилирован в файл: БСБД_Корецкий_ПС_ЛР1.pdf"

docx:
	$(PYTHON) scripts/build_docx.py
	@powershell -NoProfile -Command "Copy-Item 'БСБД_Корецкий_ПС_ЛР1.docx' 'БСБД_Корецкий_ПС_ЛP1.docx' -Force"
	@echo "Отчет успешно сгенерирован в файл: БСБД_Корецкий_ПС_ЛР1.docx"

clean:
	@powershell -NoProfile -Command "Remove-Item -Force -ErrorAction SilentlyContinue *.log, test*.typ, test*.pdf"
