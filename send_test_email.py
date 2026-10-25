"""Send test email to your-email@example.com via notification service."""
import asyncio
import sys
sys.path.insert(0, r"E:\Project\绉熸埧鏅鸿兘浣揬Rental-Housing-Platform-main\backend")

from app.db.session import async_session_maker
from app.models.user import User
from app.models.notification import NotificationType
from app.services.notification_service import NotificationService
from sqlalchemy import select


async def main():
    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.email == "your-email@example.com")
        )

        if not user:
            print("ERROR: No user with email your-email@example.com")
            return

        print(f"User found: {user.username} (ID={user.id}, Email={user.email})")
        print("Creating test notification...")

        svc = NotificationService(session)
        notification = await svc.create_notification(
            user_id=user.id,
            type=NotificationType.system,
            title="[Test] Notification System Test",
            content=(
                f"Hello {user.username}!\n\n"
                f"This is a test email from the rental platform.\n"
                f"Sent at: 2026-08-06\n\n"
                f"If you received this, the email notification channel is working.\n\n"
                f"--- Example notifications you will receive: ---\n"
                f"[Payment] Order #42 created: CNY 6,000.00 (pay within 24h)\n"
                f"[Contract] HRTA-20260806-00000042-V1 ready to sign (7 days)\n"
                f"[Booking] Confirmed! Move-in: 2026-09-01\n"
                f"---\n\n"
                f"All amounts, orders and contracts are subject to the order detail page."
            ),
            channels=["email"],
        )

        print(f"Notification created! ID={notification.id}")
        print(f"Recipient: {user.email}")
        print(f"Channel: email (Celery task dispatched)")
        print()
        print("NOTE: If SMTP is not configured in .env, the email will be SKIPPED silently.")
        print("Configure SMTP_HOST / SMTP_USER / SMTP_PASSWORD in backend/.env to enable sending.")

        await session.commit()

        # Also show what happened on the Celery side
        print()
        print("Check email delivery:")
        print("  - If SMTP configured: email sent to your-email@example.com")
        print("  - If SMTP not configured: silently skipped (check logs)")


if __name__ == "__main__":
    asyncio.run(main())
