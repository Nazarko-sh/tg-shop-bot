from dataclasses import dataclass
from dotenv import dotenv_values


@dataclass(slots=True)
class Config:
    bot_token: str
    admin_id: int
    db_path: str
    support_contact: str
    manual_payment_details: str


def load_config(path: str = ".env") -> Config:
    env = dotenv_values(path)

    bot_token = (env.get("BOT_TOKEN") or "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is missing in .env")

    admin_id_raw = (env.get("ADMIN_ID") or "").strip()
    if not admin_id_raw.isdigit():
        raise RuntimeError("ADMIN_ID must be a number in .env")
    admin_id = int(admin_id_raw)

    db_path = (env.get("DB_PATH") or "shop.db").strip()

    support_contact = (env.get("SUPPORT_CONTACT") or "@support").strip()

    manual_payment_details = (env.get("MANUAL_PAYMENT_DETAILS") or "").strip()
    if not manual_payment_details:
        manual_payment_details = "Bank: 0000 0000 0000 0000\nName: YOUR NAME\nComment: Order #{order_id}"

    # dotenv_values keeps literal \n, convert to real newlines
    manual_payment_details = manual_payment_details.replace("\\n", "\n")

    return Config(
        bot_token=bot_token,
        admin_id=admin_id,
        db_path=db_path,
        support_contact=support_contact,
        manual_payment_details=manual_payment_details,
    )
