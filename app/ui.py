import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, Message

logger = logging.getLogger("app.ui")


async def safe_delete(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        return
    except Exception:
        logger.exception("Delete failed chat_id=%s message_id=%s", chat_id, message_id)


async def safe_delete_message(msg: Message) -> None:
    try:
        await msg.delete()
    except (TelegramBadRequest, TelegramForbiddenError):
        return
    except Exception:
        logger.exception("Delete user message failed")


async def send_or_edit(
    bot: Bot,
    db,
    chat_id: int,
    user_id: int,
    text: str,
    keyboard: Optional[InlineKeyboardMarkup] = None,
    disable_web_page_preview: bool = True,
) -> Message:
    """
    One-message UI:
        - tries to edit previously stored UI message_id
        - if can't edit: sends new, deletes old, stores new id
    parse_mode=None globally (safe).
    """
    old_id = await db.get_ui_message_id(user_id)
    if old_id:
        try:
            return await bot.edit_message_text(
                chat_id=chat_id,
                message_id=old_id,
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=disable_web_page_preview,
            )
        except TelegramBadRequest as e:
            msg = str(e).lower()
            # message can't be edited / not found / etc -> fallback to send new
            if "message is not modified" in msg:
                # still OK: we keep old message as UI anchor
                try:
                    # return a "fake" by re-sending no, but to keep type stable we send nothing.
                    # We'll just return the old message by fetching not possible; send minimal.
                    return await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, disable_web_page_preview=disable_web_page_preview)
                except Exception:
                    raise
            else:
                pass
        except Exception:
            pass

    # send new
    new_msg = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        disable_web_page_preview=disable_web_page_preview,
    )
    await db.set_ui_message_id(user_id, new_msg.message_id)

    if old_id:
        await safe_delete(bot, chat_id, old_id)

    return new_msg


async def send_or_edit_photo(
    bot: Bot,
    db,
    chat_id: int,
    user_id: int,
    photo_file_id: str,
    caption: str,
    keyboard: Optional[InlineKeyboardMarkup] = None,
) -> Message:
    """
    If we have photo product screen, easiest stable UX:
        - delete old UI msg if exists (could be text)
        - sendPhoto and store as UI anchor
    """
    old_id = await db.get_ui_message_id(user_id)
    if old_id:
        await safe_delete(bot, chat_id, old_id)

    new_msg = await bot.send_photo(
        chat_id=chat_id,
        photo=photo_file_id,
        caption=caption,
        reply_markup=keyboard,
    )
    await db.set_ui_message_id(user_id, new_msg.message_id)
    return new_msg
