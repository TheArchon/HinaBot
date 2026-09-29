import random

from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton

import config
from YukiMusic import yuki

COLORS = (ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER)


def _random_styles(count, blanks):
    blank_at = set(random.sample(range(count), blanks))
    colored = [i for i in range(count) if i not in blank_at]
    while True:
        picks = {i: random.choice(COLORS) for i in colored}
        if len(colored) < 3 or len(set(picks.values())) > 1:
            break
    return [picks.get(i, ButtonStyle.DEFAULT) for i in range(count)]


def start_panel(_):
    s = _random_styles(2, random.choice((0, 1)))
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                icon_custom_emoji_id="6100125944381444896",
                url=f"https://t.me/{yuki.username}?startgroup=true",
                style=s[0],
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                icon_custom_emoji_id="6021618194228187816",
                url=config.SUPPORT_CHAT,
                style=s[1],
            ),
        ],
    ]
    return buttons


def private_panel(_):
    s = _random_styles(5, random.choice((0, 1, 1, 2, 2)))
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                icon_custom_emoji_id="6100125944381444896",
                url=f"https://t.me/{yuki.username}?startgroup=true",
                style=s[0],
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                icon_custom_emoji_id="5350396951407895212",
                callback_data="settings_back_helper",
                style=s[1],
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_6"],
                icon_custom_emoji_id="6039381989985882045",
                url=config.SUPPORT_CHANNEL,
                style=s[2],
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                icon_custom_emoji_id="4956475826762679249",
                url=config.SUPPORT_CHAT,
                style=s[3],
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                icon_custom_emoji_id="6237864166879663987",
                user_id=config.OWNER_ID,
                style=s[4],
            ),
        ],
    ]
    return buttons
