import os

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "rental_housing",
    broker=settings.redis_url,
    backend=settings.redis_url,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
)

from celery.schedules import crontab

celery_app.conf.update(
    broker_connection_retry_on_startup=False,
    broker_connection_timeout=2,
    broker_connection_max_retries=0,
    task_always_eager=os.environ.get("CELERY_TASK_ALWAYS_EAGER", "").lower() == "true",
    task_eager_propagates=os.environ.get("CELERY_TASK_EAGER_PROPAGATES", "").lower() == "true",
    task_routes={
        "app.tasks.embedding_tasks.*": {"queue": "embedding"},
        "app.tasks.import_tasks.*": {"queue": "import"},
    },
    beat_schedule={
        # 支付同步 — 每5分钟同步pending中的支付状态
        "sync-pending-payments": {
            "task": "sync_pending_payments",
            "schedule": crontab(minute="*/5"),
        },
        # 过期支付关闭 — 每10分钟
        "close-expired-payments": {
            "task": "close_expired_payments",
            "schedule": crontab(minute="*/10"),
        },
        # 支付3小时到期提醒 — 每15分钟
        "payment-reminder-3h": {
            "task": "send_payment_reminders",
            "schedule": crontab(minute="*/15"),
        },
        # 合同签署12小时到期提醒 — 每30分钟
        "contract-unsigned-12h": {
            "task": "send_contract_unsigned_reminders",
            "schedule": crontab(minute="*/30"),
        },
        # 管理员每日摘要 — 每天9:00
        "admin-3day-review": {
            "task": "send_admin_3day_review_reminder",
            "schedule": crontab(hour=9, minute=7),
        },
    },
)
