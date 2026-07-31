.PHONY: sync dev test lint worker beat

sync:           ## 安装依赖（uv）
	uv sync

dev:            ## 启动 API（热重载）
	uv run uvicorn pms.main:app --reload

test:           ## 跑测试
	uv run pytest -q

lint:           ## 代码检查
	uv run ruff check . && uv run ruff format --check .

worker:         ## Celery worker（独立进程）
	uv run celery -A pms.worker.celery_app worker -l info -Q escalation,health,notification,default

beat:           ## Celery beat 调度（单实例）
	uv run celery -A pms.worker.celery_app beat -l info
