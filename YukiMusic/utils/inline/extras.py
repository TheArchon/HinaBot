from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import SUPPORT_CHAT, SUPPORT_CHANNEL


def botplaylist_markup(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="Cʜᴀᴛ",
                url=SUPPORT_CHAT,
                style=ButtonStyle.PRIMARY,
                icon_custom_emoji_id="6021618194228187816",
            ),
            InlineKeyboardButton(
                text="Nᴇᴡs",
                url=SUPPORT_CHANNEL,
                style=ButtonStyle.SUCCESS,
                icon_custom_emoji_id="6039381989985882045",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id="6269316311172518259",
            ),
        ],
    ]
    return buttons


def close_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                    icon_custom_emoji_id="6269316311172518259",
                ),
            ]
        ]
    )
    return upl


