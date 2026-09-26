from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def danger_button(text, callback_data):
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
    )


def primary_button(text, callback_data):
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
    )


def success_button(text, callback_data):
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
    )


def stats_buttons(_, status):
    if status:
        keyboard = [
            [
                success_button(
                    text=_["SA_B_2"],
                    callback_data="bot_stats_sudo",
                ),
                primary_button(
                    text=_["SA_B_3"],
                    callback_data="TopOverall",
                ),
            ],
            [
                danger_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]
    else:
        keyboard = [
            [
                primary_button(
                    text=_["SA_B_1"],
                    callback_data="TopOverall",
                ),
            ],
            [
                danger_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]

    return InlineKeyboardMarkup(keyboard)


def back_stats_buttons(_):
    return InlineKeyboardMarkup(
        [
            [
                primary_button(
                    text=_["BACK_BUTTON"],
                    callback_data="stats_back",
                ),
                danger_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]
    )
