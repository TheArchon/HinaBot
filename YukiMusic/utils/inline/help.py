from typing import Union

from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from YukiMusic import yuki

# Only these six sections are shown in the Help Center.
HELP_PAGES = ["hb1", "hb2", "hb6", "hb11", "hb14", "hb16"]

# Telegram Premium Custom Emoji IDs for button icons.
HELP_BUTTON_EMOJI = {
    "hb1": "5429571366384842791",   # Admin
    "hb2": "5258362837411045098",   # Auth
    "hb6": "5850346984501680054",   # C-Play
    "hb11": "6089165857856952184",  # Play
    "hb14": "4969883048213480204",  # Song
    "hb16": "6030657343744644592",  # Autoplay
}

NAV_EMOJI = {
    "prev": "5960671702059848143",
    "page": "5827954206136340308",
    "next": "6267119710278522544",
    "home": "5413694143601842851",
    "back": "5352759161945867747",
    "close": "4956612582816351459",
}


def _button(text, *, callback_data=None, url=None, style=None, emoji_id=None):
    kwargs = {"text": text}
    if callback_data is not None:
        kwargs["callback_data"] = callback_data
    if url is not None:
        kwargs["url"] = url
    if style is not None:
        kwargs["style"] = style
    if emoji_id is not None:
        kwargs["icon_custom_emoji_id"] = emoji_id
    return InlineKeyboardButton(**kwargs)


def _mark_button(_, START):
    if START:
        return _button(
            _["BACK_BUTTON"],
            callback_data="settings_back_helper",
            style=ButtonStyle.SUCCESS,
            emoji_id=NAV_EMOJI["back"],
        )
    return _button(
        _["CLOSE_BUTTON"],
        callback_data="close",
        style=ButtonStyle.DANGER,
        emoji_id=NAV_EMOJI["close"],
    )


def help_pannel(_, START: Union[bool, int] = None, page: int = 1):
    """Six-category Help Center menu with Premium Custom Emoji button icons."""
    sf = "1" if START else "0"
    rows = []

    for i in range(0, len(HELP_PAGES), 2):
        row = []
        for key in HELP_PAGES[i : i + 2]:
            row.append(
                _button(
                    text=_[f"H_B_{key[2:]}"],
                    callback_data=f"help_callback {key} {sf}",
                    style=ButtonStyle.PRIMARY,
                    emoji_id=HELP_BUTTON_EMOJI[key],
                )
            )
        rows.append(row)

    rows.append([_mark_button(_, START)])
    return InlineKeyboardMarkup(rows)


def help_topic_markup(_, page: int = 1, START: Union[bool, int] = None):
    """Video-style navigation with Premium Custom Emoji icons.

    Page 1: Prev hidden.
    Pages 2-5: Prev + page + Next.
    Page 6: Prev + page; Next hidden.
    Home is always present.
    """
    sf = "1" if START else "0"
    total = len(HELP_PAGES)
    page = max(1, min(page, total))

    navigation_row = []

    if page > 1:
        navigation_row.append(
            _button(
                text=_["PREV_BUTTON"],
                callback_data=f"help_page {page - 1} {sf}",
                style=ButtonStyle.PRIMARY,
                emoji_id=NAV_EMOJI["prev"],
            )
        )

    navigation_row.append(
        _button(
            text=f"{page}/{total}",
            callback_data="help_noop",
            style=ButtonStyle.DANGER,
            emoji_id=NAV_EMOJI["page"],
        )
    )

    if page < total:
        navigation_row.append(
            _button(
                text=_["NEXT_BUTTON"],
                callback_data=f"help_page {page + 1} {sf}",
                style=ButtonStyle.PRIMARY,
                emoji_id=NAV_EMOJI["next"],
            )
        )

    return InlineKeyboardMarkup(
        [
            navigation_row,
            [
                _button(
                    text="Hᴏᴍᴇ",
                    callback_data=f"help_home {sf}",
                    style=ButtonStyle.SUCCESS,
                    emoji_id=NAV_EMOJI["home"],
                )
            ],
        ]
    )


def help_back_markup(_, page: int = 1, START: Union[bool, int] = None):
    return help_topic_markup(_, page, START)


def private_help_panel(_):
    buttons = [
        [
            _button(
                text=_["S_B_4"],
                url=f"https://t.me/{yuki.username}?start=help",
                emoji_id=NAV_EMOJI["home"],
            ),
        ],
    ]
    return buttons


def format_help_topic(text: str) -> str:
    """Format Help Center content like the reference UI.

    - Existing heading markup is kept.
    - Lines beginning with / are rendered as Telegram blockquotes.
    - Other plain text is italicized.
    - Blank lines are preserved.
    """
    lines = text.strip().splitlines()
    output = []

    for raw in lines:
        line = raw.strip()

        if not line:
            output.append("")
            continue

        # Keep existing HTML headings/labels intact.
        if line.startswith("<b>") or line.startswith("<u>"):
            output.append(line)
            continue

        # Commands get the quote treatment.
        if line.startswith("/"):
            output.append(f"<blockquote>{line}</blockquote>")
            continue

        # Other explanatory text gets italic formatting.
        if line.startswith("<"):
            output.append(f"<i>{line}</i>")
        else:
            output.append(f"<i>{line}</i>")

    return "\n".join(output)
