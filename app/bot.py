from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


def create_bot(token: str) -> Bot:
    # parse_mode=None globally (we avoid parse errors entirely)
    return Bot(token=token, default=DefaultBotProperties(parse_mode=None))
