import asyncio
import logging
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.detection import DetectionRule
from backend.app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_users():
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(select(User).where(User.email == "admin@soc.local"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@soc.local",
                hashed_password=get_password_hash("Admin123!"),
                full_name="System Admin",
                role="ADMIN",
            )
            db.add(admin)
            logger.info("Created default admin user (admin@soc.local).")
        else:
            logger.info("Admin user already exists.")

        # Check if analyst exists
        result = await db.execute(select(User).where(User.email == "analyst@soc.local"))
        analyst = result.scalar_one_or_none()
        if not analyst:
            analyst = User(
                email="analyst@soc.local",
                hashed_password=get_password_hash("Analyst123!"),
                full_name="Lead Analyst",
                role="ANALYST",
            )
            db.add(analyst)
            logger.info("Created default analyst user (analyst@soc.local).")
        else:
            logger.info("Analyst user already exists.")

        await db.commit()


async def seed_rules():
    async with AsyncSessionLocal() as db:
        # Check if rules exist
        result = await db.execute(select(DetectionRule))
        existing_rules = result.scalars().all()
        if existing_rules:
            logger.info(f"Found {len(existing_rules)} existing rules. Skipping rule seed.")
            return

        rules = [
            DetectionRule(
                rule_code="RUL-001",
                name="Suspicious Internal Port Scan",
                description="Detects rapid sequential port connections from a single internal source.",
                severity="HIGH",
                category="RECON",
                parameters={"threshold": 20, "window_sec": 60},
            ),
            DetectionRule(
                rule_code="RUL-002",
                name="Large Data Exfiltration via HTTPS",
                description="Detects unusual volume of outbound data on port 443.",
                severity="CRITICAL",
                category="EXFIL",
                parameters={"threshold_bytes": 50000000, "window_sec": 300},
            ),
            DetectionRule(
                rule_code="RUL-003",
                name="Multiple Failed Login Attempts",
                description="Detects brute-force authentication attempts against internal services.",
                severity="MEDIUM",
                category="ACCESS",
                parameters={"threshold": 5, "window_sec": 120},
            )
        ]
        
        for rule in rules:
            db.add(rule)
        
        await db.commit()
        logger.info(f"Created {len(rules)} default detection rules.")


async def main():
    logger.info("Starting database seed...")
    await seed_users()
    await seed_rules()
    logger.info("Database seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
