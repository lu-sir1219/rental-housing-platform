"""Celery 定时提醒任务 — 支付倒计时、合同签署、管理员每日摘要。

通过 Celery Beat 调度运行：
  - send_payment_reminders: 每15分钟扫描支付3小时内到期的订单
  - send_contract_unsigned_reminders: 每30分钟扫描签约即将截止的合同
  - send_admin_3day_review_reminder: 每天9:00提醒管理员超过3日未确认合同的订单
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# 合同签署期限：7个自然日（来自文档 Section 一）
CONTRACT_SIGN_DEADLINE_DAYS = 7
# 支付有效期：24小时（来自文档 Section 一.2）
PAYMENT_VALIDITY_HOURS = 24


# ── 支付倒计时提醒 ────────────────────────────────────────────────────


@celery_app.task(
    name="send_payment_reminders",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def send_payment_reminders() -> dict:
    """扫描支付有效期3小时内即将到期的订单，发送提醒通知。

    定时调度建议：每15分钟执行一次。
    """

    async def _run() -> dict:
        settings = get_settings()
        engine = create_async_engine(settings.database_url)
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            from app.models.booking import Booking, BookingStatus

            now = datetime.now(timezone.utc)
            window_start = now + timedelta(hours=3)
            # 查询：付款未完成，且在3小时内到期
            stmt = select(Booking).where(
                Booking.status.in_([
                    BookingStatus.payment_pending,
                    BookingStatus.payment_processing,
                ]),
                Booking.payment_expires_at.is_not(None),
                Booking.payment_expires_at <= window_start,
                Booking.payment_expires_at > now,
            )
            result = await session.scalars(stmt)
            bookings = list(result)

            reminded = 0
            for booking in bookings:
                try:
                    from app.services.order_notification_service import OrderNotificationService
                    await OrderNotificationService(session).enqueue(
                        "payment_reminder_3h",
                        booking,
                        discriminator=f"remind-3h:{datetime.now(timezone.utc):%Y%m%d-%H}",
                    )
                    reminded += 1
                except Exception:
                    logger.exception("提醒任务失败 booking=%s", booking.id)

            if reminded:
                await session.commit()
                logger.info("发送了 %s 条支付3小时提醒", reminded)

            await engine.dispose()
            return {"total": len(bookings), "reminded": reminded}

    return asyncio.run(_run())


# ── 合同签署到期提醒 ────────────────────────────────────────────────


@celery_app.task(
    name="send_contract_unsigned_reminders",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def send_contract_unsigned_reminders() -> dict:
    """扫描合同生成后 (7天 - 12小时) 仍未签署的合同，发送签署截止提醒。

    定时调度建议：每30分钟执行一次。
    """

    async def _run() -> dict:
        settings = get_settings()
        engine = create_async_engine(settings.database_url)
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            from app.models.booking import Booking, BookingStatus
            from app.models.contract import Contract

            now = datetime.now(timezone.utc)
            deadline_threshold = now - timedelta(days=CONTRACT_SIGN_DEADLINE_DAYS)
            reminder_window_start = deadline_threshold + timedelta(hours=12)
            # 查询：合同状态为generated，生成时间在 (7天前 ~ 7天前+12小时) 区间内
            stmt = select(Contract).where(
                Contract.status == "generated",
                Contract.generated_at.is_not(None),
                Contract.generated_at <= reminder_window_start,
                Contract.generated_at > deadline_threshold,
            )
            result = await session.scalars(stmt)
            contracts = list(result)

            reminded = 0
            for contract in contracts:
                try:
                    booking = await session.get(Booking, contract.booking_id)
                    if not booking:
                        continue
                    # 跳过已取消/已完成的订单
                    if booking.status in {BookingStatus.cancelled, BookingStatus.completed, BookingStatus.paid}:
                        continue
                    from app.services.order_notification_service import OrderNotificationService
                    await OrderNotificationService(session).enqueue(
                        "contract_unsigned_12h",
                        booking,
                        contract=contract,
                        discriminator=f"remind-12h:{datetime.now(timezone.utc):%Y%m%d-%H}",
                    )
                    reminded += 1
                except Exception:
                    logger.exception("合同提醒任务失败 contract=%s", contract.id)

            if reminded:
                await session.commit()
                logger.info("发送了 %s 条合同签署12小时提醒", reminded)

            await engine.dispose()
            return {"total": len(contracts), "reminded": reminded}

    return asyncio.run(_run())


# ── 管理员每日摘要 ────────────────────────────────────────────────────


@celery_app.task(
    name="send_admin_3day_review_reminder",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def send_admin_3day_review_reminder() -> dict:
    """提醒超级管理员：支付成功超过3日仍未确认合同的订单。

    定时调度建议：每天9:00执行一次。
    """

    async def _run() -> dict:
        settings = get_settings()
        engine = create_async_engine(settings.database_url)
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            from app.models.booking import Booking, BookingStatus
            from app.models.payment import Payment, PaymentStatus
            from app.models.user import User, UserRole
            from app.models.notification import Notification, NotificationType

            three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)

            # 查询支付成功超过3日但合同未确认的订单
            stmt = select(Booking).where(
                Booking.status.in_([
                    BookingStatus.paid,
                    BookingStatus.contract_signed,
                    BookingStatus.contract_ready,
                ]),
                Booking.updated_at <= three_days_ago,
            )
            result = await session.scalars(stmt)
            bookings = list(result)

            if not bookings:
                await engine.dispose()
                return {"total": 0, "admin_notified": 0}

            # 获取所有超级管理员
            admins = list(await session.scalars(
                select(User).where(User.role == UserRole.admin)
            ))

            if not admins:
                await engine.dispose()
                return {"total": len(bookings), "admin_notified": 0}

            # 构建摘要信息
            items_html = ""
            for booking in bookings[:20]:  # 最多展示20条
                items_html += (
                    f'<tr><td style="padding:8px;border-bottom:1px solid #e2e8f0;">'
                    f'订单 #{booking.id}</td>'
                    f'<td style="padding:8px;border-bottom:1px solid #e2e8f0;">'
                    f'{booking.status.value}</td>'
                    f'<td style="padding:8px;border-bottom:1px solid #e2e8f0;">'
                    f'{booking.updated_at.strftime("%Y-%m-%d %H:%M") if booking.updated_at else "-"}</td>'
                    f'</tr>'
                )

            digest_items = (
                f'<table width="100%" cellpadding="0" cellspacing="0" '
                f'style="border-collapse:collapse;margin-bottom:24px;">'
                f'<tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">订单编号</th>'
                f'<th style="padding:8px;text-align:left;">状态</th>'
                f'<th style="padding:8px;text-align:left;">最后更新</th></tr>'
                f'{items_html}</table>'
            )

            notified = 0
            for admin in admins:
                # 去重：同一管理员+日期不重复发
                dedup_key = f"admin-digest:{admin.id}:{datetime.now(timezone.utc):%Y%m%d}"
                existing = await session.scalar(
                    select(Notification).where(
                        Notification.user_id == admin.id,
                        Notification.entity_type == "admin_digest",
                        Notification.entity_id == dedup_key,
                    )
                )
                if existing:
                    continue

                notification = Notification(
                    user_id=admin.id,
                    type=NotificationType.system,
                    title=f"每日待处理摘要（{datetime.now(timezone.utc):%Y-%m-%d}）",
                    content=(
                        f"待复核合同：{len(bookings)} 个订单超过3日未确认。"
                        f"请登录后台处理。"
                    ),
                    entity_type="admin_digest",
                    entity_id=dedup_key,
                )
                session.add(notification)
                notified += 1

                # 发送邮件
                try:
                    from app.tasks.notification_tasks import send_email_notification
                    if admin.email:
                        html = (
                            f'<h2>每日待处理摘要（{datetime.now(timezone.utc):%Y-%m-%d}）</h2>'
                            f'<p>以下 {len(bookings)} 个订单支付成功已超过3日，合同仍未确认：</p>'
                            f'{digest_items}'
                            f'<p><a href="{settings.frontend_url}/admin">前往管理后台</a></p>'
                        )
                        send_email_notification.delay(
                            user_id=admin.id,
                            subject=f"【租房平台】每日待处理摘要 - {datetime.now(timezone.utc):%Y-%m-%d}",
                            html_body=html,
                        )
                except Exception:
                    logger.exception("管理员摘要邮件发送失败 admin=%s", admin.id)

            if notified:
                await session.commit()
                logger.info("发送了 %s 条管理员每日摘要", notified)

            await engine.dispose()
            return {"total": len(bookings), "admin_notified": notified}

    return asyncio.run(_run())
