from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_chat_id: int
    db_path: str

def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_chat_id_str = os.getenv("ADMIN_CHAT_ID", "").strip()
    db_path = os.getenv("DB_PATH", "data/shop.db").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is missing in .env")
    if not admin_chat_id_str or not admin_chat_id_str.isdigit():
        raise RuntimeError("ADMIN_CHAT_ID is missing/invalid in .env (must be integer)")

    return Config(
        bot_token=bot_token,
        admin_chat_id=int(admin_chat_id_str),
        db_path=db_path,
    )
