
# YukiMusic/plugins/admins/autoplay.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from YukiMusic import yuki
from YukiMusic.utils.database import autoplay_off, autoplay_on, is_autoplay
from YukiMusic.utils.decorators.admins import ActualAdminCB, AdminRightsCheckAnyTime
from YukiMusic.utils.formatters import with_autoplay_status
from YukiMusic.utils.inline.play import autoplay_markup
from config import BANNED_USERS


def _autoplay_command_text(mode: bool) -> str:
    status = "ON ✅" if mode else "OFF ❌"
    return (
        "🔁 Autoplay\n\n"
        f"Current status: {status}\n\n"
        "When Autoplay is ON, the bot automatically queues and plays a related track "
        "once the current queue runs out, instead of leaving the voice chat."
    )


@yuki.on_message(filters.command(["autoplay"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheckAnyTime
async def autoplay_command(client, message: Message, _, chat_id):
    mode = await is_autoplay(chat_id)
    markup = InlineKeyboardMarkup([autoplay_markup(chat_id, mode)])
    await message.reply_text(
        _autoplay_command_text(mode),
        reply_markup=markup
    )


@yuki.on_callback_query(
    filters.regex(r"^autoplay (?:on|off) ") & ~BANNED_USERS
)
@ActualAdminCB
async def autoplay_toggle(client, CallbackQuery, _):
    _, action, chat_id = CallbackQuery.data.split()
    chat_id = int(chat_id)
    mode = await is_autoplay(chat_id)

    if action == "on":
        if not mode:
            await autoplay_on(chat_id)
        new_mode = True
        toast = "Autoplay turned ON"
    else:
        if mode:
            await autoplay_off(chat_id)
        new_mode = False
        toast = "Autoplay turned OFF"

    await CallbackQuery.answer(toast, show_alert=False)

    markup = CallbackQuery.message.reply_markup

    if markup:
        rows = []
        autoplay_row_added = False

        for row in markup.inline_keyboard:
            is_autoplay_row = any(
                button.callback_data
                and button.callback_data.startswith("autoplay ")
                for button in row
            )

            if is_autoplay_row:
                # Keep exactly one Autoplay row.
                # Remove any duplicate Autoplay rows.
                if not autoplay_row_added:
                    rows.append(autoplay_markup(chat_id, new_mode))
                    autoplay_row_added = True
                continue

            # Preserve all unrelated buttons.
            rows.append(list(row))

        # Add Autoplay buttons if they were missing.
        if not autoplay_row_added:
            rows.append(autoplay_markup(chat_id, new_mode))

        markup = InlineKeyboardMarkup(rows)

    else:
        markup = InlineKeyboardMarkup(
            [autoplay_markup(chat_id, new_mode)]
        )

    if CallbackQuery.message.photo:
        base_caption = (
            CallbackQuery.message.caption.html
            if CallbackQuery.message.caption
            else ""
        )
        new_caption = await with_autoplay_status(
            base_caption, chat_id
        )

        try:
            await CallbackQuery.message.edit_caption(
                new_caption,
                reply_markup=markup
            )
        except Exception:
            pass
    else:
        try:
            await CallbackQuery.message.edit_text(
                _autoplay_command_text(new_mode),
                reply_markup=markup
            )
        except Exception:
            pass
